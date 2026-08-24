from unittest.mock import patch

import pytest
from flowos_core.components.deepseek.deepseek import DEEPSEEK_MODELS, DeepSeekModelComponent
from flowos_core.components.glean.glean_search_api import GleanAPIWrapper
from flowos_core.components.homeassistant.home_assistant_control import HomeAssistantControl
from flowos_core.components.homeassistant.list_home_assistant_states import ListHomeAssistantStates
from flowos_core.components.huggingface.huggingface_inference_api import HuggingFaceInferenceAPIEmbeddingsComponent
from flowos_core.components.litellm.litellm_proxy import LiteLLMProxyComponent
from flowos_core.components.lmstudio.lmstudioembeddings import LMStudioEmbeddingsComponent
from flowos_core.components.lmstudio.lmstudiomodel import LMStudioModelComponent
from flowos_core.components.ollama.ollama import ChatOllamaComponent
from flowos_core.components.ollama.ollama_embeddings import OllamaEmbeddingsComponent
from flowos_core.components.xai.xai import XAI_DEFAULT_MODELS, XAIModelComponent
from flowos_core.utils.ssrf_protection import SSRFProtectionError

BLOCKED_URL = "http://169.254.169.254/latest/meta-data"


@pytest.fixture(autouse=True)
def enable_ssrf_protection(monkeypatch):
    monkeypatch.setenv("FLOWOS_SSRF_PROTECTION_ENABLED", "true")
    monkeypatch.delenv("FLOWOS_SSRF_ALLOWED_HOSTS", raising=False)


@pytest.mark.asyncio
async def test_lmstudio_model_update_blocks_metadata_url_before_httpx():
    component = LMStudioModelComponent()
    build_config = {"base_url": {"load_from_db": False, "value": BLOCKED_URL}, "model_name": {"options": []}}

    with patch("httpx.AsyncClient.get") as mock_get, pytest.raises(ValueError, match="SSRF Protection"):
        await component.update_build_config(build_config, None, "model_name")

    mock_get.assert_not_called()


def test_lmstudio_model_build_blocks_metadata_url_before_openai_client():
    component = LMStudioModelComponent(base_url=BLOCKED_URL, model_name="model", api_key="test")

    with (
        patch("flowos_core.components.lmstudio.lmstudiomodel.ChatOpenAI") as mock_chat_openai,
        pytest.raises(ValueError, match="SSRF Protection"),
    ):
        component.build_model()

    mock_chat_openai.assert_not_called()


def test_lmstudio_embeddings_build_blocks_metadata_url_before_sdk_client():
    component = LMStudioEmbeddingsComponent(base_url=BLOCKED_URL, model="model", api_key="test")

    with (
        patch("flowos_core.components.lmstudio.lmstudioembeddings.NVIDIAEmbeddings", create=True) as mock_embeddings,
        pytest.raises(ValueError, match="SSRF Protection"),
    ):
        component.build_embeddings()

    mock_embeddings.assert_not_called()


def test_home_assistant_list_states_blocks_metadata_url_before_httpx():
    component = ListHomeAssistantStates()

    with patch("httpx.Client.get") as mock_get:
        result = component._list_states("token", BLOCKED_URL)

    assert "SSRF Protection" in result
    mock_get.assert_not_called()


def test_home_assistant_control_blocks_metadata_url_before_httpx():
    component = HomeAssistantControl()

    with patch("httpx.Client.post") as mock_post:
        result = component._control_device("token", BLOCKED_URL, "turn_on", "switch.test")

    assert "SSRF Protection" in result
    mock_post.assert_not_called()


def test_deepseek_model_fetch_blocks_metadata_url_before_httpx():
    component = DeepSeekModelComponent(api_base=BLOCKED_URL, api_key="test")

    with patch("httpx.Client.get") as mock_get:
        models = component.get_models()

    assert models == DEEPSEEK_MODELS
    assert "SSRF Protection" in component.status
    mock_get.assert_not_called()


def test_deepseek_build_blocks_metadata_url_before_openai_client():
    component = DeepSeekModelComponent(api_base=BLOCKED_URL, api_key="test")

    with patch("langchain_openai.ChatOpenAI") as mock_chat_openai, pytest.raises(ValueError, match="SSRF Protection"):
        component.build_model()

    mock_chat_openai.assert_not_called()


def test_xai_model_fetch_blocks_metadata_url_before_httpx():
    component = XAIModelComponent(base_url=BLOCKED_URL, api_key="test")

    with patch("httpx.Client.get") as mock_get:
        models = component.get_models()

    assert models == XAI_DEFAULT_MODELS
    assert "SSRF Protection" in component.status
    mock_get.assert_not_called()


def test_xai_build_blocks_metadata_url_before_openai_client():
    component = XAIModelComponent(base_url=BLOCKED_URL, api_key="test")

    with (
        patch("flowos_core.components.xai.xai.ChatOpenAI") as mock_chat_openai,
        pytest.raises(ValueError, match="SSRF Protection"),
    ):
        component.build_model()

    mock_chat_openai.assert_not_called()


def test_glean_blocks_metadata_url_before_httpx_post():
    wrapper = GleanAPIWrapper(glean_api_url=BLOCKED_URL, glean_access_token="test-access-token")  # noqa: S106

    with patch("httpx.Client.post") as mock_post, pytest.raises(SSRFProtectionError):
        wrapper._search_api_results("query")

    mock_post.assert_not_called()


def test_huggingface_build_blocks_metadata_url_before_sdk_client():
    component = HuggingFaceInferenceAPIEmbeddingsComponent(
        inference_endpoint=BLOCKED_URL,
        model_name="model",
    )

    with (
        patch.object(component, "create_huggingface_embeddings") as mock_create,
        pytest.raises(ValueError, match="SSRF Protection"),
    ):
        component.build_embeddings()

    mock_create.assert_not_called()


def test_ollama_embeddings_build_blocks_metadata_url_before_sdk_client():
    component = OllamaEmbeddingsComponent(base_url=BLOCKED_URL, model_name="model")

    with (
        patch("flowos_core.components.ollama.ollama_embeddings.OllamaEmbeddings") as mock_embeddings,
        pytest.raises(ValueError, match="SSRF Protection"),
    ):
        component.build_embeddings()

    mock_embeddings.assert_not_called()


def test_ollama_build_blocks_metadata_url_before_sdk_client():
    component = ChatOllamaComponent(base_url=BLOCKED_URL, model_name="model", mirostat="Disabled")

    with (
        patch("flowos_core.components.ollama.ollama.ChatOllama") as mock_chat_ollama,
        pytest.raises(ValueError, match="SSRF Protection"),
    ):
        component.build_model()

    mock_chat_ollama.assert_not_called()


def test_litellm_build_blocks_metadata_url_before_httpx_and_openai_client():
    component = LiteLLMProxyComponent(api_base=BLOCKED_URL, api_key="test", model_name="model")

    with (
        patch("httpx.Client.get") as mock_get,
        patch("flowos_core.components.litellm.litellm_proxy.ChatOpenAI") as mock_chat_openai,
        pytest.raises(ValueError, match="SSRF Protection"),
    ):
        component.build_model()

    mock_get.assert_not_called()
    mock_chat_openai.assert_not_called()

import httpx
from pydantic.v1 import SecretStr
from typing_extensions import override

from flowos_core.base.models.model import LCModelComponent
from flowos_core.field_typing import LanguageModel
from flowos_core.field_typing.range_spec import RangeSpec
from flowos_core.inputs.inputs import (
    BoolInput,
    DictInput,
    DropdownInput,
    IntInput,
    SecretStrInput,
    SliderInput,
    StrInput,
)
from flowos_core.utils.ssrf_httpx import ssrf_protected_openai_clients_for_url, ssrf_safe_httpx_get
from flowos_core.utils.ssrf_protection import SSRFProtectionError

SARVAM_API_BASE = "https://api.sarvam.ai/v1"

# Fallback list used before an API key is supplied (and if /models is
# unreachable). Sarvam's chat models are sovereign Indic-first LLMs trained
# with strong coverage of Indian languages.
SARVAM_MODELS = ["sarvam-m"]


class SarvamAIModelComponent(LCModelComponent):
    display_name = "Sarvam AI"
    description = "Generate text using Sarvam AI's Indic-first LLMs (India-sovereign models)."
    icon = "Sparkles"
    documentation = "https://docs.sarvam.ai/"

    inputs = [
        *LCModelComponent.get_base_inputs(),
        IntInput(
            name="max_tokens",
            display_name="Max Tokens",
            advanced=True,
            info="Maximum number of tokens to generate. Set to 0 for unlimited.",
            range_spec=RangeSpec(min=0, max=32000),
        ),
        DictInput(
            name="model_kwargs",
            display_name="Model Kwargs",
            advanced=True,
            info="Additional keyword arguments to pass to the model.",
        ),
        BoolInput(
            name="json_mode",
            display_name="JSON Mode",
            advanced=True,
            info="If True, it will output JSON regardless of passing a schema.",
        ),
        DropdownInput(
            name="model_name",
            display_name="Model Name",
            info="Sarvam AI model to use",
            options=SARVAM_MODELS,
            value=SARVAM_MODELS[0],
            refresh_button=True,
        ),
        StrInput(
            name="api_base",
            display_name="Sarvam API Base",
            advanced=True,
            info=f"Base URL for API requests. Defaults to {SARVAM_API_BASE}",
            value=SARVAM_API_BASE,
        ),
        SecretStrInput(
            name="api_key",
            display_name="Sarvam API Key",
            info="Your Sarvam AI subscription key (https://dashboard.sarvam.ai)",
            advanced=False,
            required=True,
        ),
        SliderInput(
            name="temperature",
            display_name="Temperature",
            info="Controls randomness in responses",
            value=0.7,
            range_spec=RangeSpec(min=0, max=2, step=0.01),
            advanced=True,
        ),
    ]

    def get_models(self) -> list[str]:
        if not self.api_key:
            return SARVAM_MODELS

        url = f"{self.api_base}/models"
        headers = {"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"}

        try:
            response = ssrf_safe_httpx_get(url, headers=headers, timeout=10)
            response.raise_for_status()
            model_list = response.json()
            models = [model["id"] for model in model_list.get("data", [])]
        except SSRFProtectionError as e:
            self.status = f"SSRF Protection: {e}"
            return SARVAM_MODELS
        except httpx.HTTPError as e:
            self.status = f"Error fetching models: {e}"
            return SARVAM_MODELS
        # An empty /models response would otherwise blank the dropdown.
        return models or SARVAM_MODELS

    @override
    def update_build_config(self, build_config: dict, field_value: str, field_name: str | None = None):
        if field_name in {"api_key", "api_base", "model_name"}:
            build_config["model_name"]["options"] = self.get_models()
        return build_config

    def build_model(self) -> LanguageModel:
        # Sarvam exposes an OpenAI-compatible /chat/completions surface, so the
        # OpenAI client works unchanged once base_url is repointed.
        try:
            from langchain_openai import ChatOpenAI
        except ImportError as e:
            msg = "langchain-openai not installed. Please install with `pip install langchain-openai`"
            raise ImportError(msg) from e

        api_key = SecretStr(self.api_key).get_secret_value() if self.api_key else None
        ssrf_client_kwargs = ssrf_protected_openai_clients_for_url(self.api_base)

        output = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature if self.temperature is not None else 0.7,
            max_tokens=self.max_tokens or None,
            model_kwargs=self.model_kwargs or {},
            base_url=self.api_base,
            api_key=api_key,
            streaming=self.stream if hasattr(self, "stream") else False,
            **ssrf_client_kwargs,
        )

        if self.json_mode:
            output = output.bind(response_format={"type": "json_object"})

        return output

    def _get_exception_message(self, e: Exception):
        """Get message from a Sarvam API exception."""
        try:
            from openai import BadRequestError

            if isinstance(e, BadRequestError):
                message = e.body.get("message")
                if message:
                    return message
        except ImportError:
            pass
        return None

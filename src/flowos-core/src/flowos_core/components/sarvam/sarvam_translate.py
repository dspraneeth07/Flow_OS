import httpx

from flowos_core.custom.custom_component.component import Component
from flowos_core.inputs.inputs import DropdownInput, MultilineInput, SecretStrInput
from flowos_core.schema.message import Message
from flowos_core.template.field.base import Output
from flowos_core.utils.ssrf_httpx import ssrf_safe_httpx_post
from flowos_core.utils.ssrf_protection import SSRFProtectionError

SARVAM_TRANSLATE_URL = "https://api.sarvam.ai/translate"

# Sarvam uses BCP-47-style codes with an -IN region. "auto" lets the service
# detect the source script, which is what you want when the text arrives from
# an untrusted chat input.
LANGUAGE_CODES = [
    "auto",
    "en-IN",
    "hi-IN",
    "te-IN",
    "ta-IN",
    "kn-IN",
    "ml-IN",
    "mr-IN",
    "bn-IN",
    "gu-IN",
    "pa-IN",
    "od-IN",
]

# Source may be auto-detected; a target must be concrete.
TARGET_LANGUAGE_CODES = [code for code in LANGUAGE_CODES if code != "auto"]


class SarvamTranslateComponent(Component):
    """Translate text between English and India's major languages via Sarvam AI."""

    display_name = "Sarvam Translate"
    description = "Translate text across Indian languages (Hindi, Telugu, Tamil, Kannada, and more)."
    icon = "Languages"
    documentation = "https://docs.sarvam.ai/api-reference-docs/text/translate"

    inputs = [
        MultilineInput(
            name="input_value",
            display_name="Text",
            info="The text to translate.",
            required=True,
            tool_mode=True,
        ),
        DropdownInput(
            name="source_language",
            display_name="Source Language",
            info="Language of the input text. 'auto' detects it.",
            options=LANGUAGE_CODES,
            value="auto",
        ),
        DropdownInput(
            name="target_language",
            display_name="Target Language",
            info="Language to translate into.",
            options=TARGET_LANGUAGE_CODES,
            value="hi-IN",
        ),
        SecretStrInput(
            name="api_key",
            display_name="Sarvam API Key",
            info="Your Sarvam AI subscription key (https://dashboard.sarvam.ai)",
            required=True,
        ),
    ]

    outputs = [
        Output(display_name="Translated Text", name="translated_text", method="translate"),
    ]

    def translate(self) -> Message:
        text = (self.input_value or "").strip()
        if not text:
            msg = "No text provided to translate."
            raise ValueError(msg)

        payload = {
            "input": text,
            "source_language_code": self.source_language,
            "target_language_code": self.target_language,
        }
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json",
        }

        try:
            response = ssrf_safe_httpx_post(SARVAM_TRANSLATE_URL, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
        except SSRFProtectionError as e:
            msg = f"SSRF protection blocked the request: {e}"
            raise ValueError(msg) from e
        except httpx.HTTPStatusError as e:
            msg = f"Sarvam translate failed ({e.response.status_code}): {e.response.text}"
            raise ValueError(msg) from e
        except httpx.HTTPError as e:
            msg = f"Could not reach the Sarvam translate API: {e}"
            raise ValueError(msg) from e

        translated = response.json().get("translated_text")
        if not translated:
            msg = f"Sarvam translate returned no text. Response: {response.text}"
            raise ValueError(msg)

        self.status = translated
        return Message(text=translated)

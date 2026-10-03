"""Sonnet 5.5 request settings and response handling for local EDSL jobs."""

from edsl.inference_services.services.anthropic_service import AnthropicService
from edsl.language_models.exceptions import LanguageModelBadResponseError
from edsl.language_models.raw_response_handler import RawResponseHandler

from src.utils.models import DEFAULT_MODEL_ID


class SonnetResponseHandler(RawResponseHandler):
    def get_generated_token_string(self, raw_response):
        if raw_response.get("stop_reason") == "refusal":
            raise LanguageModelBadResponseError(
                message="Sonnet refused the request.", response_json=raw_response
            )
        text = "\n\n".join(
            block["text"]
            for block in raw_response.get("content", [])
            if block.get("type") == "text"
        )
        if not text.strip():
            raise LanguageModelBadResponseError(
                message="Sonnet returned no text.", response_json=raw_response
            )
        return text


class SonnetModel(AnthropicService.create_model(DEFAULT_MODEL_ID)):
    # The pinned EDSL adapter omits sampling parameters for Sonnet 5.5.
    # Its generic reader still assumes content[0] is text; replace that reader.
    response_handler = SonnetResponseHandler(
        key_sequence=[],
        usage_sequence=["usage"],
        reasoning_sequence=["content"],
        inference_service="anthropic",
    )


# Remote workers reconstruct generic EDSL models and would lose our reader.
LOCAL_RUN_OPTIONS = {
    "disable_remote_inference": True,
    "disable_remote_cache": True,
    "offload_execution": False,
    "use_api_proxy": False,
    "stop_on_exception": True,
}

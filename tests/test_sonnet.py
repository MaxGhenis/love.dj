"""Offline coverage of the real EDSL and Anthropic SDK request path."""

import asyncio
import copy
import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from anthropic import AsyncAnthropic
from edsl.language_models import LanguageModel
from edsl.language_models.exceptions import LanguageModelBadResponseError
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from src.models import agents
from src.models.sonnet import LOCAL_RUN_OPTIONS, SonnetModel
from src.utils.models import DEFAULT_MODEL_ID, DEFAULT_PROVIDER


@pytest.fixture
def model(monkeypatch):
    # Keep model construction independent of environment credentials/config.
    monkeypatch.setattr(LanguageModel, "_set_key_lookup", lambda *args: {})
    result = agents._build_model(DEFAULT_MODEL_ID, DEFAULT_PROVIDER)
    result._api_token = "offline-test-key"
    return result


def response(content, stop_reason="end_turn"):
    return {
        "id": "msg_offline",
        "type": "message",
        "role": "assistant",
        "model": DEFAULT_MODEL_ID,
        "content": content,
        "stop_reason": stop_reason,
        "stop_sequence": None,
        "usage": {"input_tokens": 10, "output_tokens": 5},
    }


@pytest.mark.parametrize("thinking_first", [False, True])
def test_edsl_request_through_anthropic_sdk(model, thinking_first):
    content = [{"type": "text", "text": "Hello."}]
    if thinking_first:
        content.insert(0, {"type": "thinking", "thinking": "Private reasoning.", "signature": "test"})
    content.append({"type": "text", "text": "How are you?"})
    captured = []

    def handle(request):
        captured.append(json.loads(request.content))
        return httpx.Response(200, json=response(content))

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as http_client:
            async with AsyncAnthropic(api_key="offline-test-key", http_client=http_client) as client:
                with patch(
                    "edsl.inference_services.services.anthropic_service.AsyncAnthropic",
                    return_value=client,
                ):
                    raw = await model.async_execute_model_call("Say hello", "Be brief")
        return model.parse_response(raw, is_free_text=True)

    parsed = asyncio.run(run())
    assert parsed.answer == "Hello.\n\nHow are you?"
    assert parsed.generated_tokens == "Hello.\n\nHow are you?"
    assert len(captured) == 1
    request = captured[0]
    assert request["model"] == DEFAULT_MODEL_ID
    assert request["max_tokens"] == 4096
    assert request["thinking"] == {"type": "adaptive"}
    assert request["output_config"] == {"effort": "low"}
    assert request["messages"][-1]["role"] == "user"
    assert not ({"temperature", "top_p", "top_k", "tool_choice"} & request.keys())


@pytest.mark.parametrize("content,stop_reason,error", [
    ([{"type": "text", "text": "I cannot help."}], "refusal", "refused"),
    ([{"type": "thinking", "thinking": "No answer"}], "max_tokens", "no text"),
    ([], "end_turn", "no text"),
])
def test_refusal_and_empty_output_fail_loudly(model, content, stop_reason, error):
    with pytest.raises(LanguageModelBadResponseError, match=error):
        model.parse_response(response(content, stop_reason), is_free_text=True)


TEXT = st.one_of(st.text(), st.sampled_from(["", " ", "\n", " \t\n"]))
BLOCKS = st.lists(
    st.one_of(
        st.builds(lambda text: {"type": "text", "text": text}, TEXT),
        st.builds(
            lambda text: {"type": "thinking", "thinking": text, "signature": "test"},
            TEXT,
        ),
        st.just({"type": "redacted_thinking", "data": "opaque"}),
    ),
    max_size=5,
)
STOP_REASONS = st.sampled_from(["end_turn", "max_tokens", "stop_sequence", "refusal"])


@settings(deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(content=BLOCKS, stop_reason=STOP_REASONS)
def test_cache_gate_accepts_exactly_what_parses(model, content, stop_reason):
    """The pre-cache check and the parser accept the same responses.

    Invariants, for every response: it is rejected iff it is a refusal or its
    text blocks hold only whitespace; an accepted response passes through
    unchanged and parses to its text blocks joined in order; thinking never
    reaches the answer. A truncated (max_tokens) reply with text is accepted.
    """
    raw = response(content, stop_reason)
    original = copy.deepcopy(raw)
    expected = "\n\n".join(block["text"] for block in content if block["type"] == "text")
    accepted = stop_reason != "refusal" and bool(expected.strip())
    sdk_response = MagicMock()
    sdk_response.model_dump.return_value = raw
    client = MagicMock()
    client.messages.create = AsyncMock(return_value=sdk_response)

    def gate():
        with patch(
            "edsl.inference_services.services.anthropic_service.AsyncAnthropic",
            return_value=client,
        ):
            return asyncio.run(model.async_execute_model_call("Hi", "Be brief"))

    if accepted:
        assert gate() == original
        parsed = model.parse_response(raw, is_free_text=True)
        assert parsed.generated_tokens == expected
        assert parsed.answer == expected.strip()
    else:
        with pytest.raises(LanguageModelBadResponseError) as gate_error:
            gate()
        with pytest.raises(LanguageModelBadResponseError) as parse_error:
            model.parse_response(raw, is_free_text=True)
        message = str(gate_error.value).splitlines()[0]
        assert message == str(parse_error.value).splitlines()[0]
        assert message == (
            "Sonnet refused the request."
            if stop_reason == "refusal"
            else "Sonnet returned no text."
        )
    assert raw == original


def test_rating_ignores_thinking(model):
    parsed = model.parse_response(response([
        {"type": "thinking", "thinking": "Private reasoning"},
        {"type": "text", "text": "8"},
    ]))
    assert parsed.answer == 8


def test_default_without_provider_uses_local_adapter(model):
    assert isinstance(agents._build_model(DEFAULT_MODEL_ID, None), SonnetModel)


def test_other_models_keep_edsl_routing():
    with patch.object(agents, "Model") as factory:
        agents._build_model("other-model", "other-provider")
        factory.assert_called_once_with("other-model", service_name="other-provider")
    assert agents._run_options("other-model", "other-provider") == {}


@pytest.mark.parametrize("helper", ["opener", "response", "rating"])
def test_default_helpers_keep_local_execution_and_propagate_errors(model, helper):
    agent = MagicMock(traits={"persona": "Test persona"})
    job = MagicMock()
    job.by.return_value = job
    job.run.return_value = job
    job.select.return_value = job
    job.first.return_value = "8" if helper == "rating" else "Hello"
    question = "QuestionLinearScale" if helper == "rating" else "QuestionFreeText"
    with patch.object(agents, question, return_value=job):
        if helper == "opener":
            call = lambda: agents.get_opener(DEFAULT_MODEL_ID, agent)
        elif helper == "response":
            call = lambda: agents.get_response(DEFAULT_MODEL_ID, agent, agent, 1, "A", "Hi")
        else:
            call = lambda: agents.get_rating(DEFAULT_MODEL_ID, agent, "Hi")
        call()
        job.run.assert_called_once_with(**LOCAL_RUN_OPTIONS)
        job.run.side_effect = RuntimeError("refused")
        with pytest.raises(RuntimeError, match="refused"):
            call()


@pytest.mark.parametrize("helper", ["opener", "response", "rating"])
@pytest.mark.parametrize("refused", [False, True])
def test_real_edsl_jobs_preserve_response_handling(model, monkeypatch, tmp_path, helper, refused):
    """Exercise real questions, jobs, interviews, and parsing without providers."""
    from edsl.object_store import ObjectStore
    from edsl.runner.models import TaskExecutionError

    monkeypatch.setattr(ObjectStore, "default_root", staticmethod(lambda: tmp_path))
    # Use an in-memory cache and the fixture's dummy credential. These overrides
    # affect test setup only; the application's local execution flags stay intact.
    monkeypatch.setattr(agents, "_build_model", lambda *args: model)
    monkeypatch.setattr(
        agents,
        "_run_options",
        lambda *args: {
            **LOCAL_RUN_OPTIONS,
            "cache": False,
            "check_api_keys": False,
            "skip_retry": True,
            "print_exceptions": False,
            "progress_bar": False,
        },
    )
    agent = agents.create_agent("Test", "A friendly person", "Unused")
    agent.traits["gender"] = "they/them"
    answer = "8" if helper == "rating" else "Hello.\n\nHow are you?"
    raw = response(
        [
            {"type": "thinking", "thinking": "Private reasoning", "signature": "test"},
            {"type": "text", "text": answer},
        ],
        stop_reason="refusal" if refused else "end_turn",
    )
    sdk_response = MagicMock()
    sdk_response.model_dump.return_value = raw
    create = AsyncMock(return_value=sdk_response)
    client = MagicMock()
    client.messages.create = create

    if helper == "opener":
        call = lambda: agents.get_opener(DEFAULT_MODEL_ID, agent)
    elif helper == "response":
        call = lambda: agents.get_response(DEFAULT_MODEL_ID, agent, agent, 1, "A", "Hi")
    else:
        call = lambda: agents.get_rating(DEFAULT_MODEL_ID, agent, "Hi")

    with patch(
        "edsl.inference_services.services.anthropic_service.AsyncAnthropic",
        return_value=client,
    ):
        if refused:
            # EDSL wraps provider/response exceptions at the job boundary.
            with pytest.raises(TaskExecutionError, match="Sonnet refused"):
                call()
        else:
            assert call() == (8 if helper == "rating" else answer)
    create.assert_awaited_once()
    request = create.await_args.kwargs
    assert request["model"] == DEFAULT_MODEL_ID
    assert request["thinking"] == {"type": "adaptive"}
    assert request["output_config"] == {"effort": "low"}
    assert request["max_tokens"] == 4096
    assert not ({"temperature", "top_p", "top_k", "tool_choice"} & request.keys())


@pytest.mark.parametrize("helper", ["opener", "response", "rating"])
@pytest.mark.parametrize(
    "content,stop_reason,error",
    [
        ([{"type": "text", "text": "I cannot help."}], "refusal", "Sonnet refused"),
        (
            [{"type": "thinking", "thinking": "Out of budget", "signature": "test"}],
            "max_tokens",
            "Sonnet returned no text",
        ),
    ],
    ids=["refusal", "thinking-only"],
)
def test_failed_replies_are_not_cached(
    model, monkeypatch, tmp_path, helper, content, stop_reason, error
):
    """A failed reply must not be replayed from EDSL's persistent cache."""
    from edsl.caching.cache_handler import CacheHandler
    from edsl.config import CONFIG
    from edsl.object_store import ObjectStore
    from edsl.runner.models import TaskExecutionError

    monkeypatch.setattr(ObjectStore, "default_root", staticmethod(lambda: tmp_path))
    # Keep the app's run options, including EDSL's default on-disk cache, but
    # point that cache at a scratch file. Only the credential comes from the fixture.
    monkeypatch.setattr(CONFIG, "EDSL_DATABASE_PATH", f"sqlite:///{tmp_path / 'cache.db'}")
    monkeypatch.delattr(CONFIG, "EDSL_SESSION_CACHE", raising=False)
    monkeypatch.setattr(agents, "_build_model", lambda *args: model)
    agent = agents.create_agent("Test", "A friendly person", "Unused")
    agent.traits["gender"] = "they/them"
    answer = "8" if helper == "rating" else "Hello."
    failed, replied = MagicMock(), MagicMock()
    failed.model_dump.return_value = response(content, stop_reason)
    replied.model_dump.return_value = response([{"type": "text", "text": answer}])
    # A third API call would raise StopAsyncIteration and fail the test.
    create = AsyncMock(side_effect=[failed, replied])
    client = MagicMock()
    client.messages.create = create

    if helper == "opener":
        call = lambda: agents.get_opener(DEFAULT_MODEL_ID, agent)
    elif helper == "response":
        call = lambda: agents.get_response(DEFAULT_MODEL_ID, agent, agent, 1, "A", "Hi")
    else:
        call = lambda: agents.get_rating(DEFAULT_MODEL_ID, agent, "Hi")

    def stored_responses():
        # A new handler reopens the SQLite file, as a restarted app would.
        return len(CacheHandler().get_cache())

    with patch(
        "edsl.inference_services.services.anthropic_service.AsyncAnthropic",
        return_value=client,
    ):
        with pytest.raises(TaskExecutionError, match=error):
            call()
        assert create.await_count == 1
        assert stored_responses() == 0

        # The identical request reaches the API instead of replaying the failure.
        assert call() == (8 if helper == "rating" else answer)
        assert create.await_count == 2
        assert stored_responses() == 1

        # Successful replies stay cached.
        assert call() == (8 if helper == "rating" else answer)
        assert create.await_count == 2

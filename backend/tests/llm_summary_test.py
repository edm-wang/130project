# [GenAI Usage] Codex Prompt
# Please add a small first TDD test file for the Team 3 paper summary service. Keep the change
# limited to backend service tests only; cover validation, configuration, provider failure, etc
# [GenAI Usage] Response begins:

import sys
from pathlib import Path

import pytest


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.services import llm_summary  # noqa: E402
from app.services.summary_prompt import PROMPT_VERSION  # noqa: E402


def test_generate_summary_text_requires_title():
    with pytest.raises(llm_summary.MissingPaperContentError) as exc_info:
        llm_summary.generate_summary_text("   ", "This paper has an abstract.")

    assert "title" in str(exc_info.value).lower()


def test_generate_summary_text_requires_abstract():
    with pytest.raises(llm_summary.MissingPaperContentError) as exc_info:
        llm_summary.generate_summary_text("A Paper Title", None)

    assert "abstract" in str(exc_info.value).lower()


def test_normalize_abstract_strips_and_truncates_long_text():
    long_abstract = "  " + ("a" * (llm_summary.MAX_ABSTRACT_CHARS + 25)) + "  "

    normalized = llm_summary.normalize_abstract(long_abstract)

    assert len(normalized) == llm_summary.MAX_ABSTRACT_CHARS
    assert normalized == "a" * llm_summary.MAX_ABSTRACT_CHARS


def test_call_llm_provider_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(llm_summary.SummaryConfigurationError) as exc_info:
        llm_summary.call_llm_provider("Summarize this paper.", "test-model")

    assert "api key" in str(exc_info.value).lower()


def test_call_llm_provider_rejects_empty_response(monkeypatch):
    class FakeResponses:
        def create(self, **_kwargs):
            return type("FakeResponse", (), {"output_text": "   "})()

    class FakeOpenAI:
        def __init__(self, api_key):
            self.api_key = api_key
            self.responses = FakeResponses()

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(llm_summary, "OpenAI", FakeOpenAI)

    with pytest.raises(llm_summary.SummaryProviderError) as exc_info:
        llm_summary.call_llm_provider("Summarize this paper.", "test-model")

    assert "empty summary" in str(exc_info.value).lower()


def test_generate_summary_text_returns_metadata_on_happy_path(monkeypatch):
    def fake_call_llm_provider(prompt, model):
        assert "Trimmed Paper Title" in prompt
        assert "Important abstract content." in prompt
        assert model == "pytest-summary-model"
        return "A concise mocked summary."

    monkeypatch.setenv("LLM_MODEL", "pytest-summary-model")
    monkeypatch.setattr(llm_summary, "call_llm_provider", fake_call_llm_provider)

    generated = llm_summary.generate_summary_text(
        "  Trimmed Paper Title  ",
        "  Important abstract content.  ",
    )

    assert generated.summary_text == "A concise mocked summary."
    assert generated.llm_provider == "openai"
    assert generated.llm_model == "pytest-summary-model"
    assert generated.prompt_version == PROMPT_VERSION


# Don't delete those comments
# [GenAI Usage] Response ends
# [GenAI Usage] Reflection
# I used Codex to generate a first-pass TDD file because these are narrow, deterministic checks around
# service contracts. I avoided real OpenAI and Supabase calls by using pytest monkeypatch (modifying the
# environment variables) and then reviewed the assertions to make sure they represent stable behavior.
# We may change the summary and storage logic later, so nothing specific to the current implementation should be tested.

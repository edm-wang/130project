# [GenAI Usage 1] Codex Prompt
# Please add a small first TDD test file for the Team 3 paper summary service. Keep the change
# limited to backend service tests only; cover validation, configuration, provider failure, etc
# [GenAI Usage 1] Response begins:

import sys
from pathlib import Path

import pytest


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.services import llm_summary  # noqa: E402
from app.services.pdf_sections import PaperSection  # noqa: E402
from app.services.summary_prompt import (  # noqa: E402
    PROMPT_VERSION,
    SECTION_PROMPT_VERSION,
    VIDEO_SLIDE_PLAN_PROMPT_VERSION,
)


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


# [GenAI Usage 1] Response ends
# [GenAI Usage 2] Codex Prompt
# Please extend the existing Team 3 summary service tests for the newer PDF-section summary path.
# Keep this as a small TDD-style characterization slice: do not call OpenAI, mock the provider
# function, and assert that the generated result preserves section-summary metadata, model selection,
# prompt version, and caller-provided custom instructions.
# [GenAI Usage 2] Response begins:
def test_generate_section_summary_text_requires_sections():
    with pytest.raises(llm_summary.MissingPaperContentError) as exc_info:
        llm_summary.generate_section_summary_text("A Paper Title", [])

    assert "sections" in str(exc_info.value).lower()


def test_generate_section_summary_text_returns_section_metadata(monkeypatch):
    sections = [
        PaperSection(
            heading="Introduction",
            text="This section explains the research problem.",
        ),
        PaperSection(
            heading="Results",
            text="This section reports the main benchmark result.",
        ),
    ]

    def fake_call_llm_provider(prompt, model):
        assert "Section Paper" in prompt
        assert "Introduction" in prompt
        assert "main benchmark result" in prompt
        assert "focus on limitations" in prompt
        assert model == "pytest-section-model"
        return "Section-aware summary."

    monkeypatch.setenv("LLM_MODEL", "pytest-section-model")
    monkeypatch.setattr(llm_summary, "call_llm_provider", fake_call_llm_provider)

    generated = llm_summary.generate_section_summary_text(
        " Section Paper ",
        sections,
        custom_instructions="focus on limitations",
    )

    assert generated.summary_text == "Section-aware summary."
    assert generated.llm_provider == "openai"
    assert generated.llm_model == "pytest-section-model"
    assert generated.prompt_version == SECTION_PROMPT_VERSION


# [GenAI Usage 2] Response ends
# [GenAI Usage 3] Codex Prompt
# Please add a focused service-level test slice for the video slide-plan LLM helper. Keep the tests
# deterministic and offline by monkeypatching the LLM provider call. Cover valid JSON, fenced JSON,
# invalid JSON, and unusable slide content so Person 6 has regression coverage for the AI output
# parsing and error handling that would matter in the final demo.
# [GenAI Usage 3] Response begins:
def test_generate_video_slide_plan_parses_json_and_metadata(monkeypatch):
    sections = [PaperSection(heading="Method", text="The method uses retrieval.")]

    def fake_call_llm_provider(prompt, model, instructions):
        assert "Video Paper" in prompt
        assert "retrieval" in prompt
        assert "valid JSON" in instructions
        return """
        {
          "slides": [
            {
              "title": "Problem",
              "bullets": ["Need better retrieval"],
              "narration": "The paper studies retrieval quality.",
              "subtitle": "Retrieval quality",
              "duration_seconds": 8
            }
          ]
        }
        """

    monkeypatch.setenv("LLM_MODEL", "pytest-video-model")
    monkeypatch.setattr(llm_summary, "call_llm_provider", fake_call_llm_provider)

    generated = llm_summary.generate_video_slide_plan(
        title=" Video Paper ",
        sections=sections,
        image_assets=[],
    )

    assert generated.llm_provider == "openai"
    assert generated.llm_model == "pytest-video-model"
    assert generated.prompt_version == VIDEO_SLIDE_PLAN_PROMPT_VERSION
    assert generated.slides[0]["title"] == "Problem"


def test_generate_video_slide_plan_accepts_fenced_json(monkeypatch):
    def fake_call_llm_provider(prompt, model, instructions):
        return """```json
        {
          "slides": [
            {
              "title": "Takeaway",
              "bullets": ["One useful claim"],
              "narration": "This is a usable narration.",
              "subtitle": "Useful claim"
            }
          ]
        }
        ```"""

    monkeypatch.setenv("LLM_MODEL", "pytest-video-model")
    monkeypatch.setattr(llm_summary, "call_llm_provider", fake_call_llm_provider)

    generated = llm_summary.generate_video_slide_plan(
        title="Fenced JSON Paper",
        sections=[PaperSection(heading="Summary", text="Short text.")],
        image_assets=[],
    )

    assert generated.slides[0]["title"] == "Takeaway"


def test_generate_video_slide_plan_rejects_invalid_json(monkeypatch):
    def fake_call_llm_provider(prompt, model, instructions):
        return "not json"

    monkeypatch.setenv("LLM_MODEL", "pytest-video-model")
    monkeypatch.setattr(llm_summary, "call_llm_provider", fake_call_llm_provider)

    with pytest.raises(llm_summary.SummaryProviderError) as exc_info:
        llm_summary.generate_video_slide_plan(
            title="Invalid JSON Paper",
            sections=[PaperSection(heading="Summary", text="Short text.")],
            image_assets=[],
        )

    assert "invalid slide plan" in str(exc_info.value).lower()


def test_generate_video_slide_plan_rejects_unusable_slides(monkeypatch):
    def fake_call_llm_provider(prompt, model, instructions):
        return '{"slides": [{"title": "Missing narration", "bullets": ["ok"]}]}'

    monkeypatch.setenv("LLM_MODEL", "pytest-video-model")
    monkeypatch.setattr(llm_summary, "call_llm_provider", fake_call_llm_provider)

    with pytest.raises(llm_summary.SummaryProviderError) as exc_info:
        llm_summary.generate_video_slide_plan(
            title="Unusable Slide Paper",
            sections=[PaperSection(heading="Summary", text="Short text.")],
            image_assets=[],
        )

    assert "usable slides" in str(exc_info.value).lower()


# Don't delete those comments
# [GenAI Usage 3] Response ends
# [GenAI Usage] Reflection
# I used Codex to generate a first-pass TDD file because these are narrow, deterministic checks around
# service contracts. I avoided real OpenAI and Supabase calls by using pytest monkeypatch (modifying the
# environment variables) and then reviewed the assertions to make sure they represent stable behavior.
# We may change the summary and storage logic later, so nothing specific to the current implementation should be tested.
# For the later section-summary and video-plan additions, I kept the same offline testing strategy:
# the provider boundary is mocked, and the assertions focus on prompt inputs, metadata, parsing, and
# predictable provider-output failure handling.

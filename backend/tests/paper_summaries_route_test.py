# Don't delete comments below
# [GenAI Usage 1] Codex Prompt
# Please add a small second TDD test file for Team 3's paper summary FastAPI routes. Keep the
# tests mocked and offline.
# Focus on route response shapes and LLM error-to-HTTP-status behavior.
# [GenAI Usage 1] Response begins:

import sys
import os
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_PUBLISHABLE_KEY", "test-key")

from app.routers import paper_summaries  # noqa: E402
from app.services.llm_summary import (  # noqa: E402
    GeneratedSummary,
    MissingPaperContentError,
    SummaryConfigurationError,
    SummaryProviderError,
)
from app.services.pdf_sections import (  # noqa: E402
    PaperSection,
    PdfFetchError,
)
from app.services.summary_prompt import (  # noqa: E402
    PROMPT_VERSION,
    SECTION_PROMPT_VERSION,
)
from app.supabase.auth import AuthContext, get_auth_context  # noqa: E402


class FakeUser:
    def __init__(self):
        self.id = str(uuid4())
        self.email = "paper-summary-route-test@example.com"


class FakeQuery:
    def __init__(self, rows, table_name):
        self.rows = rows
        self.table_name = table_name
        self.filters = {}
        self.pending_upsert = None

    def select(self, *_args):
        return self

    def eq(self, field, value):
        self.filters[field] = value
        return self

    def limit(self, *_args):
        return self

    def upsert(self, row, *_args, **_kwargs):
        self.pending_upsert = row
        return self

    def execute(self):
        if self.pending_upsert is not None:
            for index, existing_row in enumerate(self.rows):
                if existing_row.get("paper_id") == self.pending_upsert.get("paper_id"):
                    self.rows[index] = {**existing_row, **self.pending_upsert}
                    return type("FakeResponse", (), {"data": [self.rows[index]]})()

            self.rows.append(dict(self.pending_upsert))
            return type("FakeResponse", (), {"data": [self.rows[-1]]})()

        data = [
            row
            for row in self.rows
            if all(str(row.get(field)) == str(value) for field, value in self.filters.items())
        ]
        return type("FakeResponse", (), {"data": data})()


class FakeSupabaseClient:
    def __init__(self, papers=None, summaries=None):
        self.tables = {
            "papers": papers or [],
            "paper_summaries": summaries or [],
        }

    def table(self, table_name):
        return FakeQuery(self.tables[table_name], table_name)


def make_test_client(fake_client):
    app = FastAPI()
    app.include_router(paper_summaries.summary_router)
    app.dependency_overrides[get_auth_context] = lambda: AuthContext(
        user=FakeUser(),
        access_token="pytest-token",
        client=fake_client,
    )
    return TestClient(app, raise_server_exceptions=False)


def test_get_paper_summary_returns_existing_summary():
    paper_id = str(uuid4())
    client = make_test_client(
        FakeSupabaseClient(
            summaries=[
                {
                    "paper_id": paper_id,
                    "summary_text": "Existing summary.",
                    "llm_provider": "openai",
                    "llm_model": "gpt-4o-mini",
                    "prompt_version": SECTION_PROMPT_VERSION,
                }
            ]
        )
    )

    response = client.get(f"/papers/{paper_id}/summary")

    assert response.status_code == 200
    assert response.json()["summary"]["paper_id"] == paper_id
    assert response.json()["summary"]["summary_text"] == "Existing summary."


def test_get_paper_detail_returns_paper():
    paper_id = str(uuid4())
    client = make_test_client(
        FakeSupabaseClient(
            papers=[
                {
                    "id": paper_id,
                    "title": "Detailed Paper",
                    "abstract": "Paper abstract text.",
                }
            ]
        )
    )

    response = client.get(f"/papers/{paper_id}")

    assert response.status_code == 200
    assert response.json()["paper"]["id"] == paper_id
    assert response.json()["paper"]["title"] == "Detailed Paper"


def test_get_paper_detail_returns_404_when_missing():
    paper_id = str(uuid4())
    client = make_test_client(FakeSupabaseClient())

    response = client.get(f"/papers/{paper_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Paper not found"


def test_get_paper_summary_returns_404_when_summary_is_missing():
    paper_id = str(uuid4())
    client = make_test_client(FakeSupabaseClient())

    response = client.get(f"/papers/{paper_id}/summary")

    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found"


# [GenAI Usage 1] Response ends
def test_generate_paper_summary_reuses_matching_cached_section_summary(monkeypatch):
    paper_id = str(uuid4())
    client = make_test_client(
        FakeSupabaseClient(
            summaries=[
                {
                    "paper_id": paper_id,
                    "summary_text": "Cached section summary.",
                    "llm_provider": "openai",
                    "llm_model": "gpt-4o-mini",
                    "prompt_version": SECTION_PROMPT_VERSION,
                }
            ]
        )
    )

    response = client.post(f"/papers/{paper_id}/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["generated"] is False
    assert body["stored"] is True
    assert body["summary"]["summary_text"] == "Cached section summary."


def test_generate_paper_summary_uses_pdf_sections_by_default(monkeypatch):
    paper_id = str(uuid4())
    client = make_test_client(
        FakeSupabaseClient(
            papers=[
                {
                    "id": paper_id,
                    "title": "Mock Paper",
                    "abstract": "A useful abstract.",
                    "pdf_url": "https://example.com/mock-paper.pdf",
                }
            ]
        )
    )

    def fake_fetch_pdf_bytes(pdf_url):
        assert pdf_url == "https://example.com/mock-paper.pdf"
        return b"%PDF fake"

    def fake_extract_pdf_sections(pdf_bytes):
        assert pdf_bytes == b"%PDF fake"
        return [PaperSection(heading="Introduction", text="Section content.")]

    def fake_generate_section_summary_text(title, sections, custom_instructions=None):
        assert title == "Mock Paper"
        assert sections[0].heading == "Introduction"
        assert custom_instructions is None
        return GeneratedSummary(
            summary_text="Generated section summary.",
            llm_provider="openai",
            llm_model="pytest-model",
            prompt_version=SECTION_PROMPT_VERSION,
        )

    monkeypatch.setattr(paper_summaries, "fetch_pdf_bytes", fake_fetch_pdf_bytes)
    monkeypatch.setattr(paper_summaries, "extract_pdf_sections", fake_extract_pdf_sections)
    monkeypatch.setattr(
        paper_summaries,
        "generate_section_summary_text",
        fake_generate_section_summary_text,
    )

    response = client.post(f"/papers/{paper_id}/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["generated"] is True
    assert body["stored"] is True
    assert body["summary"]["paper_id"] == paper_id
    assert body["summary"]["summary_text"] == "Generated section summary."
    assert body["summary"]["llm_model"] == "pytest-model"
    assert body["summary"]["prompt_version"] == SECTION_PROMPT_VERSION


def test_generate_paper_summary_falls_back_to_abstract_when_pdf_fetch_fails(monkeypatch):
    paper_id = str(uuid4())
    client = make_test_client(
        FakeSupabaseClient(
            papers=[
                {
                    "id": paper_id,
                    "title": "Mock Paper",
                    "abstract": "A useful abstract.",
                    "pdf_url": "https://example.com/missing.pdf",
                }
            ]
        )
    )

    def fake_fetch_pdf_bytes(pdf_url):
        raise PdfFetchError("PDF download failed.")

    def fake_generate_summary_text(title, abstract, custom_instructions=None):
        assert title == "Mock Paper"
        assert abstract == "A useful abstract."
        assert custom_instructions is None
        return GeneratedSummary(
            summary_text="Fallback abstract summary.",
            llm_provider="openai",
            llm_model="pytest-model",
            prompt_version=PROMPT_VERSION,
        )

    monkeypatch.setattr(paper_summaries, "fetch_pdf_bytes", fake_fetch_pdf_bytes)
    monkeypatch.setattr(paper_summaries, "generate_summary_text", fake_generate_summary_text)

    response = client.post(f"/papers/{paper_id}/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["summary_text"] == "Fallback abstract summary."
    assert body["summary"]["prompt_version"] == PROMPT_VERSION


# [GenAI Usage 4] Codex Prompt
# Add a small cache-safety test slice for the final report's AI Summary claims. Keep these mocked
# and backend-only: stale prompt versions should regenerate, custom instructions should bypass a
# matching generic cache entry, and regenerate should replace an existing cached summary.
# [GenAI Usage 4] Response begins:
def test_generate_paper_summary_regenerates_when_cached_prompt_version_is_stale(monkeypatch):
    paper_id = str(uuid4())
    fake_client = FakeSupabaseClient(
        papers=[
            {
                "id": paper_id,
                "title": "Prompt Version Paper",
                "abstract": "Prompt version abstract.",
                "pdf_url": "https://example.com/prompt-version.pdf",
            }
        ],
        summaries=[
            {
                "paper_id": paper_id,
                "summary_text": "Old abstract summary.",
                "llm_provider": "openai",
                "llm_model": "old-model",
                "prompt_version": PROMPT_VERSION,
            }
        ],
    )
    client = make_test_client(fake_client)

    monkeypatch.setattr(
        paper_summaries,
        "fetch_pdf_bytes",
        lambda _pdf_url: b"%PDF prompt-version",
    )
    monkeypatch.setattr(
        paper_summaries,
        "extract_pdf_sections",
        lambda _pdf_bytes: [PaperSection(heading="Method", text="New section text.")],
    )

    def fake_generate_section_summary_text(title, sections, custom_instructions=None):
        assert title == "Prompt Version Paper"
        assert sections[0].heading == "Method"
        assert custom_instructions is None
        return GeneratedSummary(
            summary_text="Fresh section summary.",
            llm_provider="openai",
            llm_model="fresh-model",
            prompt_version=SECTION_PROMPT_VERSION,
        )

    monkeypatch.setattr(
        paper_summaries,
        "generate_section_summary_text",
        fake_generate_section_summary_text,
    )

    response = client.post(f"/papers/{paper_id}/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["generated"] is True
    assert body["stored"] is True
    assert body["summary"]["summary_text"] == "Fresh section summary."
    assert body["summary"]["prompt_version"] == SECTION_PROMPT_VERSION
    assert fake_client.tables["paper_summaries"][0]["summary_text"] == "Fresh section summary."


def test_generate_paper_summary_custom_instructions_bypass_cached_summary(monkeypatch):
    paper_id = str(uuid4())
    fake_client = FakeSupabaseClient(
        papers=[
            {
                "id": paper_id,
                "title": "Custom Instructions Paper",
                "abstract": "Custom instructions abstract.",
                "pdf_url": "https://example.com/custom-instructions.pdf",
            }
        ],
        summaries=[
            {
                "paper_id": paper_id,
                "summary_text": "Generic cached section summary.",
                "llm_provider": "openai",
                "llm_model": "gpt-4o-mini",
                "prompt_version": SECTION_PROMPT_VERSION,
            }
        ],
    )
    client = make_test_client(fake_client)

    monkeypatch.setattr(
        paper_summaries,
        "fetch_pdf_bytes",
        lambda _pdf_url: b"%PDF custom-instructions",
    )
    monkeypatch.setattr(
        paper_summaries,
        "extract_pdf_sections",
        lambda _pdf_bytes: [PaperSection(heading="Results", text="Result text.")],
    )

    def fake_generate_section_summary_text(title, sections, custom_instructions=None):
        assert title == "Custom Instructions Paper"
        assert sections[0].heading == "Results"
        assert custom_instructions == "focus on limitations"
        return GeneratedSummary(
            summary_text="Custom focused section summary.",
            llm_provider="openai",
            llm_model="custom-model",
            prompt_version=SECTION_PROMPT_VERSION,
        )

    monkeypatch.setattr(
        paper_summaries,
        "generate_section_summary_text",
        fake_generate_section_summary_text,
    )

    response = client.post(
        f"/papers/{paper_id}/summary",
        json={"custom_instructions": "focus on limitations"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["generated"] is True
    assert body["summary"]["summary_text"] == "Custom focused section summary."
    assert fake_client.tables["paper_summaries"][0]["summary_text"] == (
        "Custom focused section summary."
    )


def test_regenerate_paper_summary_replaces_existing_cached_summary(monkeypatch):
    paper_id = str(uuid4())
    fake_client = FakeSupabaseClient(
        papers=[
            {
                "id": paper_id,
                "title": "Replace Cache Paper",
                "abstract": "Replace cache abstract.",
            }
        ],
        summaries=[
            {
                "paper_id": paper_id,
                "summary_text": "Cached summary to replace.",
                "llm_provider": "openai",
                "llm_model": "old-model",
                "prompt_version": PROMPT_VERSION,
            }
        ],
    )
    client = make_test_client(fake_client)

    def fake_generate_summary_text(title, abstract, custom_instructions=None):
        assert title == "Replace Cache Paper"
        assert abstract == "Replace cache abstract."
        assert custom_instructions is None
        return GeneratedSummary(
            summary_text="Replacement summary.",
            llm_provider="openai",
            llm_model="replacement-model",
            prompt_version=PROMPT_VERSION,
        )

    monkeypatch.setattr(paper_summaries, "generate_summary_text", fake_generate_summary_text)

    response = client.post(
        f"/papers/{paper_id}/summary/regenerate",
        json={"use_pdf_sections": False},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["generated"] is True
    assert body["stored"] is True
    assert body["summary"]["summary_text"] == "Replacement summary."
    assert body["summary"]["llm_model"] == "replacement-model"
    assert fake_client.tables["paper_summaries"][0]["summary_text"] == "Replacement summary."


# [GenAI Usage 4] Response ends
def test_generate_paper_summary_can_disable_pdf_fallback(monkeypatch):
    paper_id = str(uuid4())
    client = make_test_client(
        FakeSupabaseClient(
            papers=[
                {
                    "id": paper_id,
                    "title": "Mock Paper",
                    "abstract": "A useful abstract.",
                    "pdf_url": "https://example.com/missing.pdf",
                }
            ]
        )
    )

    def fake_fetch_pdf_bytes(pdf_url):
        raise PdfFetchError("PDF download failed.")

    monkeypatch.setattr(paper_summaries, "fetch_pdf_bytes", fake_fetch_pdf_bytes)

    response = client.post(
        f"/papers/{paper_id}/summary",
        json={"fallback_to_abstract": False},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "PDF section summary unavailable: PDF download failed."
    )


def test_generate_paper_summary_maps_missing_content_to_400(monkeypatch):
    paper_id = str(uuid4())
    client = make_test_client(
        FakeSupabaseClient(
            papers=[
                {
                    "id": paper_id,
                    "title": "Mock Paper",
                    "abstract": None,
                }
            ]
        )
    )

    def fake_generate_summary_text(title, abstract, custom_instructions=None):
        assert title == "Mock Paper"
        assert abstract is None
        assert custom_instructions is None
        raise MissingPaperContentError("Paper abstract is missing.")

    monkeypatch.setattr(paper_summaries, "generate_summary_text", fake_generate_summary_text)

    response = client.post(
        f"/papers/{paper_id}/summary",
        json={"use_pdf_sections": False},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Paper abstract is missing."


def test_generate_paper_summary_maps_configuration_error_to_503(monkeypatch):
    paper_id = str(uuid4())
    client = make_test_client(
        FakeSupabaseClient(
            papers=[
                {
                    "id": paper_id,
                    "title": "Mock Paper",
                    "abstract": "A useful abstract.",
                }
            ]
        )
    )

    def fake_generate_summary_text(title, abstract, custom_instructions=None):
        assert title == "Mock Paper"
        assert abstract == "A useful abstract."
        raise SummaryConfigurationError("api key is not configured")

    monkeypatch.setattr(paper_summaries, "generate_summary_text", fake_generate_summary_text)

    response = client.post(
        f"/papers/{paper_id}/summary",
        json={"use_pdf_sections": False},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "api key is not configured"


def test_generate_paper_summary_maps_provider_error_to_502(monkeypatch):
    paper_id = str(uuid4())
    client = make_test_client(
        FakeSupabaseClient(
            papers=[
                {
                    "id": paper_id,
                    "title": "Mock Paper",
                    "abstract": "A useful abstract.",
                }
            ]
        )
    )

    def fake_generate_summary_text(title, abstract, custom_instructions=None):
        assert title == "Mock Paper"
        assert abstract == "A useful abstract."
        raise SummaryProviderError("LLM summary generation failed.")

    monkeypatch.setattr(paper_summaries, "generate_summary_text", fake_generate_summary_text)

    response = client.post(
        f"/papers/{paper_id}/summary",
        json={"use_pdf_sections": False},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "LLM summary generation failed."


# [GenAI Usage 2] Codex Prompt
# Please extend this same test file with a small final wrap-up slice for currently implemented
# behavior: add tests for GET /papers/{paper_id} (success and 404), and one test for
# POST /papers/{paper_id}/summary/regenerate. Keep everything mocked and do not modify
# production code.
# [GenAI Usage 2] Response begins:
def test_regenerate_paper_summary_returns_generated_summary(monkeypatch):
    paper_id = str(uuid4())
    client = make_test_client(
        FakeSupabaseClient(
            papers=[
                {
                    "id": paper_id,
                    "title": "Regenerate Paper",
                    "abstract": "Regenerate abstract.",
                }
            ]
        )
    )

    def fake_generate_summary_text(title, abstract, custom_instructions=None):
        assert title == "Regenerate Paper"
        assert abstract == "Regenerate abstract."
        assert custom_instructions is None
        return GeneratedSummary(
            summary_text="Regenerated summary.",
            llm_provider="openai",
            llm_model="pytest-model",
            prompt_version=PROMPT_VERSION,
        )

    monkeypatch.setattr(paper_summaries, "generate_summary_text", fake_generate_summary_text)

    response = client.post(
        f"/papers/{paper_id}/summary/regenerate",
        json={"use_pdf_sections": False},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["generated"] is True
    assert body["stored"] is True
    assert body["summary"]["paper_id"] == paper_id
    assert body["summary"]["summary_text"] == "Regenerated summary."


# Don't delete those comments
# [GenAI Usage 2] Response ends
# [GenAI Usage 3] Codex Prompt
# Please update the existing paper summary route tests for the current branch without turning this
# into a large test session. The previous route tests were written for the abstract-only MVP, but
# the backend now defaults to PDF-section summaries, persists generated summaries with upsert, and
# reuses cached summaries when the prompt version matches. Keep the fake Supabase client offline,
# add only the minimal fake upsert behavior needed by the route, and cover Person 6 QA cases around
# cache reuse, generated/stored flags, PDF fallback, disabled fallback, prompt-version behavior, and
# regenerate behavior that explicitly opts into abstract mode when PDF extraction is not the subject.
# [GenAI Usage 3] Response ends
# [GenAI Usage] Reflection
# I used Codex in multiple small prompt chunks here. The original route tests covered the first
# paper-summary route contract and the wrap-up paper detail/regenerate cases. The later additions
# updated stale abstract-only expectations for the current PDF-section workflow and documented the
# important AI QA paths: cache reuse, abstract fallback, disabled fallback, stored/generated flags,
# and error-to-status mapping. I also added harmless dummy Supabase environment values because the
# app imports Supabase config at module import time, while the tests still replace auth and database
# access with fakes.

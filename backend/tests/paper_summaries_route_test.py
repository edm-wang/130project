# Don't delete comments below
# [GenAI Usage 1] Codex Prompt
# Please add a small second TDD test file for Team 3's paper summary FastAPI routes. Keep the
# tests mocked and offline.
# Focus on route response shapes and LLM error-to-HTTP-status behavior.
# [GenAI Usage 1] Response begins:

import sys
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.routers import paper_summaries  # noqa: E402
from app.services.llm_summary import (  # noqa: E402
    GeneratedSummary,
    MissingPaperContentError,
    SummaryConfigurationError,
    SummaryProviderError,
)
from app.supabase.auth import AuthContext, get_auth_context  # noqa: E402


class FakeUser:
    def __init__(self):
        self.id = str(uuid4())
        self.email = "paper-summary-route-test@example.com"


class FakeQuery:
    def __init__(self, rows):
        self.rows = rows
        self.filters = {}

    def select(self, *_args):
        return self

    def eq(self, field, value):
        self.filters[field] = value
        return self

    def limit(self, *_args):
        return self

    def execute(self):
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
        return FakeQuery(self.tables[table_name])


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
                    "prompt_version": "paper_summary_v1",
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


def test_generate_paper_summary_returns_generated_summary(monkeypatch):
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

    def fake_generate_summary_text(title, abstract):
        assert title == "Mock Paper"
        assert abstract == "A useful abstract."
        return GeneratedSummary(
            summary_text="Generated summary.",
            llm_provider="openai",
            llm_model="pytest-model",
            prompt_version="paper_summary_v1",
        )

    monkeypatch.setattr(paper_summaries, "generate_summary_text", fake_generate_summary_text)

    response = client.post(f"/papers/{paper_id}/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["generated"] is True
    assert body["stored"] is False
    assert body["summary"]["paper_id"] == paper_id
    assert body["summary"]["summary_text"] == "Generated summary."
    assert body["summary"]["llm_model"] == "pytest-model"


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

    def fake_generate_summary_text(title, abstract):
        assert title == "Mock Paper"
        assert abstract is None
        raise MissingPaperContentError("Paper abstract is missing.")

    monkeypatch.setattr(paper_summaries, "generate_summary_text", fake_generate_summary_text)

    response = client.post(f"/papers/{paper_id}/summary")

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

    def fake_generate_summary_text(title, abstract):
        assert title == "Mock Paper"
        assert abstract == "A useful abstract."
        raise SummaryConfigurationError("api key is not configured")

    monkeypatch.setattr(paper_summaries, "generate_summary_text", fake_generate_summary_text)

    response = client.post(f"/papers/{paper_id}/summary")

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

    def fake_generate_summary_text(title, abstract):
        assert title == "Mock Paper"
        assert abstract == "A useful abstract."
        raise SummaryProviderError("LLM summary generation failed.")

    monkeypatch.setattr(paper_summaries, "generate_summary_text", fake_generate_summary_text)

    response = client.post(f"/papers/{paper_id}/summary")

    assert response.status_code == 502
    assert response.json()["detail"] == "LLM summary generation failed."


# [GenAI Usage 1] Response ends
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

    def fake_generate_summary_text(title, abstract):
        assert title == "Regenerate Paper"
        assert abstract == "Regenerate abstract."
        return GeneratedSummary(
            summary_text="Regenerated summary.",
            llm_provider="openai",
            llm_model="pytest-model",
            prompt_version="paper_summary_v1",
        )

    monkeypatch.setattr(paper_summaries, "generate_summary_text", fake_generate_summary_text)

    response = client.post(f"/papers/{paper_id}/summary/regenerate")

    assert response.status_code == 200
    body = response.json()
    assert body["generated"] is True
    assert body["stored"] is False
    assert body["summary"]["paper_id"] == paper_id
    assert body["summary"]["summary_text"] == "Regenerated summary."


# Don't delete those comments
# [GenAI Usage 2] Response ends
# [GenAI Usage] Reflection
# I used Codex in two prompt chunks here. The first chunk generated the base route-contract tests
# for summary fetch/generation and error mapping. The second chunk added the missing wrap-up tests
# for paper detail and regenerate endpoints so the current behavior is fully covered without touching
# production code. I reviewed the fake Supabase query object to ensure it only supports the
# select/eq/limit/execute chain used by paper_summaries.py, which keeps failures focused on route
# contract changes rather than unrelated infrastructure behavior.

# Don't delete comments below
# [GenAI Usage 1] Codex Prompt
# Please add a small live integration test for the Team 3 paper summary route. This test should be
# opt-in because it uses a real OpenAI key and writes temporary rows to the connected Supabase
# project. Keep the scope narrow: insert one dummy paper, call the real FastAPI summary route with
# abstract-based generation so no external PDF is fetched, assert that OpenAI-generated summary
# metadata is returned and persisted, and clean up all inserted rows afterward.
# [GenAI Usage 1] Response begins:

import os
import sys
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest
from dotenv import dotenv_values, load_dotenv
from fastapi import FastAPI
from fastapi.testclient import TestClient
from supabase import create_client


BACKEND_DIR = Path(__file__).resolve().parents[1]
SUPABASE_DIR = BACKEND_DIR / "app" / "supabase"
sys.path.insert(0, str(BACKEND_DIR))


def load_supabase_env_from_temp_path():
    source_env_path = SUPABASE_DIR / ".env"
    if not source_env_path.exists():
        return {}

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_env_path = Path(temp_dir) / ".env"
        temp_env_path.write_text(source_env_path.read_text())
        load_dotenv(temp_env_path)
        return dotenv_values(temp_env_path)


SUPABASE_ENV = load_supabase_env_from_temp_path()
os.environ.setdefault("SUPABASE_URL", SUPABASE_ENV.get("SUPABASE_URL", ""))
os.environ.setdefault(
    "SUPABASE_PUBLISHABLE_KEY",
    SUPABASE_ENV.get("SUPABASE_PUBLISHABLE_KEY", ""),
)

from app.routers import paper_summaries  # noqa: E402
from app.services.summary_prompt import PROMPT_VERSION  # noqa: E402
from app.supabase.auth import AuthContext, get_auth_context  # noqa: E402


class FakeUser:
    def __init__(self, user_id: str):
        self.id = user_id
        self.email = "paper-summary-live-integration@example.com"


def get_env_value(key):
    return os.getenv(key) or SUPABASE_ENV.get(key)


@pytest.fixture
def live_supabase_client():
    if get_env_value("RUN_LIVE_LLM_TESTS") != "1":
        pytest.skip("Set RUN_LIVE_LLM_TESTS=1 to run live OpenAI/Supabase tests")

    if not get_env_value("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY is required for this live integration test")

    supabase_url = get_env_value("SUPABASE_URL")
    service_key = get_env_value("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not service_key:
        pytest.skip("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required")

    return create_client(supabase_url, service_key)


@pytest.fixture
def test_app(live_supabase_client):
    app = FastAPI()
    app.include_router(paper_summaries.summary_router)
    app.dependency_overrides[get_auth_context] = lambda: AuthContext(
        user=FakeUser(str(uuid4())),
        access_token="pytest-live-token",
        client=live_supabase_client,
    )
    try:
        yield app
    finally:
        app.dependency_overrides.clear()


def insert_live_test_paper(live_supabase_client, *, abstract):
    test_run_id = str(uuid4())
    paper_response = (
        live_supabase_client.table("papers")
        .insert(
            {
                "source": "manual",
                "source_id": f"pytest-live-summary-{test_run_id}",
                "title": "Live Integration Test Paper About Retrieval Quality",
                "abstract": abstract,
                "authors_text": "Pytest Author",
                "categories": ["integration-test"],
                "source_url": "https://example.com/live-summary-integration-test",
            }
        )
        .execute()
    )
    assert paper_response.data
    return paper_response.data[0]["id"]


def delete_live_test_paper(live_supabase_client, paper_id):
    if not paper_id:
        return
    (
        live_supabase_client.table("paper_summaries")
        .delete()
        .eq("paper_id", paper_id)
        .execute()
    )
    (
        live_supabase_client.table("papers")
        .delete()
        .eq("id", paper_id)
        .execute()
    )


def get_stored_summary(live_supabase_client, paper_id):
    response = (
        live_supabase_client.table("paper_summaries")
        .select("paper_id, summary_text, prompt_version, summary_status")
        .eq("paper_id", paper_id)
        .limit(1)
        .execute()
    )
    return response.data[0] if response.data else None


def upsert_live_cached_summary(
    live_supabase_client,
    paper_id,
    *,
    summary_text,
    prompt_version=PROMPT_VERSION,
):
    response = (
        live_supabase_client.table("paper_summaries")
        .upsert(
            {
                "paper_id": paper_id,
                "summary_text": summary_text,
                "summary_status": "completed",
                "llm_provider": "pytest",
                "llm_model": "cached-test-model",
                "prompt_version": prompt_version,
                "error_message": None,
            },
            on_conflict="paper_id",
        )
        .execute()
    )
    assert response.data
    return response.data[0]


def test_generate_paper_summary_live_openai_and_supabase_storage(
    live_supabase_client,
    test_app,
):
    paper_id = None

    try:
        paper_id = insert_live_test_paper(
            live_supabase_client,
            abstract=(
                "This test paper studies retrieval quality for research-paper "
                "recommendation systems. It compares a baseline keyword matcher "
                "with an embedding-based retriever and reports improved ranking "
                "quality on a small evaluation set."
            ),
        )

        response = TestClient(test_app, raise_server_exceptions=False).post(
            f"/papers/{paper_id}/summary",
            json={"use_pdf_sections": False},
        )

        assert response.status_code == 200, response.text
        body = response.json()
        summary = body["summary"]
        assert body["generated"] is True
        assert body["stored"] is True
        assert summary["paper_id"] == paper_id
        assert summary["summary_status"] == "completed"
        assert summary["llm_provider"] == "openai"
        assert summary["prompt_version"] == PROMPT_VERSION
        assert len(summary["summary_text"].strip()) > 40

        stored_summary = get_stored_summary(live_supabase_client, paper_id)
        assert stored_summary
        assert stored_summary["paper_id"] == paper_id
        assert stored_summary["prompt_version"] == PROMPT_VERSION
        assert stored_summary["summary_status"] == "completed"
        assert stored_summary["summary_text"] == summary["summary_text"]
    finally:
        delete_live_test_paper(live_supabase_client, paper_id)


# [GenAI Usage 1] Response ends
# [GenAI Usage 2] Codex Prompt
# Please add more opt-in live integration coverage for Person 6's AI QA responsibilities around
# summary route behavior. Keep these tests small and clean up all rows. Cover cached summary reuse
# against the real Supabase table and missing-abstract error handling without triggering OpenAI.
# These tests should continue to require RUN_LIVE_LLM_TESTS=1 so normal pytest runs do not spend API
# calls or write to the connected Supabase project.
# [GenAI Usage 2] Response begins:


def test_generate_paper_summary_live_reuses_cached_summary(
    live_supabase_client,
    test_app,
):
    paper_id = None

    try:
        paper_id = insert_live_test_paper(
            live_supabase_client,
            abstract=(
                "This cache test paper studies short abstract summarization for "
                "research discovery tools. It should generate once and then reuse "
                "the stored summary when the prompt version still matches."
            ),
        )

        first_response = TestClient(test_app, raise_server_exceptions=False).post(
            f"/papers/{paper_id}/summary",
            json={"use_pdf_sections": False},
        )
        assert first_response.status_code == 200, first_response.text
        first_body = first_response.json()
        assert first_body["generated"] is True

        second_response = TestClient(test_app, raise_server_exceptions=False).post(
            f"/papers/{paper_id}/summary",
            json={"use_pdf_sections": False},
        )
        assert second_response.status_code == 200, second_response.text
        second_body = second_response.json()
        assert second_body["generated"] is False
        assert second_body["stored"] is True
        assert second_body["summary"]["summary_text"] == first_body["summary"]["summary_text"]
        assert second_body["summary"]["prompt_version"] == PROMPT_VERSION
    finally:
        delete_live_test_paper(live_supabase_client, paper_id)


def test_generate_paper_summary_live_missing_abstract_returns_400_without_storage(
    live_supabase_client,
    test_app,
):
    paper_id = None

    try:
        paper_id = insert_live_test_paper(live_supabase_client, abstract=None)

        response = TestClient(test_app, raise_server_exceptions=False).post(
            f"/papers/{paper_id}/summary",
            json={"use_pdf_sections": False},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Paper abstract is missing."
        assert get_stored_summary(live_supabase_client, paper_id) is None
    finally:
        delete_live_test_paper(live_supabase_client, paper_id)


# [GenAI Usage 2] Response ends
# [GenAI Usage 3] Codex Prompt
# Add a few more opt-in live API tests for report-critical summary cache behavior. Keep them
# bounded to one OpenAI route call each by seeding cached paper_summaries rows directly, then verify
# custom instructions, stale prompt versions, and regenerate requests do not incorrectly reuse cache.
# [GenAI Usage 3] Response begins:


def test_generate_paper_summary_live_custom_instructions_bypass_cached_summary(
    live_supabase_client,
    test_app,
):
    paper_id = None
    cached_text = "Cached generic summary that should not satisfy custom instructions."

    try:
        paper_id = insert_live_test_paper(
            live_supabase_client,
            abstract=(
                "This paper studies custom summary instructions for AI-assisted "
                "research discovery. It compares generic summaries with summaries "
                "that emphasize limitations and evaluation caveats."
            ),
        )
        upsert_live_cached_summary(
            live_supabase_client,
            paper_id,
            summary_text=cached_text,
        )

        response = TestClient(test_app, raise_server_exceptions=False).post(
            f"/papers/{paper_id}/summary",
            json={
                "use_pdf_sections": False,
                "custom_instructions": (
                    "Focus on limitations and evaluation caveats rather than generic benefits."
                ),
            },
        )

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["generated"] is True
        assert body["stored"] is True
        assert body["summary"]["prompt_version"] == PROMPT_VERSION
        assert body["summary"]["summary_text"] != cached_text

        stored_summary = get_stored_summary(live_supabase_client, paper_id)
        assert stored_summary
        assert stored_summary["summary_text"] == body["summary"]["summary_text"]
    finally:
        delete_live_test_paper(live_supabase_client, paper_id)


def test_generate_paper_summary_live_stale_prompt_version_regenerates(
    live_supabase_client,
    test_app,
):
    paper_id = None
    stale_text = "Stale cached summary from an old prompt version."

    try:
        paper_id = insert_live_test_paper(
            live_supabase_client,
            abstract=(
                "This paper studies prompt-version cache invalidation for generated "
                "paper summaries. It verifies that stale prompt metadata should force "
                "a fresh LLM call instead of reusing old summary text."
            ),
        )
        upsert_live_cached_summary(
            live_supabase_client,
            paper_id,
            summary_text=stale_text,
            prompt_version="paper_summary_legacy_test",
        )

        response = TestClient(test_app, raise_server_exceptions=False).post(
            f"/papers/{paper_id}/summary",
            json={"use_pdf_sections": False},
        )

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["generated"] is True
        assert body["stored"] is True
        assert body["summary"]["prompt_version"] == PROMPT_VERSION
        assert body["summary"]["summary_text"] != stale_text

        stored_summary = get_stored_summary(live_supabase_client, paper_id)
        assert stored_summary["prompt_version"] == PROMPT_VERSION
        assert stored_summary["summary_text"] == body["summary"]["summary_text"]
    finally:
        delete_live_test_paper(live_supabase_client, paper_id)


def test_regenerate_paper_summary_live_replaces_cached_summary(
    live_supabase_client,
    test_app,
):
    paper_id = None
    cached_text = "Cached summary that regenerate should replace."

    try:
        paper_id = insert_live_test_paper(
            live_supabase_client,
            abstract=(
                "This paper studies explicit regeneration of AI paper summaries. "
                "The service should replace stored summaries when the user requests "
                "a fresh generation."
            ),
        )
        upsert_live_cached_summary(
            live_supabase_client,
            paper_id,
            summary_text=cached_text,
        )

        response = TestClient(test_app, raise_server_exceptions=False).post(
            f"/papers/{paper_id}/summary/regenerate",
            json={"use_pdf_sections": False},
        )

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["generated"] is True
        assert body["stored"] is True
        assert body["summary"]["prompt_version"] == PROMPT_VERSION
        assert body["summary"]["summary_text"] != cached_text

        stored_summary = get_stored_summary(live_supabase_client, paper_id)
        assert stored_summary["summary_text"] == body["summary"]["summary_text"]
    finally:
        delete_live_test_paper(live_supabase_client, paper_id)


# [GenAI Usage 3] Response ends
# [GenAI Usage] Reflection
# I used Codex to create opt-in live integration tests instead of adding them to the normal mocked
# suite. That matters because these tests can spend real OpenAI requests and write to the real
# Supabase project. The tests keep the blast radius small by inserting identifiable dummy papers,
# using abstract-based summary generation, checking both stored rows and route responses, and deleting
# generated summaries and papers in finally blocks.

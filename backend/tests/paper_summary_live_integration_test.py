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


def test_generate_paper_summary_live_openai_and_supabase_storage(
    live_supabase_client,
    test_app,
):
    paper_id = None
    test_run_id = str(uuid4())
    paper_source_id = f"pytest-live-summary-{test_run_id}"

    try:
        paper_response = (
            live_supabase_client.table("papers")
            .insert(
                {
                    "source": "manual",
                    "source_id": paper_source_id,
                    "title": "Live Integration Test Paper About Retrieval Quality",
                    "abstract": (
                        "This test paper studies retrieval quality for research-paper "
                        "recommendation systems. It compares a baseline keyword matcher "
                        "with an embedding-based retriever and reports improved ranking "
                        "quality on a small evaluation set."
                    ),
                    "authors_text": "Pytest Author",
                    "categories": ["integration-test"],
                    "source_url": "https://example.com/live-summary-integration-test",
                }
            )
            .execute()
        )
        assert paper_response.data
        paper_id = paper_response.data[0]["id"]

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

        stored_response = (
            live_supabase_client.table("paper_summaries")
            .select("paper_id, summary_text, prompt_version, summary_status")
            .eq("paper_id", paper_id)
            .limit(1)
            .execute()
        )
        assert stored_response.data
        stored_summary = stored_response.data[0]
        assert stored_summary["paper_id"] == paper_id
        assert stored_summary["prompt_version"] == PROMPT_VERSION
        assert stored_summary["summary_status"] == "completed"
        assert stored_summary["summary_text"] == summary["summary_text"]
    finally:
        if paper_id:
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


# [GenAI Usage 1] Response ends
# [GenAI Usage] Reflection
# I used Codex to create this as an opt-in live integration test instead of adding it to the normal
# mocked suite. That matters because the test spends a real OpenAI request and writes to the real
# Supabase project. The test keeps the blast radius small by using abstract-based summary generation,
# inserting one identifiable dummy paper, asserting the stored summary row, and deleting both the
# generated summary and paper in a finally block.

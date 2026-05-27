# Don't Delete the comments below
# [GenAI Usage] Codex Prompt
# I need to write integration tests for recommendation endpoint. Can u write this test in recommendation_integration_test.py under /test
# U can insert dummy value into recommendation_batch production database directly, but make sure to delete it
# [Debugging prompts]
# Dont edit recommendation_test, only edit this integration test file
# Show me the command to test it
# Can u load_dotenv via a temporary path?
# is it still use fake uer? Delete them, only focus on integration testing
# Why a service role key is required? 
# Is it ok to send a pr right now? but dont commit for me

# [GenAI Usage] Response begin (Final)

import os
import sys
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest
from dotenv import dotenv_values, load_dotenv
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

from app.main import app  # noqa: E402
from app.supabase.auth import AuthContext, get_auth_context  # noqa: E402


INTEGRATION_ALGORITHM_VERSION = "pytest_recommendation_integration"


class FakeUser:
    def __init__(self, user_id: str):
        self.id = user_id
        self.email = "recommendation-integration-test@example.com"


def get_env_value(key):
    return os.getenv(key) or SUPABASE_ENV.get(key)


@pytest.fixture
def supabase_client():
    supabase_url = get_env_value("SUPABASE_URL")
    supabase_key = (
        get_env_value("SUPABASE_SERVICE_ROLE_KEY")
        or get_env_value("SUPABASE_SECRET_KEY")
        or get_env_value("SUPABASE_PUBLISHABLE_KEY")
    )

    if supabase_url == "https://example.supabase.co":
        supabase_url = SUPABASE_ENV.get("SUPABASE_URL")
    if supabase_key == "test-key":
        supabase_key = SUPABASE_ENV.get("SUPABASE_PUBLISHABLE_KEY")

    if (
        not supabase_url
        or not supabase_key
        or supabase_url == "https://example.supabase.co"
        or supabase_key == "test-key"
    ):
        pytest.skip("Supabase credentials are required for this integration test")

    return create_client(supabase_url, supabase_key)


@pytest.fixture
def test_user(supabase_client):
    service_role_key = (
        get_env_value("SUPABASE_SERVICE_ROLE_KEY")
        or get_env_value("SUPABASE_SECRET_KEY")
    )
    if not service_role_key:
        pytest.skip(
            "SUPABASE_SERVICE_ROLE_KEY or SUPABASE_SECRET_KEY is required "
            "to create and delete a dummy auth user"
        )

    test_run_id = str(uuid4())
    email = f"recommendation-integration-{test_run_id}@example.com"
    auth_user_id = None

    try:
        auth_response = supabase_client.auth.admin.create_user(
            {
                "email": email,
                "password": f"pytest-{test_run_id}",
                "email_confirm": True,
            }
        )
        assert auth_response.user
        auth_user_id = auth_response.user.id

        app_user_response = (
            supabase_client.table("app_users")
            .insert(
                {
                    "id": auth_user_id,
                    "email": email,
                    "display_name": "Recommendation Integration Test User",
                }
            )
            .execute()
        )
        assert app_user_response.data

        yield FakeUser(auth_user_id)
    finally:
        if auth_user_id:
            (
                supabase_client.table("app_users")
                .delete()
                .eq("id", auth_user_id)
                .execute()
            )
            supabase_client.auth.admin.delete_user(auth_user_id)


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


def test_get_recommendations_returns_latest_completed_batch_with_joined_papers(
    supabase_client,
    test_user,
):
    batch_id = None
    paper_id = None
    recommendation_id = None
    test_run_id = str(uuid4())
    paper_source_id = f"pytest-recommendation-integration-{test_run_id}"
    stale_cleanup_query = (
        supabase_client.table("recommendation_batches")
        .delete()
        .eq("user_id", test_user.id)
        .eq("algorithm_version", INTEGRATION_ALGORITHM_VERSION)
    )
    stale_cleanup_query.execute()

    try:
        paper_response = (
            supabase_client.table("papers")
            .insert(
                {
                    "source": "manual",
                    "source_id": paper_source_id,
                    "title": "Integration Test Recommendation Paper",
                    "abstract": "A dummy paper used by the recommendation integration test.",
                    "authors_text": "Pytest Author",
                    "categories": ["integration-test"],
                    "source_url": "https://example.com/integration-test-paper",
                }
            )
            .execute()
        )
        assert paper_response.data
        paper_id = paper_response.data[0]["id"]

        insert_response = (
            supabase_client.table("recommendation_batches")
            .insert(
                {
                    "user_id": test_user.id,
                    "status": "completed",
                    "algorithm_version": INTEGRATION_ALGORITHM_VERSION,
                    "parameters": {"test_run_id": test_run_id},
                    "candidate_count": 3,
                    "final_count": 1,
                    "completed_at": "2099-01-01T00:00:00+00:00",
                    "created_at": "2099-01-01T00:00:00+00:00",
                }
            )
            .execute()
        )
        assert insert_response.data
        batch_id = insert_response.data[0]["id"]

        recommendation_response = (
            supabase_client.table("recommendations")
            .insert(
                {
                    "batch_id": batch_id,
                    "paper_id": paper_id,
                    "rank_position": 1,
                    "final_score": 0.95,
                    "interest_score": 0.85,
                    "saved_paper_score": 0.05,
                    "upvote_score": 0.03,
                    "downvote_penalty": 0,
                    "freshness_score": 0.02,
                    "explanation_summary": "Dummy joined recommendation.",
                }
            )
            .execute()
        )
        assert recommendation_response.data
        recommendation_id = recommendation_response.data[0]["id"]

        app.dependency_overrides[get_auth_context] = lambda: AuthContext(
            user=test_user,
            access_token="pytest-token",
            client=supabase_client,
        )

        response = TestClient(app, raise_server_exceptions=False).get("/recommendations")

        assert response.status_code == 200
        body = response.json()
        assert body["batch"]["id"] == batch_id
        assert body["batch"]["user_id"] == test_user.id
        assert body["batch"]["status"] == "completed"
        assert body["batch"]["parameters"]["test_run_id"] == test_run_id

        assert len(body["recommendations"]) == 1
        recommendation = body["recommendations"][0]
        assert recommendation["id"] == recommendation_id
        assert recommendation["batch_id"] == batch_id
        assert recommendation["paper_id"] == paper_id
        assert recommendation["rank_position"] == 1
        assert recommendation["paper"]["id"] == paper_id
        assert recommendation["paper"]["source_id"] == paper_source_id
        assert recommendation["paper"]["title"] == "Integration Test Recommendation Paper"
    finally:
        cleanup_query = (
            supabase_client.table("recommendation_batches")
            .delete()
            .eq("user_id", test_user.id)
            .eq("algorithm_version", INTEGRATION_ALGORITHM_VERSION)
        )
        if batch_id:
            cleanup_query = cleanup_query.eq("id", batch_id)
        cleanup_query.execute()

        if paper_id:
            (
                supabase_client.table("papers")
                .delete()
                .eq("id", paper_id)
                .execute()
            )
# Don't delete those comments
# [GenAI Usage] Response ends
# [GenAI Usage] Reflection
# I did a thorough walk-through of the code. I saw it creates the dummy user, papers, recommendations, recommendation batches. 
# Then, it sets up a dummy client server and calls the endpoint. 
# Finally, it use assert statement to ensure the recommendation is the latest. 
# This piece of code looks correct to me and the quality of the testing /GET recommendation is high.
# Not to mention, the code cleanly everything it inserts to ensure the state of db is intact.
# So, this code should be accepted.

# Don't delete comments below
# [GenAI Usage] Codex Prompt
#  can u write one integration on the happy path about the upvote feature? You need to first ingest a fake recommendation and a fake
#  paper and then downvote it by setting up a client and then fail fast if any unexpected situation happens. If the voting is
#  succesfully, then assert the feedback field. You need to test both upvote and downvote -- so there are a 2 tests. Dont forgot to
#  delete the fake recommendation after the integration test finishes. integration test shall be added here: /Users/jerry/
#  Desktop/130project/backend/tests. the file name i suggest would be rec_upvote_downvote_test.py
# [GenAI Usage] LLM reseponse begins:


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

from app.routers.recommendation_batch import rec_router  # noqa: E402
from app.supabase.auth import AuthContext, get_auth_context  # noqa: E402


INTEGRATION_ALGORITHM_VERSION = "pytest_rec_feedback_integration"


class FakeUser:
    def __init__(self, user_id: str):
        self.id = user_id
        self.email = "rec-feedback-integration-test@example.com"


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
    email = f"rec-feedback-integration-{test_run_id}@example.com"
    auth_user_id = None

    try:
        auth_response = supabase_client.auth.admin.create_user(
            {
                "email": email,
                "password": f"pytest-{test_run_id}",
                "email_confirm": True,
            }
        )
        assert auth_response.user, "Failed to create dummy auth user"
        auth_user_id = auth_response.user.id

        app_user_response = (
            supabase_client.table("app_users")
            .insert(
                {
                    "id": auth_user_id,
                    "email": email,
                    "display_name": "Recommendation Feedback Integration Test User",
                }
            )
            .execute()
        )
        assert app_user_response.data, "Failed to create dummy app user"

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


@pytest.fixture
def test_app(test_user, supabase_client):
    app = FastAPI()
    app.include_router(rec_router)
    app.dependency_overrides[get_auth_context] = lambda: AuthContext(
        user=test_user,
        access_token="pytest-token",
        client=supabase_client,
    )
    return app


def _insert_one(response, table_name):
    if not response.data:
        pytest.fail(f"Expected {table_name} insert to return one row")
    return response.data[0]


def _insert_fake_recommendation(supabase_client, test_user, feedback_label):
    test_run_id = str(uuid4())
    rows = {}

    try:
        paper = _insert_one(
            (
                supabase_client.table("papers")
                .insert(
                    {
                        "source": "manual",
                        "source_id": f"pytest-rec-feedback-{feedback_label}-{test_run_id}",
                        "title": f"Feedback Integration Test Paper {feedback_label}",
                        "abstract": "A dummy paper used by the feedback integration test.",
                        "authors_text": "Pytest Author",
                        "categories": ["integration-test"],
                        "source_url": "https://example.com/feedback-integration-test-paper",
                    }
                )
                .execute()
            ),
            "papers",
        )
        rows["paper_id"] = paper["id"]

        batch = _insert_one(
            (
                supabase_client.table("recommendation_batches")
                .insert(
                    {
                        "user_id": test_user.id,
                        "status": "completed",
                        "algorithm_version": INTEGRATION_ALGORITHM_VERSION,
                        "parameters": {
                            "test_run_id": test_run_id,
                            "feedback_label": feedback_label,
                        },
                        "candidate_count": 1,
                        "final_count": 1,
                        "completed_at": "2099-01-01T00:00:00+00:00",
                        "created_at": "2099-01-01T00:00:00+00:00",
                    }
                )
                .execute()
            ),
            "recommendation_batches",
        )
        rows["batch_id"] = batch["id"]

        recommendation = _insert_one(
            (
                supabase_client.table("recommendations")
                .insert(
                    {
                        "batch_id": rows["batch_id"],
                        "paper_id": rows["paper_id"],
                        "rank_position": 1,
                        "final_score": 0.95,
                        "interest_score": 0.85,
                        "saved_paper_score": 0.05,
                        "upvote_score": 0.03,
                        "downvote_penalty": 0,
                        "freshness_score": 0.02,
                        "explanation_summary": "Dummy recommendation for feedback.",
                    }
                )
                .execute()
            ),
            "recommendations",
        )
        rows["recommendation_id"] = recommendation["id"]
    except Exception:
        _delete_fake_recommendation_data(supabase_client, test_user, rows)
        raise

    return rows


def _delete_fake_recommendation_data(supabase_client, test_user, rows):
    paper_id = rows.get("paper_id")
    recommendation_id = rows.get("recommendation_id")
    batch_id = rows.get("batch_id")

    if paper_id:
        (
            supabase_client.table("recommendation_feedback")
            .delete()
            .eq("user_id", test_user.id)
            .eq("paper_id", paper_id)
            .execute()
        )

    if recommendation_id:
        (
            supabase_client.table("recommendations")
            .delete()
            .eq("id", recommendation_id)
            .execute()
        )

    if batch_id:
        (
            supabase_client.table("recommendation_batches")
            .delete()
            .eq("id", batch_id)
            .execute()
        )

    if paper_id:
        (
            supabase_client.table("papers")
            .delete()
            .eq("id", paper_id)
            .execute()
        )


def _assert_recommendation_feedback_happy_path(
    supabase_client,
    test_user,
    test_app,
    feedback_label,
    expected_feedback_value,
):
    rows = {}

    try:
        rows = _insert_fake_recommendation(
            supabase_client,
            test_user,
            feedback_label,
        )

        response = TestClient(test_app, raise_server_exceptions=False).post(
            f"/recommendations/feedback/{rows['paper_id']}",
            json={"feedback": feedback_label},
        )

        assert response.status_code == 200, response.text
        body = response.json()
        feedback = body["feedback"]
        assert feedback["user_id"] == test_user.id
        assert feedback["paper_id"] == rows["paper_id"]
        assert feedback["feedback_value"] == expected_feedback_value
        assert body["feedback_type"] == feedback_label
    finally:
        _delete_fake_recommendation_data(supabase_client, test_user, rows)


def test_recommendation_feedback_upvote_happy_path(
    supabase_client,
    test_user,
    test_app,
):
    _assert_recommendation_feedback_happy_path(
        supabase_client=supabase_client,
        test_user=test_user,
        test_app=test_app,
        feedback_label="upvote",
        expected_feedback_value=1,
    )


def test_recommendation_feedback_downvote_happy_path(
    supabase_client,
    test_user,
    test_app,
):
    _assert_recommendation_feedback_happy_path(
        supabase_client=supabase_client,
        test_user=test_user,
        test_app=test_app,
        feedback_label="downvote",
        expected_feedback_value=-1,
    )


# Don't delete those comments
# [GenAI Usage] Response ends
# [GenAI Usage] Reflection
# My prompt is very clear -- give high-level instruction to instruct Codex to insert dummy values into tables and then mock user's POST upvote and downvote request
# This code is exactly what how this happy-path integration test of upvote/downvote recommended paper feature shall be implemented. Therefore, this code looks great to me for the integration test.
# It shall be accepted. 
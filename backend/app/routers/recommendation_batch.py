from datetime import datetime, timezone, timedelta
from math import ceil
from typing import Optional

from fastapi import APIRouter, Depends, Query, Response
from supabase import Client

from app.supabase.auth import AuthContext, get_auth_context
from app.services.recommendation import RecGenParams
from app.services.recommendation_runner import (
    _fetch_active_interests,
    _fetch_feedback_rows,
    _fetch_saved_paper_rows,
    generate_recommentation_parameter_hash,
    generate_user_snapshot_hash,
)

rec_router = APIRouter(prefix='/recommendations')

FRESH_RECOMMENDATION_WINDOW_SECONDS = 24 * 60 * 60
DEFAULT_MIN_REC_GEN_RETRIEVAL_TOP_N = 100
DEFAULT_MAX_REC_GEN_RETRIEVAL_TOP_N = 200

def _limit_recommendations(
    recommendations: Optional[list[dict]],
    max_papers: Optional[int],
) -> list[dict]:
    recommendations = recommendations or []
    if max_papers is None:
        return recommendations
    return recommendations[:max_papers]

def _get_reusable_completed_recommendation_batch(client: Client, user, params: RecGenParams) -> Optional[dict]:
    user_id = str(user.id)
    active_interests = _fetch_active_interests(client, user_id)
    saved_paper_rows = _fetch_saved_paper_rows(client, user_id)
    feedback_rows = _fetch_feedback_rows(client, user_id)
    user_snapshot_hash = generate_user_snapshot_hash(
        user_id=user_id,
        interests=active_interests,
        saved_papers=saved_paper_rows,
        feedback_rows=feedback_rows,
    )

    completed_run = (
        client
        .table("recommendation_batches")
        .select("*")
        .eq("user_id", user_id)
        .eq("user_snapshot_hash", user_snapshot_hash)
        .eq("status", "completed")
        .eq("algorithm_version", params.algorithm_version)
        .order("created_at", desc=True)
        .execute()
    )

    if(not completed_run.data):
        return None

    expected_param_hash = generate_recommentation_parameter_hash(params)
    now_time = datetime.now(timezone.utc)
    for run in completed_run.data:
        run_param_hash = generate_recommentation_parameter_hash(run["parameters"])
        run_creation_time = datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))

        if(
            run_param_hash == expected_param_hash
            and run_creation_time >= now_time - timedelta(seconds=FRESH_RECOMMENDATION_WINDOW_SECONDS)
        ):
            return run

    return None

def _get_recommendation_generation_parameters(client: Client, user, max_papers: Optional[int] = None):
    if max_papers is None:
        return RecGenParams()

    params = RecGenParams()

    user_id = str(user.id)
    active_interests = _fetch_active_interests(client, user_id)
    num_interests = max(1, len(active_interests))
    target_candidates = max(max_papers * 2, DEFAULT_MIN_REC_GEN_RETRIEVAL_TOP_N)
    keep_top_n_per_interest = ceil(target_candidates / num_interests)

    params.keep_top_n_per_interest = max(1, min(
        keep_top_n_per_interest,
        DEFAULT_MAX_REC_GEN_RETRIEVAL_TOP_N,
    ))
    params.retrieval_top_n = max(
        params.keep_top_n_per_interest,
        DEFAULT_MIN_REC_GEN_RETRIEVAL_TOP_N,
    )
    params.retrieval_top_n = min(
        params.retrieval_top_n,
        DEFAULT_MAX_REC_GEN_RETRIEVAL_TOP_N,
    )
    return params


def _get_recommendations_for_batch(
    client: Client,
    batch_id: str,
    max_papers: Optional[int],
) -> list[dict]:
    response = (
        client
        .table("recommendations")
        .select("*, paper:papers(*)")
        .eq("batch_id", batch_id)
        .order("rank_position", desc=False)
        .execute()
    )
    return _limit_recommendations(response.data or [], max_papers)


@rec_router.get('')
def get_recommendation_batch(
    response: Response,
    max_papers: Optional[int] = Query(default=None, ge=0),
    auth: AuthContext = Depends(get_auth_context),
):
    user = auth.user
    client = auth.client

    rec_gen_params = _get_recommendation_generation_parameters(client, user, max_papers)
    reusable_completed_recommendation_batch = _get_reusable_completed_recommendation_batch(client, user, rec_gen_params)

    if(reusable_completed_recommendation_batch):
        return {
            "status": reusable_completed_recommendation_batch.get("status", "completed"),
            "batch": reusable_completed_recommendation_batch,
            "recommendations": _get_recommendations_for_batch(
                client,
                reusable_completed_recommendation_batch["id"],
                max_papers,
            )
        }

    from app.services.recommendation_runner import generate_recommendations_for_user 
    batch, recommendations = generate_recommendations_for_user(client, user, rec_gen_params)
    response.status_code = 201
    return {
        "status": batch.get("status", "completed"),
        "batch": batch,
        "recommendations": _limit_recommendations(recommendations, max_papers)
    }

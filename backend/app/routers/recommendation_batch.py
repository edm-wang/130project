from typing import Optional, Tuple

from fastapi import APIRouter, Depends, Query, Response
from supabase import Client

from app.supabase.auth import AuthContext, get_auth_context

rec_router = APIRouter(prefix='/recommendations')

def get_pending_recommendation_batch(client: Client, user) -> Tuple[bool, Optional[dict]]:
    pending_run = (
        client
        .table("recommendation_batches")
        .select("*")
        .eq("user_id", user.id)
        .eq("status", "pending")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if(pending_run.data):
        batch = pending_run.data[0]
        return True, batch

    return False, None


def _limit_recommendations(
    recommendations: Optional[list[dict]],
    max_papers: Optional[int],
) -> list[dict]:
    recommendations = recommendations or []
    if max_papers is None:
        return recommendations
    return recommendations[:max_papers]

@rec_router.get('')
def get_recommendation_batch(
    response: Response,
    max_papers: Optional[int] = Query(default=None, ge=0),
    auth: AuthContext = Depends(get_auth_context),
):
    user = auth.user
    client = auth.client

    has_pending_recommendation_batch, pending_recommendation_batch = get_pending_recommendation_batch(client, user)
    if(has_pending_recommendation_batch):
        response.status_code = 202
        return {
            "status": "pending",
            "batch": pending_recommendation_batch,
            "recommendations": [],
        }

    from app.services.recommendation_runner import generate_recommendations_for_user 
    batch, recommendations = generate_recommendations_for_user(client, user)
    response.status_code = 201
    return {
        "status": batch.get("status", "completed"),
        "batch": batch,
        "recommendations": _limit_recommendations(recommendations, max_papers)
    }

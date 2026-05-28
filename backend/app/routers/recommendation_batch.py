from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple

from fastapi import APIRouter, Depends, Query
from supabase import Client

from app.supabase.auth import AuthContext, get_auth_context

rec_router = APIRouter(prefix='/recommendations')
RECOMMENDATION_COOLDOWN_SECONDS = 30


def is_within_recommendation_cooldown(created_at: str) -> bool:
    creation_time = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    now_time = datetime.now(timezone.utc)
    return creation_time >= now_time - timedelta(
        seconds=RECOMMENDATION_COOLDOWN_SECONDS
    )


def get_completed_recommendation_batch(client: Client, user) -> Tuple[Optional[dict], Optional[list[dict]]]:
    """
    Return a tuple of the completed recommendation batch (if any), and the recommendation items (if any)
    """
    completed_run = (
        client
        .table("recommendation_batches")
        .select("*")
        .eq("user_id", user.id)
        .eq("status", "completed")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if(completed_run.data):
        batch = completed_run.data[0]

        if(is_within_recommendation_cooldown(batch["created_at"])):
            recommendation_items = (
                client
                .table("recommendations")
                .select("*, paper:papers(*)")
                .eq("batch_id", batch["id"])
                .order("rank_position", desc=False)
                .execute()
            ).data

            return batch, recommendation_items if recommendation_items else []
        
    return None, None


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
    max_papers: Optional[int] = Query(default=None, ge=0),
    auth: AuthContext = Depends(get_auth_context),
):
    user = auth.user
    client = auth.client

    completed_batch, completed_recommendations = get_completed_recommendation_batch(client, user)
    if(completed_batch is not None):
        return {
            "batch": completed_batch,
            "recommendations": _limit_recommendations(
                completed_recommendations,
                max_papers,
            )
        }

    from app.services.recommendation_runner import generate_recommendations_for_user 
    batch, recommendations = generate_recommendations_for_user(client, user)
    return {
        "batch": batch,
        "recommendations": _limit_recommendations(recommendations, max_papers)
    }

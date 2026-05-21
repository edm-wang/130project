from fastapi import APIRouter, Depends
from app.supabase.auth import get_user
from app.supabase.db import get_or_create_supabase_client

rec_router = APIRouter(prefix='/recommendations')


@rec_router.get('')
def get_recommendation_batch(user=Depends(get_user)):
    client = get_or_create_supabase_client()

    res = client.table('recommendation_batches').select('*').eq('user_id', user.id).eq("status", 'completed').order('created_at', desc=True).limit(1).execute()
    if not res.data:
        return {
            "recommendations": [],
            "batch": None,
        }

    batch = res.data[0]

    res = client.table('recommendations').select("*, paper:papers(*)").eq('batch_id', batch['id']).order('rank_position').execute()

    return {
        "batch": batch,
        "recommendations": res.data if res.data else []
    }

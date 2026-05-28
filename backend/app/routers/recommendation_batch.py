from fastapi import APIRouter, Depends
from app.supabase.auth import AuthContext, get_auth_context

rec_router = APIRouter(prefix='/recommendations')


@rec_router.get('')
def get_recommendation_batch(auth: AuthContext = Depends(get_auth_context)):
    user = auth.user
    client = auth.client

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


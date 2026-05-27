from fastapi import APIRouter, Depends

from app.supabase.auth import AuthContext, get_auth_context

saved_papers_router = APIRouter(prefix="/saved-papers")


@saved_papers_router.get("")
def get_saved_papers(auth: AuthContext = Depends(get_auth_context)):
    client = auth.client
    user_id = str(auth.user.id)
    res = (
        client.table("saved_papers")
        .select(
            "id, paper_id, category, category_source, created_at,"
            " paper:papers(id, title, authors_text, categories, source_url, published_at, source)"
        )
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return {"saved_papers": res.data if res.data else []}

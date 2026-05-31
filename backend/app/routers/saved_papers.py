from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

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


class SavePaperRequest(BaseModel):
    paper_id: UUID


@saved_papers_router.post("", status_code=201)
def save_paper(body: SavePaperRequest, auth: AuthContext = Depends(get_auth_context)):
    client = auth.client
    user_id = str(auth.user.id)
    paper_id = str(body.paper_id)

    res = (
        client.table("saved_papers")
        .upsert(
            {"user_id": user_id, "paper_id": paper_id},
            on_conflict="user_id,paper_id",
        )
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=500, detail="Failed to save paper")
    return {"saved_paper": res.data[0]}


@saved_papers_router.delete("/{paper_id}", status_code=200)
def unsave_paper(paper_id: UUID, auth: AuthContext = Depends(get_auth_context)):
    client = auth.client
    user_id = str(auth.user.id)

    res = (
        client.table("saved_papers")
        .delete()
        .eq("user_id", user_id)
        .eq("paper_id", str(paper_id))
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Saved paper not found")
    return {"deleted": str(paper_id)}

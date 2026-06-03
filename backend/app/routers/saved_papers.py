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


#[GenAI Usage] Prompt: Auto-categorize a saved paper by assigning the first arXiv category from the linked paper row after saving it.
#[GenAI Usage] LLM response begins

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

    saved_paper = res.data[0]
    if saved_paper.get("category"):
        return {"saved_paper": saved_paper}

    auto_category = _get_first_paper_category(client, paper_id)
    if not auto_category:
        return {"saved_paper": saved_paper}

    category_res = (
        client.table("saved_papers")
        .update(
            {
                "category": auto_category,
                "category_source": "auto",
            }
        )
        .eq("id", saved_paper["id"])
        .execute()
    )
    if not category_res.data:
        raise HTTPException(status_code=500, detail="Failed to categorize saved paper")
    return {"saved_paper": category_res.data[0]}


def _get_first_paper_category(client, paper_id: str) -> str | None:
    res = (
        client.table("papers")
        .select("categories")
        .eq("id", paper_id)
        .limit(1)
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Paper not found")

    categories = res.data[0].get("categories")
    if not isinstance(categories, list):
        return None

    for category in categories:
        if isinstance(category, str) and category.strip():
            return category.strip()
    return None


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

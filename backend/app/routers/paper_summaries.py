from uuid import UUID
from fastapi import APIRouter, Depends,Header, HTTPException

from app.services.llm_summary import (
    MissingPaperContentError,
    SummaryConfigurationError,
    SummaryProviderError,
    generate_summary_text,
)
from app.supabase.auth import get_user
from app.supabase.db import get_or_create_supabase_client

summary_router = APIRouter(prefix="/papers",tags=["paper summaries"])

@summary_router.get('/{paper_id}/summary')
def get_paper_summary(paper_id: UUID, user=Depends(get_user)):
    client = get_or_create_supabase_client()
    summary = _get_existing_summary(client, str(paper_id))
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return {"summary":summary}

@summary_router.post('/{paper_id}/summary')
def generate_paper_summary(paper_id: UUID, user=Depends(get_user), authorization:str | None = Header(default=None)):
    client=get_or_create_supabase_client()
    token = authorization[7:].strip()
    client.postgrest.auth(token)
    paper_id_str = str(paper_id)
    # existing = _get_existing_summary(client, paper_id_str)
    # if existing: 
    #     return {"summary": existing, "generated": False}
    return _generate_and_store_summary(client, paper_id_str)

@summary_router.post("/{paper_id}/summary/regenerate")
def regenerate_paper_summary(paper_id: UUID, user=Depends(get_user)):
    client = get_or_create_supabase_client()
    return _generate_and_store_summary(client, str(paper_id))

def _generate_and_store_summary(client, paper_id:str):
    paper = _get_paper(client, paper_id)
    try: 
        generated = generate_summary_text(
            title=paper["title"],
            abstract=paper.get("abstract"),
        )
    except MissingPaperContentError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SummaryConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except SummaryProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    # row = {
    #     "paper_id": paper_id,
    #     "summary_text": generated.summary_text,
    #     "summary_status": "completed",
    #     "llm_provider": generated.llm_provider,
    #     "llm_model": generated.llm_model,
    #     "prompt_version": generated.prompt_version,
    #     "error_message": None,
    # }

    # res=(
    #     client.table("paper_summaries")
    #     .upsert(row, on_conflict="paper_id")
    #     .execute()
    # )

    # summary = res.data[0] if res.data else _get_existing_summary(client,paper_id)
    # return {"summary":summary, "generated": True}

    return {
      "summary": {
          "paper_id": paper_id,
          "summary_text": generated.summary_text,
          "llm_provider": generated.llm_provider,
          "llm_model": generated.llm_model,
          "prompt_version": generated.prompt_version,
      },
      "generated": True,
      "stored": False,
    }

def _get_paper(client, paper_id:str):
    res = (
        client.table("papers")
        .select("id,title,abstract")
        .eq("id", paper_id)
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Paper not found")
    return res.data[0]

def _get_existing_summary(client, paper_id:str):
    res=(
        client.table("paper_summaries")
        .select("*")
        .eq("paper_id", paper_id)
        .limit(1)
        .execute()
    )
    return res.data[0] if res.data else None

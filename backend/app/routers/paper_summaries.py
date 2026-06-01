from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.services.pdf_sections import (
    PdfExtractionError,
    PdfFetchError,
    extract_pdf_sections,
    fetch_pdf_bytes,
)
from app.services.llm_summary import (
    MissingPaperContentError,
    SummaryConfigurationError,
    SummaryProviderError,
    generate_section_summary_text,
    generate_summary_text,
)
from app.services.summary_prompt import PROMPT_VERSION, SECTION_PROMPT_VERSION
from app.supabase.auth import AuthContext, get_auth_context

summary_router = APIRouter(prefix="/papers",tags=["paper summaries"])

class SummaryGenerationRequest(BaseModel):
    custom_instructions: str | None = None
    force_regenerate: bool = False
    use_pdf_sections: bool = True
    fallback_to_abstract: bool = True


#[GenAI Usage] Prompt: the code below is the result of a conversation with Codex. The request was to restore persistent paper-summary caching for the Team 3 summary MVP and then extend it to summarize papers by PDF section. The implementation should use the existing authenticated Supabase client, check whether a matching summary already exists for a paper, fetch and extract paper PDF sections when available, allow optional caller-provided summary instructions, fall back to abstract-based summaries when configured, save generated summaries to the paper_summaries table, and return a consistent JSON response for generated and cached summaries.
#[GenAI Usage] LLM response begins

@summary_router.get('/{paper_id}')
def get_paper_detail(
    paper_id: UUID,
    auth: AuthContext = Depends(get_auth_context),
):
    client = auth.client
    res = (
        client.table("papers")
        .select("*")
        .eq("id", str(paper_id))
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Paper not found")
    return {"paper": res.data[0]}

@summary_router.get('/{paper_id}/summary')
def get_paper_summary(
    paper_id: UUID,
    auth: AuthContext = Depends(get_auth_context),
):
    client = auth.client
    summary = _get_existing_summary(client, str(paper_id))
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return {"summary":summary}

@summary_router.post('/{paper_id}/summary')
def generate_paper_summary(
    paper_id: UUID,
    request: SummaryGenerationRequest | None = None,
    auth: AuthContext = Depends(get_auth_context),
    ):
    client = auth.client
    options = request or SummaryGenerationRequest()
    paper_id_str = str(paper_id)
    existing = _get_existing_summary(client, paper_id_str)
    if _should_use_existing_summary(existing, options):
        return {"summary": existing, "generated": False, "stored": True}
    return _generate_and_store_summary(client, paper_id_str, options)

@summary_router.post("/{paper_id}/summary/regenerate")
def regenerate_paper_summary(
    paper_id: UUID,
    request: SummaryGenerationRequest | None = None,
    auth: AuthContext = Depends(get_auth_context),
):
    client = auth.client
    options = request or SummaryGenerationRequest()
    return _generate_and_store_summary(client, str(paper_id), options)

def _generate_and_store_summary(
    client,
    paper_id:str,
    options: SummaryGenerationRequest,
):
    paper = _get_paper(client, paper_id)
    try: 
        generated = _generate_summary_for_paper(paper, options)
    except MissingPaperContentError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SummaryConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except SummaryProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    row = {
        "paper_id": paper_id,
        "summary_text": generated.summary_text,
        "summary_status": "completed",
        "llm_provider": generated.llm_provider,
        "llm_model": generated.llm_model,
        "prompt_version": generated.prompt_version,
        "error_message": None,
    }

    res=(
        client.table("paper_summaries")
        .upsert(row, on_conflict="paper_id")
        .execute()
    )

    summary = res.data[0] if res.data else _get_existing_summary(client,paper_id)
    return {"summary":summary, "generated": True, "stored": True}


def _get_paper(client, paper_id:str):
    res = (
        client.table("papers")
        .select("id,title,abstract,pdf_url,source_url")
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


def _generate_summary_for_paper(paper: dict, options: SummaryGenerationRequest):
    custom_instructions = _clean_custom_instructions(options.custom_instructions)

    if options.use_pdf_sections:
        try:
            pdf_bytes = fetch_pdf_bytes(paper.get("pdf_url"))
            sections = extract_pdf_sections(pdf_bytes)
            return generate_section_summary_text(
                title=paper["title"],
                sections=sections,
                custom_instructions=custom_instructions,
            )
        except (PdfFetchError, PdfExtractionError) as exc:
            if not options.fallback_to_abstract:
                raise MissingPaperContentError(
                    f"PDF section summary unavailable: {exc}"
                ) from exc

    return generate_summary_text(
        title=paper["title"],
        abstract=paper.get("abstract"),
        custom_instructions=custom_instructions,
    )


def _should_use_existing_summary(
    existing_summary: dict | None,
    options: SummaryGenerationRequest,
) -> bool:
    if not existing_summary or options.force_regenerate:
        return False
    if _clean_custom_instructions(options.custom_instructions):
        return False

    expected_prompt_version = (
        SECTION_PROMPT_VERSION if options.use_pdf_sections else PROMPT_VERSION
    )
    return existing_summary.get("prompt_version") == expected_prompt_version


def _clean_custom_instructions(custom_instructions: str | None) -> str | None:
    if not custom_instructions or not custom_instructions.strip():
        return None
    return custom_instructions.strip()[:2000]


# [GenAI Usage] LLM response end
# [GenAI Reflection] I asked Codex to restore the summary persistence path while keeping the implementation aligned with the existing FastAPI router and Supabase RLS authentication pattern. I reviewed that the endpoint first checks for an existing matching summary, only calls the LLM when needed, extracts bounded PDF sections before prompting, saves the generated response with model and prompt metadata, supports custom prompt instructions, and returns whether the result was newly generated or retrieved from storage.

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.services.pdf_sections import (
    PaperSection,
    PdfExtractionError,
    PdfFetchError,
    extract_pdf_visual_assets,
    extract_pdf_sections,
    fetch_pdf_bytes,
)
from app.services.llm_summary import (
    MissingPaperContentError,
    SummaryConfigurationError,
    SummaryProviderError,
    generate_video_slide_plan,
    generate_section_summary_text,
    generate_summary_text,
)
from app.services.summary_prompt import PROMPT_VERSION, SECTION_PROMPT_VERSION
from app.services.video_summary import (
    DEFAULT_OUTPUT_ROOT,
    VideoSummaryError,
    create_video_summary_artifacts,
)
from app.supabase.auth import AuthContext, get_auth_context

summary_router = APIRouter(prefix="/papers",tags=["paper summaries"])

class SummaryGenerationRequest(BaseModel):
    custom_instructions: str | None = None
    force_regenerate: bool = False
    use_pdf_sections: bool = True
    fallback_to_abstract: bool = True


class VideoSummaryRequest(BaseModel):
    custom_instructions: str | None = None
    video_instructions: str | None = None
    force_regenerate_summary: bool = False
    use_pdf_sections: bool = True
    fallback_to_abstract: bool = True
    slide_duration_seconds: int = 8
    include_voiceover: bool = True


#[GenAI Usage] Prompt: Restore persistent paper-summary caching for the Team 3 summary MVP and then extend it to summarize papers by PDF section. 
# The implementation should use the existing authenticated Supabase client, check whether a matching summary already exists for a paper, 
# fetch and extract paper PDF sections when available, allow optional caller-provided summary instructions, fall back to abstract-based summaries when configured, 
# save generated summaries to the paper_summaries table, and return a consistent JSON response for generated and cached summaries.
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

#[GenAI Usage] Prompt: implement the video summary functionality. Make it similar to text summary, but instead use a python package that directly creates presentation slides, . Write the script with timestamps. Then play the slides with the timestamps and render a video.
#[GenAI Usage] LLM response begins

@summary_router.post("/{paper_id}/video-summary")
def generate_paper_video_summary(
    paper_id: UUID,
    request: VideoSummaryRequest | None = None,
    auth: AuthContext = Depends(get_auth_context),
):
    client = auth.client
    options = request or VideoSummaryRequest()
    paper_id_str = str(paper_id)
    paper = _get_paper(client, paper_id_str)

    summary_options = SummaryGenerationRequest(
        custom_instructions=options.custom_instructions,
        force_regenerate=options.force_regenerate_summary,
        use_pdf_sections=options.use_pdf_sections,
        fallback_to_abstract=options.fallback_to_abstract,
    )
    existing = _get_existing_summary(client, paper_id_str)
    if _should_use_existing_summary(existing, summary_options):
        summary = existing
        summary_generated = False
    else:
        summary_response = _generate_and_store_summary(
            client,
            paper_id_str,
            summary_options,
        )
        summary = summary_response["summary"]
        summary_generated = bool(summary_response.get("generated"))

    try:
        sections, image_assets = _prepare_video_source_material(
            paper=paper,
            options=options,
            paper_id=paper_id_str,
            summary_text=summary["summary_text"],
        )
        slide_plan = generate_video_slide_plan(
            title=paper["title"],
            sections=sections,
            image_assets=image_assets,
            video_instructions=options.video_instructions,
        )
        video_summary = create_video_summary_artifacts(
            paper_id=paper_id_str,
            title=paper["title"],
            summary_text=summary["summary_text"],
            slide_plan=slide_plan.slides,
            image_assets=image_assets,
            video_instructions=options.video_instructions,
            slide_duration_seconds=options.slide_duration_seconds,
            include_voiceover=options.include_voiceover,
        )
    except MissingPaperContentError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SummaryConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except SummaryProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except VideoSummaryError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "summary": summary,
        "summary_generated": summary_generated,
        "slide_plan": {
            "llm_provider": slide_plan.llm_provider,
            "llm_model": slide_plan.llm_model,
            "prompt_version": slide_plan.prompt_version,
            "visual_asset_count": len(image_assets),
        },
        "video_summary": video_summary.to_dict(),
    }


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


def _prepare_video_source_material(
    *,
    paper: dict,
    options: VideoSummaryRequest,
    paper_id: str,
    summary_text: str,
) -> tuple[list[PaperSection], list]:
    sections: list[PaperSection] = []
    image_assets = []

    if options.use_pdf_sections:
        try:
            pdf_bytes = fetch_pdf_bytes(paper.get("pdf_url"))
            sections = extract_pdf_sections(pdf_bytes)
            image_assets = extract_pdf_visual_assets(
                pdf_bytes,
                DEFAULT_OUTPUT_ROOT / paper_id / "assets",
            )
        except PdfFetchError as exc:
            if not options.fallback_to_abstract:
                raise MissingPaperContentError(
                    f"PDF video source material unavailable: {exc}"
                ) from exc
        except PdfExtractionError as exc:
            if "pymupdf is not installed" in str(exc).lower():
                raise VideoSummaryError(str(exc)) from exc
            if not options.fallback_to_abstract:
                raise MissingPaperContentError(
                    f"PDF video source material unavailable: {exc}"
                ) from exc

    if not sections:
        sections = [PaperSection(heading="Generated Summary", text=summary_text)]

    return sections, image_assets


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

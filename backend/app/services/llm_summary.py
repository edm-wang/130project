import os
import json
from dataclasses import dataclass

from openai import OpenAI, OpenAIError

from app.services.summary_prompt import (
    PROMPT_VERSION,
    SECTION_PROMPT_VERSION,
    VIDEO_SLIDE_PLAN_PROMPT_VERSION,
    build_paper_summary_prompt,
    build_section_summary_prompt,
    build_video_slide_plan_prompt,
)

MAX_ABSTRACT_CHARS = 12000
DEFAULT_LLM_MODEL = "gpt-4o-mini"
DEFAULT_LLM_INSTRUCTIONS = "You summarize research papers clearly and concisely. Return only the summary."
SLIDE_PLAN_LLM_INSTRUCTIONS = "You design concise research paper explainer slides. Return only valid JSON."

#[GenAI Usage] Prompt: Extend the LLM summary service so it can generate either abstract-based summaries or section-by-section summaries from extracted PDF sections, 
# while preserving the existing OpenAI integration, model metadata, prompt version metadata, and error handling behavior.
#[GenAI Usage] LLM response begins

class SummaryGenerationError(Exception):
    pass
class MissingPaperContentError(SummaryGenerationError):
    pass
class SummaryConfigurationError(SummaryGenerationError):
    pass
class SummaryProviderError(SummaryGenerationError):
    pass

@dataclass(frozen=True)
class GeneratedSummary:
    summary_text: str
    llm_provider: str
    llm_model: str
    prompt_version: str


@dataclass(frozen=True)
class GeneratedVideoSlidePlan:
    slides: list[dict]
    llm_provider: str
    llm_model: str
    prompt_version: str

def generate_summary_text(
    title: str,
    abstract: str | None,
    custom_instructions: str | None = None,
) -> GeneratedSummary:
    if not title or not title.strip():
        raise MissingPaperContentError("Paper title is missing.")
    clean_abstract = normalize_abstract(abstract)
    prompt = build_paper_summary_prompt(
        title.strip(),
        clean_abstract,
        custom_instructions,
    )
    model = os.getenv("LLM_MODEL", DEFAULT_LLM_MODEL)

    return GeneratedSummary(
        summary_text = call_llm_provider(prompt, model),
        llm_provider="openai",
        llm_model = model,
        prompt_version = PROMPT_VERSION,
    )


def generate_section_summary_text(
    title: str,
    sections,
    custom_instructions: str | None = None,
) -> GeneratedSummary:
    if not title or not title.strip():
        raise MissingPaperContentError("Paper title is missing.")
    if not sections:
        raise MissingPaperContentError("Paper PDF sections are missing.")

    prompt = build_section_summary_prompt(
        title.strip(),
        sections,
        custom_instructions,
    )
    model = os.getenv("LLM_MODEL", DEFAULT_LLM_MODEL)

    return GeneratedSummary(
        summary_text=call_llm_provider(prompt, model),
        llm_provider="openai",
        llm_model=model,
        prompt_version=SECTION_PROMPT_VERSION,
    )


#[GenAI Usage] Prompt: prompt the LLM to generate slides given raw text and images from the PDF
#[GenAI Usage] LLM response begins

def generate_video_slide_plan(
    title: str,
    sections,
    image_assets,
    video_instructions: str | None = None,
) -> GeneratedVideoSlidePlan:
    if not title or not title.strip():
        raise MissingPaperContentError("Paper title is missing.")

    prompt = build_video_slide_plan_prompt(
        title=title.strip(),
        sections=sections,
        image_assets=image_assets,
        video_instructions=video_instructions,
    )
    model = os.getenv("LLM_MODEL", DEFAULT_LLM_MODEL)
    raw_slide_plan = call_llm_provider(
        prompt,
        model,
        instructions=SLIDE_PLAN_LLM_INSTRUCTIONS,
    )

    return GeneratedVideoSlidePlan(
        slides=_parse_slide_plan_json(raw_slide_plan),
        llm_provider="openai",
        llm_model=model,
        prompt_version=VIDEO_SLIDE_PLAN_PROMPT_VERSION,
    )


def normalize_abstract(abstract:str|None)->str:
    if not abstract or not abstract.strip():
        raise MissingPaperContentError("Paper abstract is missing.")
    return abstract.strip()[:MAX_ABSTRACT_CHARS]

def call_llm_provider(
    prompt: str,
    model: str,
    instructions: str = DEFAULT_LLM_INSTRUCTIONS,
) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SummaryConfigurationError("api key is not configured")
    try:
        client = OpenAI(api_key = api_key)
        response = client.responses.create(
            model=model,
            instructions=instructions,
            input=prompt,
        )
    except OpenAIError as exc:
        raise SummaryProviderError("LLM summary generation failed.") from exc
    summary = response.output_text.strip()
    if not summary:
        raise SummaryProviderError("LLM returned an empty summary")
    return summary


def _parse_slide_plan_json(raw_slide_plan: str) -> list[dict]:
    try:
        data = json.loads(_extract_json_object(raw_slide_plan))
    except json.JSONDecodeError as exc:
        raise SummaryProviderError("LLM returned an invalid slide plan.") from exc

    slides = data.get("slides")
    if not isinstance(slides, list) or not slides:
        raise SummaryProviderError("LLM slide plan did not include slides.")

    cleaned_slides = []
    for slide in slides[:8]:
        if not isinstance(slide, dict):
            continue
        title = str(slide.get("title") or "").strip()
        narration = str(slide.get("narration") or "").strip()
        bullets = slide.get("bullets") or []
        if not title or not narration or not isinstance(bullets, list):
            continue
        cleaned_slides.append(slide)

    if not cleaned_slides:
        raise SummaryProviderError("LLM slide plan did not include usable slides.")
    return cleaned_slides


def _extract_json_object(raw_text: str) -> str:
    clean_text = raw_text.strip()
    if clean_text.startswith("```"):
        clean_text = clean_text.strip("`")
        if clean_text.lower().startswith("json"):
            clean_text = clean_text[4:].strip()

    start = clean_text.find("{")
    end = clean_text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return clean_text
    return clean_text[start:end + 1]

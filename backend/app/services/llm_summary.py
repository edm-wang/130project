import os
from dataclasses import dataclass

from openai import OpenAI, OpenAIError

from app.services.summary_prompt import (
    PROMPT_VERSION,
    SECTION_PROMPT_VERSION,
    build_paper_summary_prompt,
    build_section_summary_prompt,
)

MAX_ABSTRACT_CHARS = 12000
DEFAULT_LLM_MODEL = "gpt-4o-mini"

#[GenAI Usage] Prompt: Extend the LLM summary service so it can generate either abstract-based summaries or section-by-section summaries from extracted PDF sections, while preserving the existing OpenAI integration, model metadata, prompt version metadata, and error handling behavior.
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


def normalize_abstract(abstract:str|None)->str:
    if not abstract or not abstract.strip():
        raise MissingPaperContentError("Paper abstract is missing.")
    return abstract.strip()[:MAX_ABSTRACT_CHARS]

def call_llm_provider(prompt:str,model: str)->str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SummaryConfigurationError("api key is not configured")
    try:
        client = OpenAI(api_key = api_key)
        response = client.responses.create(
            model=model,
            instructions=(
                "You summarize research papers clearly and concisely. "
                "Return only the summary."
            ),
            input=prompt,
        )
    except OpenAIError as exc:
        raise SummaryProviderError("LLM summary generation failed.") from exc
    summary = response.output_text.strip()
    if not summary:
        raise SummaryProviderError("LLM returned an empty summary")
    return summary

# [GenAI Usage] LLM response end
# [GenAI Reflection] I asked Codex to preserve the existing OpenAI call wrapper and add a section-summary path without coupling this service to PDF fetching. I reviewed that both generation functions return the same GeneratedSummary metadata shape and route provider/configuration errors through the existing exception classes.

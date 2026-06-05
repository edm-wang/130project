# Don't delete comments below
# [GenAI Usage 1] Codex Prompt
# Please add a focused opt-in live integration test file for the newer Team 3 LLM service helpers.
# These tests should use the real OpenAI key but should not touch Supabase. Cover section-based
# summary generation and video slide-plan generation with small synthetic paper sections, and assert
# stable contract details like provider metadata, prompt versions, non-empty summary text, and usable
# slide-plan fields. Keep the tests behind RUN_LIVE_LLM_TESTS=1 so normal runs do not spend API calls.
# [GenAI Usage 1] Response begins:

import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[1]
SUPABASE_ENV_PATH = BACKEND_DIR / "app" / "supabase" / ".env"
sys.path.insert(0, str(BACKEND_DIR))
load_dotenv(SUPABASE_ENV_PATH)
load_dotenv()

from app.services.llm_summary import (  # noqa: E402
    generate_section_summary_text,
    generate_video_slide_plan,
)
from app.services.pdf_sections import PaperSection, PdfImageAsset  # noqa: E402
from app.services.summary_prompt import (  # noqa: E402
    SECTION_PROMPT_VERSION,
    VIDEO_SLIDE_PLAN_PROMPT_VERSION,
)


def require_live_llm_tests():
    if os.getenv("RUN_LIVE_LLM_TESTS") != "1":
        pytest.skip("Set RUN_LIVE_LLM_TESTS=1 to run live OpenAI LLM tests")
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY is required for live OpenAI LLM tests")


def test_generate_section_summary_text_live_openai_returns_metadata_and_content():
    require_live_llm_tests()

    generated = generate_section_summary_text(
        title="Live Section Summary Integration Paper",
        sections=[
            PaperSection(
                heading="Introduction",
                text=(
                    "The paper studies how retrieval quality affects researcher-facing "
                    "recommendation systems and motivates concise AI summaries."
                ),
            ),
            PaperSection(
                heading="Results",
                text=(
                    "The evaluation reports that embedding-based retrieval improves the "
                    "ranking of relevant papers over a keyword-only baseline."
                ),
            ),
        ],
        custom_instructions="Mention the main method and the main result.",
    )

    assert generated.llm_provider == "openai"
    assert generated.prompt_version == SECTION_PROMPT_VERSION
    assert generated.llm_model
    assert len(generated.summary_text.strip()) > 80
    assert "retrieval" in generated.summary_text.lower()


def test_generate_video_slide_plan_live_openai_returns_usable_slides():
    require_live_llm_tests()

    generated = generate_video_slide_plan(
        title="Live Video Slide Plan Integration Paper",
        sections=[
            PaperSection(
                heading="Problem",
                text=(
                    "Researchers need a quick way to understand why a recommended paper "
                    "is relevant before deciding whether to read it."
                ),
            ),
            PaperSection(
                heading="Method",
                text=(
                    "The system combines paper summaries, user interests, and short "
                    "visual explanations into a compact explainer video."
                ),
            ),
            PaperSection(
                heading="Evaluation",
                text=(
                    "A small qualitative evaluation checks whether the generated slides "
                    "are concise, grounded, and easy to follow."
                ),
            ),
        ],
        image_assets=[
            PdfImageAsset(
                index=1,
                label="Figure 1: System overview",
                path="/tmp/live-video-plan-figure.png",
                page_number=2,
                kind="embedded_image",
                nearby_text="Figure 1 shows the summary and recommendation pipeline.",
                description="A system diagram connecting interests, papers, summaries, and video output.",
            )
        ],
        video_instructions="Use simple language for a student demo audience.",
    )

    assert generated.llm_provider == "openai"
    assert generated.prompt_version == VIDEO_SLIDE_PLAN_PROMPT_VERSION
    assert generated.llm_model
    assert 1 <= len(generated.slides) <= 8
    first_slide = generated.slides[0]
    assert first_slide["title"].strip()
    assert first_slide["narration"].strip()
    assert isinstance(first_slide["bullets"], list)
    assert first_slide["bullets"]


# [GenAI Usage 1] Response ends
# [GenAI Usage] Reflection
# I used Codex to add live OpenAI service tests for the newer section-summary and video slide-plan
# helpers without adding Supabase or rendering dependencies. This gives Person 6 direct QA coverage
# for the generated AI outputs while keeping the test contract stable: metadata, prompt version,
# non-empty grounded content, and usable slide fields. The tests stay opt-in because they spend real
# OpenAI calls and may vary slightly in wording across runs.

# Don't delete comments below
# [GenAI Usage 1] Codex Prompt
# Please add the next small Person 6 TDD slice for the new video-summary route, but keep it in a
# separate test file so the paper-summary route tests stay readable. Keep the tests route-level,
# mocked, and offline: do not render a real video, call OpenAI, call Supabase Storage, or fetch a
# real PDF. Focus on demo-critical QA behavior for the AI video flow: cached summary reuse,
# extracted PDF sections and visuals being passed into the slide planner, artifact response shape,
# and clear HTTP mapping when the slide planner, video artifact creation, or required PDF source
# material fails.
# [GenAI Usage 1] Response begins:

import os
import sys
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_PUBLISHABLE_KEY", "test-key")

from app.routers import paper_summaries  # noqa: E402
from app.services.llm_summary import GeneratedVideoSlidePlan, SummaryProviderError  # noqa: E402
from app.services.pdf_sections import (  # noqa: E402
    PaperSection,
    PdfFetchError,
    PdfImageAsset,
)
from app.services.summary_prompt import (  # noqa: E402
    PROMPT_VERSION,
    SECTION_PROMPT_VERSION,
    VIDEO_SLIDE_PLAN_PROMPT_VERSION,
)
from app.services.video_summary import VideoSummaryError  # noqa: E402
from app.supabase.auth import AuthContext, get_auth_context  # noqa: E402


class FakeUser:
    def __init__(self):
        self.id = str(uuid4())
        self.email = "video-summary-route-test@example.com"


class FakeQuery:
    def __init__(self, rows):
        self.rows = rows
        self.filters = {}

    def select(self, *_args):
        return self

    def eq(self, field, value):
        self.filters[field] = value
        return self

    def limit(self, *_args):
        return self

    def execute(self):
        data = [
            row
            for row in self.rows
            if all(str(row.get(field)) == str(value) for field, value in self.filters.items())
        ]
        return type("FakeResponse", (), {"data": data})()


class FakeSupabaseClient:
    def __init__(self, papers=None, summaries=None):
        self.tables = {
            "papers": papers or [],
            "paper_summaries": summaries or [],
        }

    def table(self, table_name):
        return FakeQuery(self.tables[table_name])


class FakeVideoSummaryArtifact:
    def to_dict(self):
        return {
            "output_dir": "https://storage.example/video_summaries/paper/",
            "video_path": "https://storage.example/video_summaries/paper/video.mp4",
            "pptx_path": "https://storage.example/video_summaries/paper/slides.pptx",
            "script_path": "https://storage.example/video_summaries/paper/script.txt",
            "slide_image_paths": [
                "https://storage.example/video_summaries/paper/frame_001.png"
            ],
            "slides": [{"title": "Problem"}],
        }


def make_test_client(fake_client):
    app = FastAPI()
    app.include_router(paper_summaries.summary_router)
    app.dependency_overrides[get_auth_context] = lambda: AuthContext(
        user=FakeUser(),
        access_token="pytest-token",
        client=fake_client,
    )
    return TestClient(app, raise_server_exceptions=False)


def test_generate_video_summary_returns_artifact_response_with_cached_summary(monkeypatch):
    paper_id = str(uuid4())
    image_asset = PdfImageAsset(
        index=1,
        label="Figure 1",
        path="/tmp/figure_1.png",
        page_number=1,
        kind="embedded_image",
        nearby_text="Figure 1 shows the retrieval pipeline.",
        description="A diagram of the retrieval pipeline.",
    )
    client = make_test_client(
        FakeSupabaseClient(
            papers=[
                {
                    "id": paper_id,
                    "title": "Video Paper",
                    "abstract": "Video abstract.",
                    "pdf_url": "https://example.com/video-paper.pdf",
                }
            ],
            summaries=[
                {
                    "paper_id": paper_id,
                    "summary_text": "Cached section summary.",
                    "llm_provider": "openai",
                    "llm_model": "gpt-4o-mini",
                    "prompt_version": SECTION_PROMPT_VERSION,
                }
            ],
        )
    )

    def fake_fetch_pdf_bytes(pdf_url):
        assert pdf_url == "https://example.com/video-paper.pdf"
        return b"%PDF video"

    def fake_extract_pdf_sections(pdf_bytes):
        assert pdf_bytes == b"%PDF video"
        return [PaperSection(heading="Method", text="The method uses retrieval.")]

    def fake_extract_pdf_visual_assets(pdf_bytes, output_dir):
        assert pdf_bytes == b"%PDF video"
        assert str(output_dir).endswith(f"{paper_id}/assets")
        return [image_asset]

    def fake_generate_video_slide_plan(
        title,
        sections,
        image_assets,
        video_instructions=None,
    ):
        assert title == "Video Paper"
        assert sections[0].heading == "Method"
        assert image_assets == [image_asset]
        assert video_instructions == "keep it visual"
        return GeneratedVideoSlidePlan(
            slides=[
                {
                    "title": "Problem",
                    "bullets": ["Need better retrieval"],
                    "narration": "The paper studies retrieval quality.",
                    "subtitle": "Retrieval quality",
                    "visual_asset_index": 1,
                }
            ],
            llm_provider="openai",
            llm_model="pytest-video-model",
            prompt_version=VIDEO_SLIDE_PLAN_PROMPT_VERSION,
        )

    def fake_create_video_summary_artifacts(**kwargs):
        assert kwargs["paper_id"] == paper_id
        assert kwargs["title"] == "Video Paper"
        assert kwargs["summary_text"] == "Cached section summary."
        assert kwargs["slide_plan"][0]["title"] == "Problem"
        assert kwargs["image_assets"] == [image_asset]
        assert kwargs["video_instructions"] == "keep it visual"
        assert kwargs["slide_duration_seconds"] == 6
        assert kwargs["include_voiceover"] is False
        return FakeVideoSummaryArtifact()

    monkeypatch.setattr(paper_summaries, "fetch_pdf_bytes", fake_fetch_pdf_bytes)
    monkeypatch.setattr(paper_summaries, "extract_pdf_sections", fake_extract_pdf_sections)
    monkeypatch.setattr(
        paper_summaries,
        "extract_pdf_visual_assets",
        fake_extract_pdf_visual_assets,
    )
    monkeypatch.setattr(
        paper_summaries,
        "generate_video_slide_plan",
        fake_generate_video_slide_plan,
    )
    monkeypatch.setattr(
        paper_summaries,
        "create_video_summary_artifacts",
        fake_create_video_summary_artifacts,
    )

    response = client.post(
        f"/papers/{paper_id}/video-summary",
        json={
            "video_instructions": "keep it visual",
            "slide_duration_seconds": 6,
            "include_voiceover": False,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["summary_generated"] is False
    assert body["summary"]["summary_text"] == "Cached section summary."
    assert body["slide_plan"]["llm_model"] == "pytest-video-model"
    assert body["slide_plan"]["prompt_version"] == VIDEO_SLIDE_PLAN_PROMPT_VERSION
    assert body["slide_plan"]["visual_asset_count"] == 1
    assert body["video_summary"]["video_path"].endswith("/video.mp4")


def test_generate_video_summary_maps_slide_plan_provider_error_to_502(monkeypatch):
    paper_id = str(uuid4())
    client = make_test_client(
        FakeSupabaseClient(
            papers=[
                {
                    "id": paper_id,
                    "title": "Video Paper",
                    "abstract": "Video abstract.",
                    "pdf_url": "https://example.com/video-paper.pdf",
                }
            ],
            summaries=[
                {
                    "paper_id": paper_id,
                    "summary_text": "Cached section summary.",
                    "prompt_version": SECTION_PROMPT_VERSION,
                }
            ],
        )
    )

    monkeypatch.setattr(paper_summaries, "fetch_pdf_bytes", lambda _url: b"%PDF video")
    monkeypatch.setattr(
        paper_summaries,
        "extract_pdf_sections",
        lambda _pdf_bytes: [PaperSection(heading="Method", text="Method text.")],
    )
    monkeypatch.setattr(paper_summaries, "extract_pdf_visual_assets", lambda *_args: [])

    def fake_generate_video_slide_plan(*_args, **_kwargs):
        raise SummaryProviderError("LLM returned an invalid slide plan.")

    monkeypatch.setattr(
        paper_summaries,
        "generate_video_slide_plan",
        fake_generate_video_slide_plan,
    )

    response = client.post(
        f"/papers/{paper_id}/video-summary",
        json={"include_voiceover": False},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "LLM returned an invalid slide plan."


def test_generate_video_summary_maps_artifact_error_to_500(monkeypatch):
    paper_id = str(uuid4())
    client = make_test_client(
        FakeSupabaseClient(
            papers=[
                {
                    "id": paper_id,
                    "title": "Video Paper",
                    "abstract": "Video abstract.",
                }
            ],
            summaries=[
                {
                    "paper_id": paper_id,
                    "summary_text": "Cached abstract summary.",
                    "prompt_version": PROMPT_VERSION,
                }
            ],
        )
    )

    monkeypatch.setattr(
        paper_summaries,
        "generate_video_slide_plan",
        lambda *_args, **_kwargs: GeneratedVideoSlidePlan(
            slides=[
                {
                    "title": "Problem",
                    "bullets": ["Need better retrieval"],
                    "narration": "The paper studies retrieval quality.",
                    "subtitle": "Retrieval quality",
                }
            ],
            llm_provider="openai",
            llm_model="pytest-video-model",
            prompt_version=VIDEO_SLIDE_PLAN_PROMPT_VERSION,
        ),
    )

    def fake_create_video_summary_artifacts(**_kwargs):
        raise VideoSummaryError("Supabase Storage upload failed for video_summary.mp4.")

    monkeypatch.setattr(
        paper_summaries,
        "create_video_summary_artifacts",
        fake_create_video_summary_artifacts,
    )

    response = client.post(
        f"/papers/{paper_id}/video-summary",
        json={"use_pdf_sections": False, "include_voiceover": False},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Supabase Storage upload failed for video_summary.mp4."
    )


def test_generate_video_summary_can_require_pdf_source_material(monkeypatch):
    paper_id = str(uuid4())
    client = make_test_client(
        FakeSupabaseClient(
            papers=[
                {
                    "id": paper_id,
                    "title": "Video Paper",
                    "abstract": "Video abstract.",
                    "pdf_url": "https://example.com/missing-video.pdf",
                }
            ],
            summaries=[
                {
                    "paper_id": paper_id,
                    "summary_text": "Cached section summary.",
                    "prompt_version": SECTION_PROMPT_VERSION,
                }
            ],
        )
    )

    def fake_fetch_pdf_bytes(_pdf_url):
        raise PdfFetchError("PDF download failed.")

    monkeypatch.setattr(paper_summaries, "fetch_pdf_bytes", fake_fetch_pdf_bytes)

    response = client.post(
        f"/papers/{paper_id}/video-summary",
        json={"fallback_to_abstract": False, "include_voiceover": False},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "PDF video source material unavailable: PDF download failed."
    )


# [GenAI Usage 1] Response ends
# [GenAI Usage] Reflection
# I used Codex for a focused Person 6 QA slice around the video-summary route. The tests stay
# offline by mocking every expensive or external boundary: PDF fetch/extraction, the slide-plan LLM,
# video rendering, voiceover, and Supabase Storage. This keeps the tests stable while still covering
# the demo-critical behavior: successful artifact response shape and clear failure status codes.

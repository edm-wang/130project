
PROMPT_VERSION = "paper_summary_v1"
SECTION_PROMPT_VERSION = "paper_section_summary_v1"
VIDEO_SLIDE_PLAN_PROMPT_VERSION = "video_slide_plan_v1"

#[GenAI Usage] Prompt: Extend the paper summary prompt layer so it can support both abstract-based summaries and PDF section-based summaries, 
# while also allowing optional caller-provided instructions to customize the generated summary format or focus.
#[GenAI Usage] LLM response begins

def build_paper_summary_prompt(
    title: str,
    abstract:str,
    custom_instructions: str | None = None,
) -> str:
    customization = _format_custom_instructions(custom_instructions)
    return f"""
summarize this research paper for a researcher. 

Title: {title}

Abstract:
{abstract}

Write 3-5 concise bullet points for TL;DR. Focus on:
- the main problem this paper is trying to solve
- the method
- experiment setup and the key result
- why it matters
{customization}
""".strip()


def build_section_summary_prompt(
    title: str,
    sections,
    custom_instructions: str | None = None,
) -> str:
    section_blocks = "\n\n".join(
        f"Section: {section.heading}\n{section.text}"
        for section in sections
    )
    customization = _format_custom_instructions(custom_instructions)

    return f"""
Summarize this research paper section by section for a researcher.

Title: {title}

Paper Sections:
{section_blocks}

Return a concise markdown summary with these headings:
1. Overall TL;DR
2. Section-by-section Summary
3. Key Takeaways

For each section, explain the section's purpose, main technical content, and most important finding or claim.
{customization}
""".strip()


#[GenAI Usage] Prompt: prompt the LLM to generate slides given raw text and images from the PDF
#[GenAI Usage] LLM response begins

def build_video_slide_plan_prompt(
    title: str,
    sections,
    image_assets,
    video_instructions: str | None = None,
) -> str:
    section_blocks = _format_video_sections(sections)
    image_blocks = _format_video_image_assets(image_assets)
    customization = _format_custom_instructions(video_instructions)

    return f"""
Create a concise visual slide plan for a short research-paper explainer video.

Title: {title}

Paper sections:
{section_blocks}

Available PDF visuals:
{image_blocks}

Return only valid JSON with this exact top-level shape:
{{
  "slides": [
    {{
      "title": "short slide title",
      "bullets": ["one compact claim", "one supporting detail"],
      "narration": "one spoken paragraph for this slide",
      "subtitle": "short subtitle text for captions",
      "visual_asset_index": 1,
      "visual_caption": "short caption for the chosen visual",
      "visual_reason": "why this visual belongs on the slide",
      "duration_seconds": 8
    }}
  ]
}}

Slide rules:
- Make 5 to 7 slides.
- Use a different purpose for each slide: problem, core idea, method, evidence, limitations, and takeaway.
- Keep each slide visual-first: choose a visual_asset_index when useful, and keep text sparse.
- Use at most 3 bullets per slide, with each bullet under 16 words.
- Do not copy dense paper text verbatim.
- Narration should explain the slide clearly for someone who has not read the paper.
- Subtitles should be shorter than narration and suitable for frontend timed captions.
{customization}
""".strip()


def _format_custom_instructions(custom_instructions: str | None) -> str:
    if not custom_instructions or not custom_instructions.strip():
        return ""

    return f"""

Additional user instructions:
{custom_instructions.strip()}
""".rstrip()


def _format_video_sections(sections) -> str:
    if not sections:
        return "No extracted PDF sections were available."

    blocks = []
    for section in list(sections)[:7]:
        section_text = " ".join((section.text or "").split())[:1800]
        blocks.append(f"Section: {section.heading}\n{section_text}")
    return "\n\n".join(blocks)


def _format_video_image_assets(image_assets) -> str:
    if not image_assets:
        return "No PDF visuals were extracted. Create text-light slides without visual_asset_index values."

    blocks = []
    for asset in list(image_assets)[:8]:
        description = getattr(asset, "description", "") or getattr(asset, "nearby_text", "")
        blocks.append(
            "\n".join(
                [
                    f"Index: {asset.index}",
                    f"Label: {asset.label}",
                    f"Page: {asset.page_number}",
                    f"Type: {asset.kind}",
                    f"Description: {description}",
                ]
            )
        )
    return "\n\n".join(blocks)

# [GenAI Usage] LLM response end

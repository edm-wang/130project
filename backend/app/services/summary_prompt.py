
PROMPT_VERSION = "paper_summary_v1"
SECTION_PROMPT_VERSION = "paper_section_summary_v1"

#[GenAI Usage] Prompt: the code below is the result of a conversation with Codex. The request was to extend the paper summary prompt layer so it can support both abstract-based summaries and PDF section-based summaries, while also allowing optional caller-provided instructions to customize the generated summary format or focus.
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


def _format_custom_instructions(custom_instructions: str | None) -> str:
    if not custom_instructions or not custom_instructions.strip():
        return ""

    return f"""

Additional user instructions:
{custom_instructions.strip()}
""".rstrip()

# [GenAI Usage] LLM response end
# [GenAI Reflection] I asked Codex to keep the prompt builders small and explicit. I reviewed that the abstract prompt keeps the original behavior, the section prompt asks for structured markdown output, and custom instructions are appended only when the caller provides non-empty text.

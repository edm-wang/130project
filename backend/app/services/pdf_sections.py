from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


MAX_PDF_BYTES = 15 * 1024 * 1024
MAX_PDF_PAGES = 40
MAX_SECTION_CHARS = 5000
MAX_TOTAL_SECTION_CHARS = 24000


#[GenAI Usage] Prompt: the code below is the result of a conversation with Codex. The request was to add a controlled PDF-section extraction pipeline for paper summaries. The implementation should download a paper PDF from a trusted paper metadata URL, extract readable text with a Python PDF parser, split the extracted text into common research-paper sections, and return bounded section text suitable for an LLM summary prompt.
#[GenAI Usage] LLM response begins

class PdfFetchError(Exception):
    pass


class PdfExtractionError(Exception):
    pass


@dataclass(frozen=True)
class PaperSection:
    heading: str
    text: str


def fetch_pdf_bytes(
    pdf_url: str | None,
    *,
    timeout_seconds: int = 20,
    max_bytes: int = MAX_PDF_BYTES,
) -> bytes:
    if not pdf_url or not pdf_url.strip():
        raise PdfFetchError("Paper PDF URL is missing.")

    request = Request(
        pdf_url.strip(),
        headers={"User-Agent": "paper-summary-services/0.1"},
    )

    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            content_type = response.headers.get("Content-Type", "").lower()
            data = response.read(max_bytes + 1)
    except HTTPError as exc:
        raise PdfFetchError(f"PDF download failed with HTTP {exc.code}.") from exc
    except (TimeoutError, URLError, OSError) as exc:
        raise PdfFetchError("PDF download failed.") from exc

    if len(data) > max_bytes:
        raise PdfFetchError("PDF is too large to summarize.")

    if not data.startswith(b"%PDF") and "pdf" not in content_type:
        raise PdfFetchError("Downloaded file does not look like a PDF.")

    return data


def extract_pdf_sections(pdf_bytes: bytes, *, max_sections: int = 8) -> list[PaperSection]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise PdfExtractionError("pypdf is not installed.") from exc

    try:
        reader = PdfReader(BytesIO(pdf_bytes))
        page_texts = [
            page.extract_text() or ""
            for page in reader.pages[:MAX_PDF_PAGES]
        ]
    except Exception as exc:
        raise PdfExtractionError("PDF text extraction failed.") from exc

    full_text = _normalize_text("\n".join(page_texts))
    if not full_text:
        raise PdfExtractionError("PDF did not contain extractable text.")

    sections = _split_into_sections(full_text, max_sections=max_sections)
    if not sections:
        raise PdfExtractionError("No usable paper sections were extracted.")

    return _fit_section_budget(sections)


def _split_into_sections(text: str, *, max_sections: int) -> list[PaperSection]:
    matches = list(_section_heading_pattern().finditer(text))
    sections: list[PaperSection] = []

    for index, match in enumerate(matches):
        heading = _clean_heading(match.group("heading"))
        if heading.lower() in {"references", "bibliography", "acknowledgments"}:
            break

        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section_text = _normalize_text(text[start:end])
        if section_text:
            sections.append(PaperSection(heading=heading, text=section_text))

        if len(sections) >= max_sections:
            break

    if sections:
        return sections

    return [
        PaperSection(heading=f"Paper Body Part {index + 1}", text=chunk)
        for index, chunk in enumerate(_chunk_text(text, MAX_SECTION_CHARS))
    ][:max_sections]


def _fit_section_budget(sections: list[PaperSection]) -> list[PaperSection]:
    remaining = MAX_TOTAL_SECTION_CHARS
    budgeted_sections: list[PaperSection] = []

    for section in sections:
        if remaining <= 0:
            break
        text = section.text[: min(MAX_SECTION_CHARS, remaining)].strip()
        if text:
            budgeted_sections.append(PaperSection(section.heading, text))
            remaining -= len(text)

    return budgeted_sections


def _section_heading_pattern() -> re.Pattern:
    headings = [
        "abstract",
        "introduction",
        "background",
        "related work",
        "method",
        "methods",
        "methodology",
        "approach",
        "model",
        "experiments",
        "experimental setup",
        "results",
        "evaluation",
        "discussion",
        "limitations",
        "conclusion",
        "references",
        "bibliography",
        "acknowledgments",
    ]
    heading_alternatives = "|".join(re.escape(heading) for heading in headings)
    return re.compile(
        rf"(?im)^(?:\d+(?:\.\d+)*\.?\s+)?(?P<heading>{heading_alternatives})\b[^\n]{{0,80}}$"
    )


def _chunk_text(text: str, chunk_size: int) -> list[str]:
    return [
        text[index:index + chunk_size].strip()
        for index in range(0, len(text), chunk_size)
        if text[index:index + chunk_size].strip()
    ]


def _clean_heading(heading: str) -> str:
    return " ".join(word.capitalize() for word in heading.strip().split())


def _normalize_text(text: str) -> str:
    text = re.sub(r"-\s*\n\s*", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# [GenAI Usage] LLM response end
# [GenAI Reflection] I asked Codex to keep this PDF processing layer deterministic and bounded instead of making the LLM responsible for fetching files. I reviewed that the code validates PDF URLs, caps download size and page count, extracts text lazily through pypdf, detects common paper section headings, and falls back to body chunks when headings are unavailable.

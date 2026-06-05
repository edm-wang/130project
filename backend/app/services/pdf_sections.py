from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


MAX_PDF_BYTES = 15 * 1024 * 1024
MAX_PDF_PAGES = 40
MAX_SECTION_CHARS = 5000
MAX_TOTAL_SECTION_CHARS = 24000
MAX_VISUAL_ASSETS = 6
MIN_VISUAL_DIMENSION = 120
MAX_VISUAL_CONTEXT_CHARS = 900


#[GenAI Usage] Prompt: Add a controlled PDF-section extraction pipeline for paper summaries. 
# The implementation should download a paper PDF from a trusted paper metadata URL, extract readable text with a Python PDF parser, 
# split the extracted text into common research-paper sections, and return bounded section text suitable for an LLM summary prompt.
#[GenAI Usage] LLM response begins

class PdfFetchError(Exception):
    pass


class PdfExtractionError(Exception):
    pass


@dataclass(frozen=True)
class PaperSection:
    heading: str
    text: str


@dataclass(frozen=True)
class PdfImageAsset:
    index: int
    label: str
    path: str
    page_number: int
    kind: str
    nearby_text: str
    description: str


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


def extract_pdf_visual_assets(
    pdf_bytes: bytes,
    output_dir: Path,
    *,
    max_assets: int = MAX_VISUAL_ASSETS,
) -> list[PdfImageAsset]:
    try:
        import fitz
    except ImportError as exc:
        raise PdfExtractionError("pymupdf is not installed.") from exc

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        document = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:
        raise PdfExtractionError("PDF visual extraction failed.") from exc

    assets: list[PdfImageAsset] = []
    seen_xrefs: set[int] = set()

    try:
        page_count = min(len(document), MAX_PDF_PAGES)
        for page_index in range(page_count):
            if len(assets) >= max_assets:
                break
            page = document.load_page(page_index)
            page_text = _normalize_text(page.get_text("text") or "")
            context = _select_visual_context(page_text)

            for image_info in page.get_images(full=True):
                if len(assets) >= max_assets:
                    break
                xref = image_info[0]
                if xref in seen_xrefs:
                    continue
                seen_xrefs.add(xref)

                image_path = output_dir / f"visual_{len(assets) + 1:02d}.png"
                if not _save_embedded_image(document, xref, image_path):
                    continue

                label = _visual_label(context, page_index + 1, len(assets) + 1)
                assets.append(
                    PdfImageAsset(
                        index=len(assets) + 1,
                        label=label,
                        path=str(image_path),
                        page_number=page_index + 1,
                        kind="embedded_image",
                        nearby_text=context,
                        description=_visual_description(label, page_index + 1, context),
                    )
                )

    finally:
        document.close()

    return assets


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

def _save_embedded_image(document, xref: int, image_path: Path) -> bool:
    try:
        import fitz

        pixmap = fitz.Pixmap(document, xref)
        if pixmap.width < MIN_VISUAL_DIMENSION or pixmap.height < MIN_VISUAL_DIMENSION:
            return False
        if pixmap.n - pixmap.alpha > 3:
            pixmap = fitz.Pixmap(fitz.csRGB, pixmap)
        pixmap.save(str(image_path))
        return True
    except Exception:
        return False


def _select_visual_context(page_text: str) -> str:
    if not page_text:
        return ""

    lines = [line.strip() for line in page_text.splitlines() if line.strip()]
    caption_lines = [
        line
        for line in lines
        if re.search(r"\b(fig(?:ure)?\.?\s*\d+|table\s*\d+)\b", line, re.IGNORECASE)
    ]
    context = " ".join(caption_lines[:4]) if caption_lines else " ".join(lines[:10])
    return _shorten_context(context)


def _visual_label(context: str, page_number: int, asset_index: int) -> str:
    caption_match = re.search(
        r"\b((?:fig(?:ure)?\.?|table)\s*\d+[^\n.]{0,90})",
        context,
        re.IGNORECASE,
    )
    if caption_match:
        return _shorten_context(caption_match.group(1), limit=110)
    return f"Visual {asset_index} from page {page_number}"


def _visual_description(label: str, page_number: int, context: str) -> str:
    if context:
        return _shorten_context(
            f"{label}. Appears on page {page_number}. Nearby paper text: {context}",
            limit=650,
        )
    return f"{label}. Appears on page {page_number}."


def _shorten_context(text: str, *, limit: int = MAX_VISUAL_CONTEXT_CHARS) -> str:
    clean_text = " ".join(text.split())
    if len(clean_text) <= limit:
        return clean_text
    return clean_text[: limit - 3].rstrip() + "..."

# [GenAI Usage] LLM response end
# [GenAI Reflection] I asked Codex to keep this PDF processing layer deterministic and bounded instead of making the LLM responsible for fetching files. 
# I reviewed that the code validates PDF URLs, caps download size and page count, extracts text lazily through pypdf, 
# detects common paper section headings, and falls back to body chunks when headings are unavailable.
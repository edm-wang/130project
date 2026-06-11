# Don't delete comments below
# [GenAI Usage 1] Codex Prompt
# Please add a local QA harness for iterating on the Team 3 paper summary feature using a locally
# stored PDF. The script should extract PDF sections, figures, and table evidence, save all extracted
# artifacts into an ignored local output folder, build and save the prompt, call the existing OpenAI
# summary helper, and write a section-by-section summary markdown file. Keep this separate from the
# production API route so we can manually inspect extraction quality and iterate on prompts using one
# real paper at a time.
# [GenAI Usage 1] Response begins:

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import sys
from typing import Any

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))
load_dotenv(BACKEND_DIR / "app" / "supabase" / ".env")
load_dotenv()

from app.services.llm_summary import generate_section_summary_text  # noqa: E402
from app.services.pdf_sections import (  # noqa: E402
    PaperSection,
    extract_pdf_sections,
    extract_pdf_visual_assets,
)
from app.services.summary_prompt import build_section_summary_prompt  # noqa: E402


DEFAULT_OUTPUT_ROOT = BACKEND_DIR / "generated" / "summary_qa"
MAX_TABLES = 12
MAX_TABLE_CONTEXT_CHARS = 1200
MAX_VISUAL_EVIDENCE_CHARS = 5000


@dataclass(frozen=True)
class TableEvidence:
    index: int
    page_number: int
    label: str
    extraction_method: str
    caption_or_context: str
    rows: list[list[str]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run local extraction and summary QA for one research-paper PDF."
    )
    parser.add_argument(
        "--pdf",
        required=True,
        help="Path to a local PDF file, for example backend/pdf/dp.pdf.",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Paper title to use in the summary prompt. Defaults to the PDF filename stem.",
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Root output directory for local QA artifacts.",
    )
    parser.add_argument(
        "--run-name",
        default=None,
        help="Output folder name. Defaults to the PDF filename stem.",
    )
    parser.add_argument(
        "--max-sections",
        type=int,
        default=10,
        help="Maximum extracted sections to pass into the summary prompt.",
    )
    parser.add_argument(
        "--max-figures",
        type=int,
        default=8,
        help="Maximum embedded figures/images to extract.",
    )
    parser.add_argument(
        "--max-tables",
        type=int,
        default=MAX_TABLES,
        help="Maximum tables/caption evidence records to extract.",
    )
    parser.add_argument(
        "--skip-openai",
        action="store_true",
        help="Only extract and save evidence; do not call OpenAI for the summary.",
    )
    parser.add_argument(
        "--custom-instructions",
        default=(
            "Write a section-by-section research-paper summary for a student reader. "
            "Use concrete details from methods, experiments, figures, and tables when available. "
            "Avoid generic filler; mention limitations or assumptions if the paper states them."
        ),
        help="Additional summary instructions appended to the section-summary prompt.",
    )
    return parser.parse_args()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def section_markdown(sections: list[PaperSection]) -> str:
    chunks = []
    for index, section in enumerate(sections, start=1):
        chunks.append(
            "\n".join(
                [
                    f"## {index}. {section.heading}",
                    "",
                    section.text.strip(),
                ]
            )
        )
    return "\n\n".join(chunks).strip() + "\n"


def table_markdown(tables: list[TableEvidence]) -> str:
    if not tables:
        return "No table evidence extracted.\n"

    chunks = []
    for table in tables:
        chunks.append(f"## Table Evidence {table.index}: {table.label}")
        chunks.append(f"- Page: {table.page_number}")
        chunks.append(f"- Method: {table.extraction_method}")
        if table.caption_or_context:
            chunks.append(f"- Context: {table.caption_or_context}")
        if table.rows:
            chunks.append("")
            chunks.append(_rows_to_markdown(table.rows))
        chunks.append("")
    return "\n".join(chunks).strip() + "\n"


def visual_markdown(visuals: list) -> str:
    if not visuals:
        return "No figure/image evidence extracted.\n"

    chunks = []
    for asset in visuals:
        chunks.append(f"## Visual {asset.index}: {asset.label}")
        chunks.append(f"- Page: {asset.page_number}")
        chunks.append(f"- Type: {asset.kind}")
        chunks.append(f"- File: {asset.path}")
        chunks.append(f"- Description: {asset.description}")
        if asset.nearby_text:
            chunks.append(f"- Nearby text: {asset.nearby_text}")
        chunks.append("")
    return "\n".join(chunks).strip() + "\n"


def _rows_to_markdown(rows: list[list[str]], *, max_rows: int = 12, max_cols: int = 8) -> str:
    clean_rows = [
        [str(cell or "").replace("\n", " ").strip() for cell in row[:max_cols]]
        for row in rows[:max_rows]
        if row
    ]
    if not clean_rows:
        return ""

    width = max(len(row) for row in clean_rows)
    padded = [row + [""] * (width - len(row)) for row in clean_rows]
    header = padded[0]
    separator = ["---"] * width
    body = padded[1:]

    def fmt(row: list[str]) -> str:
        return "| " + " | ".join(row) + " |"

    return "\n".join([fmt(header), fmt(separator), *[fmt(row) for row in body]])


def dedupe_visual_assets(visuals: list) -> list:
    deduped = []
    seen = set()
    for asset in visuals:
        key = (
            int(getattr(asset, "page_number", 0)),
            str(getattr(asset, "label", "")).lower(),
            str(getattr(asset, "nearby_text", ""))[:180].lower(),
        )
        asset_path = Path(asset.path)
        if key in seen:
            _delete_file_quietly(asset_path)
            continue
        seen.add(key)
        new_index = len(deduped) + 1
        renamed_path = _rename_visual_asset(asset_path, new_index)
        deduped.append(replace(asset, index=new_index, path=str(renamed_path)))
    return deduped


def _delete_file_quietly(path: Path) -> None:
    try:
        path.unlink()
    except OSError:
        pass


def _rename_visual_asset(path: Path, index: int) -> Path:
    target = path.with_name(f"visual_{index:02d}{path.suffix or '.png'}")
    if path == target:
        return path
    _delete_file_quietly(target)
    try:
        path.rename(target)
        return target
    except OSError:
        return path


def extract_table_evidence(pdf_bytes: bytes, *, max_tables: int = MAX_TABLES) -> list[TableEvidence]:
    try:
        import fitz
    except ImportError:
        return []

    document = fitz.open(stream=pdf_bytes, filetype="pdf")
    tables: list[TableEvidence] = []
    try:
        for page_index in range(len(document)):
            if len(tables) >= max_tables:
                break
            page = document.load_page(page_index)
            tables.extend(_extract_structured_tables(page, page_index, len(tables), max_tables))
            if len(tables) >= max_tables:
                break
            tables.extend(_extract_table_caption_contexts(page, page_index, len(tables), max_tables))
    finally:
        document.close()

    return _dedupe_tables(tables)[:max_tables]


def _extract_structured_tables(page, page_index: int, existing_count: int, max_tables: int) -> list[TableEvidence]:
    page_text = page.get_text("text") or ""
    if not re.search(r"(?i)\btable\s+\d+", page_text):
        return []
    if not hasattr(page, "find_tables"):
        return []

    found = []
    try:
        table_finder = page.find_tables()
    except Exception:
        return []

    for raw_table in getattr(table_finder, "tables", []) or []:
        if existing_count + len(found) >= max_tables:
            break
        try:
            rows = raw_table.extract() or []
        except Exception:
            rows = []
        if not rows:
            continue
        found.append(
            TableEvidence(
                index=existing_count + len(found) + 1,
                page_number=page_index + 1,
                label=f"Detected table on page {page_index + 1}",
                extraction_method="pymupdf_find_tables",
                caption_or_context=_short_text(page.get_text("text") or ""),
                rows=rows,
            )
        )
    return found


def _extract_table_caption_contexts(page, page_index: int, existing_count: int, max_tables: int) -> list[TableEvidence]:
    page_text = page.get_text("text") or ""
    normalized = "\n".join(line.strip() for line in page_text.splitlines() if line.strip())
    if not normalized:
        return []

    matches = list(re.finditer(r"(?i)\btable\s+\d+[\w:.-]*\b.{0,500}", normalized))
    found = []
    for match in matches:
        if existing_count + len(found) >= max_tables:
            break
        context_start = max(0, match.start() - 350)
        context_end = min(len(normalized), match.end() + 650)
        context = _short_text(normalized[context_start:context_end])
        label = _short_text(match.group(0), limit=120)
        found.append(
            TableEvidence(
                index=existing_count + len(found) + 1,
                page_number=page_index + 1,
                label=label or f"Table evidence on page {page_index + 1}",
                extraction_method="caption_context",
                caption_or_context=context,
                rows=[],
            )
        )
    return found


def _dedupe_tables(tables: list[TableEvidence]) -> list[TableEvidence]:
    seen = set()
    deduped = []
    for table in tables:
        key = (table.page_number, table.label.lower(), table.caption_or_context[:120].lower())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(table)
    return [
        TableEvidence(
            index=index,
            page_number=table.page_number,
            label=table.label,
            extraction_method=table.extraction_method,
            caption_or_context=table.caption_or_context,
            rows=table.rows,
        )
        for index, table in enumerate(deduped, start=1)
    ]


def _short_text(text: str, *, limit: int = MAX_TABLE_CONTEXT_CHARS) -> str:
    clean = " ".join(text.split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 3].rstrip() + "..."


def visual_evidence_section(visuals: list, tables: list[TableEvidence]) -> PaperSection | None:
    lines = []
    if visuals:
        lines.append("Figures and visual evidence:")
        for asset in visuals:
            lines.append(
                f"- Visual {asset.index} on page {asset.page_number}: {asset.description}"
            )
    if tables:
        lines.append("Tables and quantitative evidence:")
        for table in tables:
            row_note = ""
            if table.rows:
                row_note = f" Extracted {len(table.rows)} table rows."
            lines.append(
                f"- Table evidence {table.index} on page {table.page_number}: "
                f"{table.caption_or_context or table.label}.{row_note}"
            )
    if not lines:
        return None

    text = "\n".join(lines)[:MAX_VISUAL_EVIDENCE_CHARS]
    return PaperSection(heading="Extracted Figures And Tables", text=text)


def main() -> None:
    args = parse_args()
    pdf_path = Path(args.pdf).expanduser().resolve()
    if not pdf_path.exists():
        raise SystemExit(f"PDF not found: {pdf_path}")

    title = args.title or pdf_path.stem.replace("_", " ").replace("-", " ").title()
    run_name = args.run_name or pdf_path.stem
    output_dir = Path(args.output_root).expanduser().resolve() / run_name
    figures_dir = output_dir / "figures"

    if output_dir.exists():
        shutil.rmtree(output_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    pdf_bytes = pdf_path.read_bytes()
    sections = extract_pdf_sections(pdf_bytes, max_sections=args.max_sections)
    visuals = dedupe_visual_assets(
        extract_pdf_visual_assets(pdf_bytes, figures_dir, max_assets=args.max_figures * 3)
    )[: args.max_figures]
    tables = extract_table_evidence(pdf_bytes, max_tables=args.max_tables)

    prompt_sections = list(sections)
    evidence_section = visual_evidence_section(visuals, tables)
    if evidence_section:
        prompt_sections.append(evidence_section)

    prompt = build_section_summary_prompt(
        title=title,
        sections=prompt_sections,
        custom_instructions=args.custom_instructions,
    )

    write_json(
        output_dir / "run_metadata.json",
        {
            "pdf_path": str(pdf_path),
            "title": title,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "section_count": len(sections),
            "visual_count": len(visuals),
            "table_evidence_count": len(tables),
            "skip_openai": args.skip_openai,
        },
    )
    write_json(output_dir / "sections.json", [asdict(section) for section in sections])
    write_text(output_dir / "sections.md", section_markdown(sections))
    write_json(output_dir / "figures.json", [asdict(asset) for asset in visuals])
    write_text(output_dir / "figures.md", visual_markdown(visuals))
    write_json(output_dir / "tables.json", [asdict(table) for table in tables])
    write_text(output_dir / "tables.md", table_markdown(tables))
    write_text(output_dir / "prompt.txt", prompt)

    if args.skip_openai:
        write_text(
            output_dir / "summary.md",
            "OpenAI summary generation skipped. Re-run without --skip-openai to generate it.\n",
        )
    else:
        generated = generate_section_summary_text(
            title=title,
            sections=prompt_sections,
            custom_instructions=args.custom_instructions,
        )
        write_json(output_dir / "summary_metadata.json", asdict(generated))
        write_text(output_dir / "summary.md", generated.summary_text.strip() + "\n")

    print(f"Wrote local summary QA artifacts to: {output_dir}")
    print(f"Sections: {len(sections)} | Figures: {len(visuals)} | Table evidence: {len(tables)}")


if __name__ == "__main__":
    main()

# [GenAI Usage 1] Response ends
# [GenAI Usage] Reflection
# I used Codex to create this as a local, inspectable QA loop rather than another production route.
# The script keeps extraction outputs, prompt text, figures, table evidence, and model summaries side
# by side so we can tell whether bad summaries come from weak PDF extraction or weak prompting. The
# table extraction is intentionally pragmatic: it uses PyMuPDF table detection when available and also
# saves table-caption context, which is often enough evidence for summary iteration even when exact
# table structure is hard to recover.

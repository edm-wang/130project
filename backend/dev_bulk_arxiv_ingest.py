#[GenAI Usage] Prompt: Please write a script that allows bulk ingestion of papers. The program should be executed manually as an initial ingestion of paper.GeneratorExit
# Instead of specifying a target date, as implemented in the daily paper ingestion runner. Please instead allow specifying a start and end date range; in addition, the
# user should be able to specify the list of categories, max paper to ingest. Then, the program should reuse appropriate components, formulate the query URL, and query
# arxiv to fetch the papers (with appropriate timeout and retry mechianism), and then compute the embeddings of the paper, and then insert the papers and their respective
# embeddings into the database. 
#[GenAI Usage] LLM response begins:

from __future__ import annotations

import argparse
from datetime import date, datetime, time, timezone
import json
import sys
import time as time_module
from typing import Iterable, Optional, TypeVar
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.services.embedding_config import (
    DEFAULT_EMBEDDING_DIMENSIONS,
    DEFAULT_EMBEDDING_MODEL,
)
from app.services.paper_ingestion import (
    ARXIV_API_URL,
    DEFAULT_CATEGORIES,
    DEFAULT_REQUEST_DELAY_SECONDS,
    DEFAULT_TIMEOUT_SECONDS,
    ArxivPaper,
    embed_arxiv_papers,
    parse_arxiv_feed,
    upsert_papers,
    _format_arxiv_date,
    _normalize_categories,
    _wait_for_arxiv_rate_limit,
)

MAX_ARXIV_PAGE_SIZE = 2000
DEFAULT_RATE_LIMIT_BACKOFF_SECONDS = 300
DEFAULT_DB_BATCH_SIZE = 50
T = TypeVar("T")


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("dates must use YYYY-MM-DD format") from exc

"""
python dev_bulk_arxiv_ingest.py `
--start-date 2025-01-01 `
--end-date 2025-05-31 `
--category cs.AI cs.LG cs.CL cs.CV stat.ML cs.RO cs.MA cs.NE cs.IR `
--max-results 500 `

python dev_bulk_arxiv_ingest.py `
--start-date 2025-06-01 `
--end-date 2025-12-31 `
--category cs.AI cs.LG cs.CL cs.CV stat.ML cs.RO cs.MA cs.NE cs.IR `
--max-results 500 `

python dev_bulk_arxiv_ingest.py `
--start-date 2025-01-01 `
--end-date 2025-12-31 `
--category cs.AI `
--max-results 1000 `

python dev_bulk_arxiv_ingest.py `
  --start-date 2026-01-01 `
  --end-date 2026-05-28 `
  --category math.NT math.AG math.GT physics.optics astro-ph.GA q-bio.PE econ.TH `
  --max-results 500
"""

def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Manually ingest an initial bulk of arXiv papers over a date range."
    )
    parser.add_argument("--start-date", type=parse_date, required=True)
    parser.add_argument("--end-date", type=parse_date, required=True)
    parser.add_argument(
        "--category",
        nargs="+",
        default=None,
        help="Space-separated arXiv categories, e.g. --category cs.AI cs.LG cs.CL.",
    )
    parser.add_argument("--max-results", type=int, default=1000)
    parser.add_argument("--page-size", type=int, default=2000)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument(
        "--db-batch-size",
        type=int,
        default=DEFAULT_DB_BATCH_SIZE,
        help="Rows per Supabase upsert statement.",
    )
    parser.add_argument(
        "--request-delay",
        type=int,
        default=10,
        help="Minimum delay in seconds between arXiv API requests.",
    )
    parser.add_argument(
        "--rate-limit-backoff",
        type=int,
        default=DEFAULT_RATE_LIMIT_BACKOFF_SECONDS,
        help="Seconds to wait before retrying after arXiv returns HTTP 429.",
    )
    parser.add_argument(
        "--fetch-only",
        action="store_true",
        help="Fetch papers without inserting papers or embeddings into Supabase.",
    )
    parser.add_argument(
        "--skip-embeddings",
        action="store_true",
        help="Persist paper metadata without computing paper embeddings.",
    )

    args = parser.parse_args(argv)
    if args.start_date > args.end_date:
        parser.error("--start-date must be before or equal to --end-date")
    if args.max_results < 1:
        parser.error("--max-results must be at least 1")
    if args.page_size < 1 or args.page_size > MAX_ARXIV_PAGE_SIZE:
        parser.error(f"--page-size must be between 1 and {MAX_ARXIV_PAGE_SIZE}")
    if args.request_delay < 0:
        parser.error("--request-delay must not be negative")
    if args.retries < 0:
        parser.error("--retries must not be negative")
    if args.timeout < 1:
        parser.error("--timeout must be at least 1")
    if args.rate_limit_backoff < 0:
        parser.error("--rate-limit-backoff must not be negative")
    if args.db_batch_size < 1:
        parser.error("--db-batch-size must be at least 1")

    args.categories = parse_categories(args.category)
    return args


def parse_categories(values: Optional[list[str]]) -> list[str]:
    if not values:
        return list(DEFAULT_CATEGORIES)

    return _normalize_categories(values)


def build_arxiv_range_query_url(
    *,
    start_date: date,
    end_date: date,
    categories: list[str],
    start: int,
    max_results: int,
) -> str:
    start_time = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
    end_time = datetime.combine(end_date, time(23, 59), tzinfo=timezone.utc)
    category_query = " OR ".join(f"cat:{category}" for category in categories)
    search_query = (
        f"({category_query}) AND "
        f"submittedDate:[{_format_arxiv_date(start_time)} TO "
        f"{_format_arxiv_date(end_time)}]"
    )
    params = {
        "search_query": search_query,
        "start": start,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    return f"{ARXIV_API_URL}?{urlencode(params)}"


def fetch_arxiv_papers_for_range(
    *,
    start_date: date,
    end_date: date,
    categories: list[str],
    max_results: int,
    page_size: int,
    timeout_seconds: int,
    retries: int,
    request_delay_seconds: int,
    rate_limit_backoff_seconds: int,
) -> tuple[list[ArxivPaper], list[str]]:
    papers: list[ArxivPaper] = []
    query_urls: list[str] = []
    start = 0

    while len(papers) < max_results:
        batch_size = min(page_size, max_results - len(papers))
        query_url = build_arxiv_range_query_url(
            start_date=start_date,
            end_date=end_date,
            categories=categories,
            start=start,
            max_results=batch_size,
        )
        print(f"Query URL: {query_url}", file=sys.stderr)
        batch = fetch_arxiv_query_url(
            query_url,
            timeout_seconds=timeout_seconds,
            retries=retries,
            request_delay_seconds=request_delay_seconds,
            rate_limit_backoff_seconds=rate_limit_backoff_seconds,
        )
        query_urls.append(query_url)

        if not batch:
            break

        papers.extend(batch)
        if len(batch) < batch_size:
            break

        start += batch_size

    return papers[:max_results], query_urls


def fetch_arxiv_query_url(
    query_url: str,
    *,
    timeout_seconds: int,
    retries: int,
    request_delay_seconds: int,
    rate_limit_backoff_seconds: int,
) -> list[ArxivPaper]:
    request = Request(
        query_url,
        headers={"User-Agent": "paper-arxiv-dev-bulk-ingest/0.1"},
    )
    last_error = None
    attempts_made = 0

    for attempt in range(retries + 1):
        attempts_made = attempt + 1
        try:
            _wait_for_arxiv_rate_limit(request_delay_seconds)
            with urlopen(request, timeout=timeout_seconds) as response:
                return parse_arxiv_feed(response.read())
        except HTTPError as exc:
            last_error = exc
            if exc.code == 429:
                if attempt >= retries:
                    break

                wait_seconds = _retry_after_seconds(
                    exc,
                    rate_limit_backoff_seconds,
                )
                print(
                    "arXiv returned HTTP 429 Too Many Requests; "
                    f"waiting {wait_seconds}s before retrying...",
                    file=sys.stderr,
                )
                time_module.sleep(wait_seconds)
        except (TimeoutError, OSError) as exc:
            last_error = exc

    raise RuntimeError(
        f"arXiv API request failed after {attempts_made} attempt(s): {last_error}"
    ) from last_error


def _retry_after_seconds(exc: HTTPError, default_seconds: int) -> int:
    retry_after = exc.headers.get("Retry-After")
    if retry_after is None:
        return default_seconds

    try:
        return max(0, int(retry_after))
    except ValueError:
        return default_seconds


def paper_to_sample_row(paper: ArxivPaper) -> dict:
    return {
        "source_id": paper.source_id,
        "title": paper.title,
        "categories": paper.categories,
        "published_at": paper.published_at,
    }


def _iter_batches(
    items: list[T],
    batch_size: int,
) -> Iterable[tuple[int, int, list[T]]]:
    total_batches = (len(items) + batch_size - 1) // batch_size
    for start in range(0, len(items), batch_size):
        yield (
            (start // batch_size) + 1,
            total_batches,
            items[start:start + batch_size],
        )


def upsert_papers_in_batches(
    papers: list[ArxivPaper],
    *,
    client,
    batch_size: int,
) -> list[dict]:
    inserted_papers: list[dict] = []
    for batch_number, total_batches, batch in _iter_batches(papers, batch_size):
        print(
            "Upserting papers batch "
            f"{batch_number}/{total_batches} ({len(batch)} row(s))...",
            file=sys.stderr,
        )
        try:
            inserted_papers.extend(upsert_papers(batch, client=client))
        except Exception as exc:
            raise RuntimeError(
                "paper upsert batch "
                f"{batch_number}/{total_batches} failed ({len(batch)} row(s)): {exc}"
            ) from exc

    return inserted_papers


def _paper_embedding_rows(
    papers: list[ArxivPaper],
    persisted_papers: list[dict],
) -> list[dict]:
    persisted_by_source_id = {
        paper.get("source_id"): paper
        for paper in persisted_papers
        if paper.get("source_id") and paper.get("id")
    }
    rows = []
    for paper in papers:
        persisted_paper = persisted_by_source_id.get(paper.source_id)
        if (
            persisted_paper
            and paper.embedding is not None
            and paper.embedded_text is not None
            and paper.embedding_model is not None
        ):
            rows.append(
                {
                    "paper_id": persisted_paper["id"],
                    "embedding_model": paper.embedding_model,
                    "embedding": paper.embedding,
                    "embedded_text": paper.embedded_text,
                }
            )

    return rows


def upsert_paper_embeddings_in_batches(
    papers: list[ArxivPaper],
    persisted_papers: list[dict],
    *,
    client,
    batch_size: int,
) -> int:
    rows = _paper_embedding_rows(papers, persisted_papers)
    if not rows:
        return 0

    from postgrest.types import ReturnMethod

    embedded_count = 0
    for batch_number, total_batches, batch in _iter_batches(rows, batch_size):
        print(
            "Upserting paper embeddings batch "
            f"{batch_number}/{total_batches} ({len(batch)} row(s))...",
            file=sys.stderr,
        )
        try:
            (
                client.table("paper_embeddings")
                .upsert(
                    batch,
                    on_conflict="paper_id",
                    returning=ReturnMethod.minimal,
                )
                .execute()
            )
        except Exception as exc:
            raise RuntimeError(
                "paper embedding upsert batch "
                f"{batch_number}/{total_batches} failed ({len(batch)} row(s)): {exc}"
            ) from exc

        embedded_count += len(batch)

    return embedded_count


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)

    try:
        papers, query_urls = fetch_arxiv_papers_for_range(
            start_date=args.start_date,
            end_date=args.end_date,
            categories=args.categories,
            max_results=args.max_results,
            page_size=args.page_size,
            timeout_seconds=args.timeout,
            retries=args.retries,
            request_delay_seconds=args.request_delay,
            rate_limit_backoff_seconds=args.rate_limit_backoff,
        )

        inserted_papers = []
        embedded_count = 0
        if not args.fetch_only:
            from app.supabase.db import get_or_create_service_supabase_client

            client = get_or_create_service_supabase_client()
            if not args.skip_embeddings:
                print(f"Embedding {len(papers)} paper(s)...", file=sys.stderr)
                papers = embed_arxiv_papers(
                    papers,
                    embedding_model=DEFAULT_EMBEDDING_MODEL,
                    embedding_dimensions=DEFAULT_EMBEDDING_DIMENSIONS,
                )

            inserted_papers = upsert_papers_in_batches(
                papers,
                client=client,
                batch_size=args.db_batch_size,
            )
            if not args.skip_embeddings:
                embedded_count = upsert_paper_embeddings_in_batches(
                    papers,
                    inserted_papers,
                    client=client,
                    batch_size=args.db_batch_size,
                )

        output = {
            "date_range": {
                "start_date": args.start_date.isoformat(),
                "end_date": args.end_date.isoformat(),
            },
            "categories": args.categories,
            "sort_by": "relevance",
            "fetched_count": len(papers),
            "inserted_count": len(inserted_papers),
            "embedded_count": embedded_count,
            "embeddings_skipped": args.fetch_only or args.skip_embeddings,
            "query_count": len(query_urls),
            "query_urls": query_urls,
            "sample_papers": [paper_to_sample_row(paper) for paper in papers[:5]],
        }
    except Exception as exc:
        print(f"bulk arXiv ingestion failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#[GenAI Usage] LLM response ends
#[GenAI Usage] Reflection: I used Codex for this task with a high level instruction because this is not an integral part of the product.
# The purpose of the initial ingestion is to mainly accumulate a large number of papers to our database (isntead of ingesting through 
# scheduled cron jobs in our actual application) so we can thoroughly test our recommendation algorithm. Nonetheless, I clearly specified
# the arguments that the user can provide to the program, the intended effect; I also thoroughly examined the code to ensure it achieves
# the desired behavior.
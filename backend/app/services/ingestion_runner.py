# Dont Delete the comments below
# [GenAI Usage] Codex Prompt
# Need to have a simple invocation script that uses paper_ingesetion.py functions in ingestion_runner.py in the relative path: backend/app/services/ingestion_runner.py
# Supabase URL can be load from .env under /supabase
# [GenAI Usage] Response begins:


from __future__ import annotations

import argparse
from datetime import date, datetime, timezone, timedelta
import json
from pathlib import Path
import sys
from typing import Optional, Any, Iterable
from dotenv import load_dotenv

from app.services.paper_ingestion import (
    DEFAULT_CATEGORIES,
    DEFAULT_MAX_RESULTS,
    DEFAULT_REQUEST_DELAY_SECONDS,
    DEFAULT_RETRIES,
    DEFAULT_TIMEOUT_SECONDS,
    fetch_arxiv_papers_for_date,
    ingest_arxiv_papers_for_date,
)


SUPABASE_ENV_PATH = Path(__file__).resolve().parents[1] / "supabase" / ".env"

# Don't delete comments below
# [GenAI Usage] Codex Prompt:
# Right now, the cron job defined in paper ingestion only run for one domain: CS.AI. I want to expand its scope to multi domain: physics, cs.db, cs.cv, math, life science etc. each with limit 500?
# Too much. i'm afraid it will throttle. maybe several cron job each with a domain run at different time -- each with an hour difference?
# [Gen AI usage Round 2] Codex prompt:
# I noticed that math has so many sub-domains that is not ideal. It is too much subdomains, isn't it? For each domain in ( Economics, Electrical Engineering and Systems Science, Mathematics, Physics, Quantitative Biology, Quantitative Finance) defined in  https://arxiv.org/category_taxonomy, select only up to 5 subdomains too avoid 429 error.
# [GenAI Usage] Response begins:
DEFAULT_CRON_MAX_RESULTS = 300
DEFAULT_CRON_DOMAIN_CATEGORY_GROUPS: dict[str, tuple[str, ...]] = {
    "cs_ai": ("cs.AI",),
    "cs_db": ("cs.DB",),
    "cs_cv": ("cs.CV",),
    "cs_lg": ("cs.LG",),
    "cs_cl": ("cs.CL",),
    "econ": (
        "econ.EM",
        "econ.GN",
        "econ.TH",
    ),
    "eess": (
        "eess.AS",
        "eess.SP",
        "eess.SY",
    ),
    "math": (
        "math.AP",
        "math.CO",
        "math.OC",
        "math.PR",
    ),
    "physics": (
        "physics.app-ph",
        "physics.comp-ph",
        "physics.optics",
        "quant-ph",
    ),
    "q_bio": (
        "q-bio.BM",
        "q-bio.GN",
        "q-bio.NC",
        "q-bio.QM",
    ),
    "q_fin": (
        "q-fin.CP",
        "q-fin.GN",
        "q-fin.PM",
        "q-fin.ST",
    ),
    "stat": (
        "stat.AP",
        "stat.CO",
        "stat.ML",
    ),
}
DEFAULT_CRON_DOMAIN_ALIASES = {
    "cs-ai": "cs_ai",
    "cs.ai": "cs_ai",
    "cs_ai": "cs_ai",
    "cs-db": "cs_db",
    "cs.db": "cs_db",
    "cs_db": "cs_db",
    "cs-cv": "cs_cv",
    "cs.cv": "cs_cv",
    "cs_cv": "cs_cv",
    "cs-lg": "cs_lg",
    "cs.lg": "cs_lg",
    "cs_lg": "cs_lg",
    "cs-cl": "cs_cl",
    "cs.cl": "cs_cl",
    "cs_cl": "cs_cl",
    "economics": "econ",
    "econ": "econ",
    "electrical-engineering-and-systems-science": "eess",
    "electrical_engineering_and_systems_science": "eess",
    "electrical-engineering": "eess",
    "systems-science": "eess",
    "eess": "eess",
    "math": "math",
    "mathematics": "math",
    "physics": "physics",
    "life-science": "q_bio",
    "life_science": "q_bio",
    "quantitative-biology": "q_bio",
    "quantitative_biology": "q_bio",
    "q-bio": "q_bio",
    "q.bio": "q_bio",
    "q_bio": "q_bio",
    "quantitative-finance": "q_fin",
    "quantitative_finance": "q_fin",
    "q-fin": "q_fin",
    "q.fin": "q_fin",
    "q_fin": "q_fin",
    "statistics": "stat",
    "stat": "stat",
}
# Don't delete comments below
# [GenAI Usage] Response ends
# [GenAI Usage] Reflection:
# I prompted Codex with clear instructions so that it comes up with a list of usable domains.
# I verified the validity of these domains myself in https://arxiv.org/category_taxonomy, where all domain names are documented. The implementation right now will cover all CS domains, and key domains in other areas as well, which is intended in the design doc.
# [GenAI Usage] Reflection:
# Round2: I narrowed the scope of subdomains to avoid throttling Arxiv server so that the ingestion will be more robust.


def load_supabase_env() -> None:
    load_dotenv(SUPABASE_ENV_PATH)
    load_dotenv()


def parse_date(value: Optional[str]) -> date:
    if value is None:
        #Defaults to yesterday in UTC timezone to avoid querying a future date, which returns 0 results regardless
        return datetime.now(timezone.utc).date() - timedelta(days=1)

    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "--date must use YYYY-MM-DD format"
        ) from exc


def parse_args(argv: Optional[list[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch arXiv papers and insert them into the papers table."
    )
    parser.add_argument(
        "--date",
        type=parse_date,
        default=None,
        help="UTC submitted date to ingest, formatted as YYYY-MM-DD. Defaults to today.",
    )
    parser.add_argument(
        "--category",
        action="append",
        default=None,
        help="arXiv category to include. Repeat for multiple categories. Defaults to cs.AI.",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=DEFAULT_MAX_RESULTS,
        help=f"Maximum arXiv records to request. Defaults to {DEFAULT_MAX_RESULTS}.",
    )
    parser.add_argument(
        "--fetch-only",
        action="store_true",
        help="Fetch and print arXiv results without inserting into Supabase.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"arXiv request timeout in seconds. Defaults to {DEFAULT_TIMEOUT_SECONDS}.",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=DEFAULT_RETRIES,
        help=f"Number of retries after a failed arXiv request. Defaults to {DEFAULT_RETRIES}.",
    )
    parser.add_argument(
        "--request-delay",
        type=int,
        default=DEFAULT_REQUEST_DELAY_SECONDS,
        help=(
            "Minimum delay in seconds between arXiv API requests. "
            f"Defaults to {DEFAULT_REQUEST_DELAY_SECONDS}."
        ),
    )

    args = parser.parse_args(argv)
    if args.date is None:
        args.date = parse_date(None)
    return args


def paper_to_output_row(paper) -> dict:
    return {
        "source": "arxiv",
        "source_id": paper.source_id,
        "title": paper.title,
        "abstract": paper.abstract,
        "authors_text": paper.authors_text,
        "categories": paper.categories,
        "source_url": paper.source_url,
        "pdf_url": paper.pdf_url,
        "published_at": paper.published_at,
        "source_updated_at": paper.source_updated_at,
    }

#Begin human-written code
def run_paper_ingestion_cron(
        *,
        target_date: date | None = None,
        categories: Iterable[str] | None = None,
        max_results: int = DEFAULT_CRON_MAX_RESULTS,
    ) -> dict[str, Any]:
    from app.supabase.db import get_or_create_service_supabase_client

    service_client = get_or_create_service_supabase_client()
    
    parsed_target_date = parse_date(target_date.isoformat() if target_date else None)
    normalized_categories = list(sorted(DEFAULT_CATEGORIES) if not categories else sorted(categories))

    existing_run = (
        service_client
        .table("paper_ingestion_runs")
        .select("id, completed_at")
        .eq("source", "arxiv")
        .eq("target_date", parsed_target_date.isoformat())
        .eq("status", "completed")
        .eq("max_results", max_results)
        .contains("categories", normalized_categories)
        .contained_by("categories", normalized_categories)
        .limit(1)
        .execute()
    )

    if(existing_run.data):
        _ = (
            service_client
            .table("paper_ingestion_runs")
            .insert({
                "source": "arxiv",
                "target_date": parsed_target_date.isoformat(),
                "status": "skipped",
                "categories": normalized_categories,
                "max_results": max_results,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat(),
            })
        ).execute()

        return {
            "skipped": True,
            "run_id": None,
            "status": "skipped",
            "fetched_count": None,
            "inserted_count": None,
            "embedded_count": None,
        }


    run_response = (
        service_client
        .table("paper_ingestion_runs")
        .insert({
            "source": "arxiv",
            "target_date": parsed_target_date.isoformat(),
            "status": "running",
            "categories": normalized_categories,
            "max_results": max_results,
            "query_url": None,
            "started_at": datetime.now(timezone.utc).isoformat(),
        })
        .execute()
    )
    run = run_response.data[0]

    try:
        ingestion_result = ingest_arxiv_papers_for_date(
            submitted_date=parsed_target_date,
            categories=normalized_categories,
            max_results=max_results,
            client=service_client
        )

        _ = (
            service_client
            .table("paper_ingestion_runs")
            .update({
                "status": "completed",
                "fetched_count": ingestion_result.fetched_count,
                "inserted_count": ingestion_result.inserted_count,
                "query_url": ingestion_result.query_url,
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "error_message": None
            })
            .eq("id", run["id"])
            .execute()
        )

        return {
            "skipped": False,
            "run_id": run["id"],
            "status": "completed",
            "query_url": ingestion_result.query_url,
            "fetched_count": ingestion_result.fetched_count,
            "inserted_count": ingestion_result.inserted_count,
            "embedded_count": ingestion_result.embedded_count,
        }

    except Exception as exception:
        _ = (
            service_client
            .table("paper_ingestion_runs")
            .update({
                "status": "failed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "error_message": str(exception)
            })
            .eq("id", run["id"])
            .execute()
        )

        raise


# [GenAI Usage] Codex Prompt:
# Right now, the cron job defined in paper ingestion only run for one domain: CS.AI. I want to expand its scope to multi domain: physics, cs.db, cs.cv, math, life science etc. each with limit 500?
# too much. i'm afraid it will throttle. maybe several cron job each with a domain run at different time -- each with an hour difference?
# [GenAI Usage] Response begins:
def run_domain_paper_ingestion_cron(
        domain: str,
        *,
        target_date: date | None = None,
        max_results: int = DEFAULT_CRON_MAX_RESULTS,
    ) -> dict[str, Any]:
    normalized_domain = DEFAULT_CRON_DOMAIN_ALIASES.get(domain.strip().lower())
    if normalized_domain is None:
        valid_domains = ", ".join(sorted(DEFAULT_CRON_DOMAIN_CATEGORY_GROUPS))
        raise ValueError(f"unknown paper ingestion domain: {domain}. Valid domains: {valid_domains}")

    categories = DEFAULT_CRON_DOMAIN_CATEGORY_GROUPS[normalized_domain]
    result = run_paper_ingestion_cron(
        target_date=target_date,
        categories=categories,
        max_results=max_results,
    )

    return {
        "domain": normalized_domain,
        "categories": list(categories),
        **result,
    }
# [GenAI Usage] Response ends
# [GenAI Usage] Reflection:
# This wrapper prevents scheduled ingestion from fanning out across all domains in one request.

#End human-written code

def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    categories = args.category or list(DEFAULT_CATEGORIES)

    try:
        if args.fetch_only:
            papers, query_url = fetch_arxiv_papers_for_date(
                args.date,
                categories=categories,
                max_results=args.max_results,
                timeout_seconds=args.timeout,
                retries=args.retries,
                request_delay_seconds=args.request_delay,
            )
            output = {
                "query_url": query_url,
                "fetched_count": len(papers),
                "inserted_count": 0,
                "papers": [paper_to_output_row(paper) for paper in papers],
                "embeddings_skipped": True,
                "insert_skipped": True,
            }
        else:
            load_supabase_env()
            result = ingest_arxiv_papers_for_date(
                args.date,
                categories=categories,
                max_results=args.max_results,
                timeout_seconds=args.timeout,
                retries=args.retries,
                request_delay_seconds=args.request_delay,
            )
            output = {
                "query_url": result.query_url,
                "fetched_count": result.fetched_count,
                "inserted_count": result.inserted_count,
                "embedded_count": result.embedded_count,
                "papers": result.papers,
                "embeddings_skipped": result.embeddings_skipped,
            }
    except Exception as exc:
        print(f"paper ingestion failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# Don't delete the comments below
# [GenAI Usage] Response ends
# [GenAI Usage] Reflection
# The structure of the code is simple: main() + flag-parser helper
# flag-parser keeps track of the paper domain, limit number, and date. Or is the fetch-only or upsert-db. 
# main() is quite naive right now -- no parallelism, no async call, no page-limit ... So, the latency may be a big issue if the volume goes up.
# However, for the purpose of the v1, it is acceptable right now. 

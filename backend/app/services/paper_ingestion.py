# Dont Delete the comments below
# [GenAI Usage 1] Codex Prompt
# I need to run a simple paper ingestion service pipeline via arxiv api (https://info.arxiv.org/help/api/user-manual.html).
# You need to query today's article across CS.AI domain for now.
# You need to read the /models why the ORM paper-related models are defined. For paper embedding, right now skip the
# actual embedding model, but still complete the insertion logic - yet keep that embedding value field empty.
# Choose a reason number of default articles.
# [Debugging Prompt]: Notice that arXiv strictly requires a 3-second minimum delay between consecutive API requests. Please respect this restriction
# [GenAI Usage 1] Response begins:

# [GenAI Usage 2] Note: this GenAI usage generated the code and modified the existing code to support computing the embedding of papers
# and persisting them to the database.
# [GenAI Usage 2] Prompt: 
# Prompt 1: Can you modify paper_ingestion.py so that in fetch_arxiv_papers_for_date, we can also compute the embedding for each paper? Maybe we can expand 
# the ArxivPaper class to have an optional embeddings attribute, and then also implement an upsert_embeddings when the embedding is not none. Assume 
# that we will e using a OpenAI client with the OPENAI_API_KEY loaded form the dotenv. Please keep the implementation minimal. 
# Prompt 2: It seems like you are not providing the API Key to the OpenAI client. Can you assume we hve an OPENAI_API_KEY in the .env file and we should load
#  it when instantiating the client? In addition, I think we should also use a singleton pattern same as the get_or_create_client for the OpenAI client.
# Prompt 3: Since we already have get_or_create_openai_client, should we remove the openai client passing and only get the client within embed_arxiv_papers?
# [GenAI Usage 2] Response begins:

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime, time, timezone
import os
from pathlib import Path
import re
import sys
import tempfile
import time as time_module
from typing import Iterable, Optional
from urllib.parse import urlencode
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

ARXIV_API_URL = "https://export.arxiv.org/api/query"
ATOM_NS = "{http://www.w3.org/2005/Atom}"
OPENSEARCH_NS = "{http://a9.com/-/spec/opensearch/1.1/}"
OPENAI_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

DEFAULT_CATEGORIES = ("cs.AI",)
DEFAULT_MAX_RESULTS = 100
DEFAULT_SORT_BY = "submittedDate"
DEFAULT_SORT_ORDER = "descending"
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_RETRIES = 1
DEFAULT_REQUEST_DELAY_SECONDS = 3
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_EMBEDDING_DIMENSIONS = 1536
DEFAULT_EMBEDDING_BATCH_SIZE = 128
ARXIV_LAST_REQUEST_PATH = Path(tempfile.gettempdir()) / "paper_arxiv_last_request.txt"
service_openai_client = None


@dataclass(frozen=True)
class ArxivPaper:
    source_id: str
    title: str
    abstract: Optional[str]
    authors_text: Optional[str]
    categories: list[str]
    source_url: str
    pdf_url: Optional[str]
    published_at: Optional[str]
    source_updated_at: Optional[str]
    embedding: Optional[list[float]] = None
    embedded_text: Optional[str] = None
    embedding_model: Optional[str] = None


@dataclass(frozen=True)
class PaperIngestionResult:
    query_url: str
    fetched_count: int
    inserted_count: int
    papers: list[dict]
    embedded_count: int = 0
    embeddings_skipped: bool = False


def ingest_today_cs_ai_papers(
    *,
    categories: Iterable[str] = DEFAULT_CATEGORIES,
    max_results: int = DEFAULT_MAX_RESULTS,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    retries: int = DEFAULT_RETRIES,
    request_delay_seconds: int = DEFAULT_REQUEST_DELAY_SECONDS,
    compute_embeddings: bool = True,
    client=None,
) -> PaperIngestionResult:
    return ingest_arxiv_papers_for_date(
        datetime.now(timezone.utc).date(),
        categories=categories,
        max_results=max_results,
        timeout_seconds=timeout_seconds,
        retries=retries,
        request_delay_seconds=request_delay_seconds,
        compute_embeddings=compute_embeddings,
        client=client,
    )


def ingest_arxiv_papers_for_date(
    submitted_date: date,
    *,
    categories: Iterable[str] = DEFAULT_CATEGORIES,
    max_results: int = DEFAULT_MAX_RESULTS,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    retries: int = DEFAULT_RETRIES,
    request_delay_seconds: int = DEFAULT_REQUEST_DELAY_SECONDS,
    compute_embeddings: bool = True,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    embedding_dimensions: int = DEFAULT_EMBEDDING_DIMENSIONS,
    client=None,
) -> PaperIngestionResult:
    papers, query_url = fetch_arxiv_papers_for_date(
        submitted_date,
        categories=categories,
        max_results=max_results,
        timeout_seconds=timeout_seconds,
        retries=retries,
        request_delay_seconds=request_delay_seconds,
        compute_embeddings=compute_embeddings,
        embedding_model=embedding_model,
        embedding_dimensions=embedding_dimensions,
    )
    inserted_papers = upsert_papers(papers, client=client)
    inserted_embeddings = upsert_paper_embeddings(
        papers,
        inserted_papers,
        client=client,
    )

    return PaperIngestionResult(
        query_url=query_url,
        fetched_count=len(papers),
        inserted_count=len(inserted_papers),
        papers=inserted_papers,
        embedded_count=len(inserted_embeddings),
        embeddings_skipped=not compute_embeddings,
    )


def fetch_arxiv_papers_for_date(
    submitted_date: date,
    *,
    categories: Iterable[str] = DEFAULT_CATEGORIES,
    max_results: int = DEFAULT_MAX_RESULTS,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    retries: int = DEFAULT_RETRIES,
    request_delay_seconds: int = DEFAULT_REQUEST_DELAY_SECONDS,
    compute_embeddings: bool = False,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    embedding_dimensions: int = DEFAULT_EMBEDDING_DIMENSIONS,
) -> tuple[list[ArxivPaper], str]:
    if timeout_seconds < 1:
        raise ValueError("timeout_seconds must be at least 1")
    if retries < 0:
        raise ValueError("retries must not be negative")
    if request_delay_seconds < 0:
        raise ValueError("request_delay_seconds must not be negative")

    query_url = build_arxiv_query_url(
        submitted_date,
        categories=categories,
        max_results=max_results,
    )
    print(f"Query URL: {query_url}")
    request = Request(
        query_url,
        headers={"User-Agent": "paper-arxiv-services/0.1"},
    )

    last_error = None
    attempts_made = 0
    for attempt in range(retries + 1):
        attempts_made = attempt + 1
        try:
            _wait_for_arxiv_rate_limit(request_delay_seconds)
            with urlopen(request, timeout=timeout_seconds) as response:
                xml_bytes = response.read()
            papers = parse_arxiv_feed(xml_bytes)
            if compute_embeddings:
                papers = embed_arxiv_papers(
                    papers,
                    embedding_model=embedding_model,
                    embedding_dimensions=embedding_dimensions,
                )
            return papers, query_url
        except HTTPError as exc:
            last_error = exc
            if exc.code == 429:
                print(
                    "arXiv returned HTTP 429 Too Many Requests; "
                    "stop retrying and wait before running again.",
                    file=sys.stderr,
                )
                break
        except TimeoutError as exc:
            last_error = exc
        except OSError as exc:
            last_error = exc

        if attempt < retries:
            print(
                "arXiv fetch attempt "
                f"{attempt + 1}/{retries + 1} failed: {last_error}; retrying...",
                file=sys.stderr,
            )
            time_module.sleep(min(2 ** attempt, 5))

    raise RuntimeError(
        f"arXiv API request failed after {attempts_made} attempt(s): {last_error}"
    ) from last_error


def _wait_for_arxiv_rate_limit(request_delay_seconds: int) -> None:
    if request_delay_seconds == 0:
        _record_arxiv_request_time()
        return

    now = time_module.monotonic()
    last_request_time = _read_last_arxiv_request_time()
    if last_request_time is not None:
        elapsed = now - last_request_time
        if elapsed < request_delay_seconds:
            sleep_seconds = request_delay_seconds - elapsed
            print(
                f"waiting {sleep_seconds:.1f}s to respect arXiv request delay...",
                file=sys.stderr,
            )
            time_module.sleep(sleep_seconds)

    _record_arxiv_request_time()


def _read_last_arxiv_request_time() -> Optional[float]:
    try:
        return float(ARXIV_LAST_REQUEST_PATH.read_text().strip())
    except (OSError, ValueError):
        return None


def _record_arxiv_request_time() -> None:
    try:
        ARXIV_LAST_REQUEST_PATH.write_text(str(time_module.monotonic()))
    except OSError:
        pass


def build_arxiv_query_url(
    submitted_date: date,
    *,
    categories: Iterable[str] = DEFAULT_CATEGORIES,
    max_results: int = DEFAULT_MAX_RESULTS,
) -> str:
    normalized_categories = _normalize_categories(categories)
    if max_results < 1:
        raise ValueError("max_results must be at least 1")

    start_of_day = datetime.combine(submitted_date, time.min, tzinfo=timezone.utc)
    end_of_day = datetime.combine(submitted_date, time(23, 59), tzinfo=timezone.utc)
    category_query = " OR ".join(f"cat:{category}" for category in normalized_categories)
    search_query = (
        f"({category_query}) AND "
        f"submittedDate:[{_format_arxiv_date(start_of_day)} TO "
        f"{_format_arxiv_date(end_of_day)}]"
    )
    params = {
        "search_query": search_query,
        "start": 0,
        "max_results": max_results,
        "sortBy": DEFAULT_SORT_BY,
        "sortOrder": DEFAULT_SORT_ORDER,
    }

    return f"{ARXIV_API_URL}?{urlencode(params)}"


def parse_arxiv_feed(xml_bytes: bytes) -> list[ArxivPaper]:
    root = ET.fromstring(xml_bytes)
    error = _feed_error(root)
    if error:
        raise ValueError(f"arXiv API error: {error}")

    papers = []
    for entry in root.findall(f"{ATOM_NS}entry"):
        source_url = _text(entry, "id")
        if not source_url:
            continue

        source_id = _source_id_from_url(source_url)
        categories = [
            category.attrib["term"]
            for category in entry.findall(f"{ATOM_NS}category")
            if category.attrib.get("term")
        ]

        papers.append(
            ArxivPaper(
                source_id=source_id,
                title=_normalize_whitespace(_text(entry, "title") or ""),
                abstract=_optional_normalized(_text(entry, "summary")),
                authors_text=_authors_text(entry),
                categories=categories,
                source_url=source_url,
                pdf_url=_pdf_url(entry),
                published_at=_text(entry, "published"),
                source_updated_at=_text(entry, "updated"),
            )
        )

    return papers


def upsert_papers(papers: Iterable[ArxivPaper], *, client=None) -> list[dict]:
    rows = [_paper_to_row(paper) for paper in papers]
    if not rows:
        return []

    if client is None:
        from app.supabase.db import get_or_create_service_supabase_client

        supabase_client = get_or_create_service_supabase_client()
    else:
        supabase_client = client
    response = (
        supabase_client.table("papers")
        .upsert(rows, on_conflict="source,source_id")
        .execute()
    )

    return response.data or []


def get_or_create_openai_client():
    global service_openai_client

    if service_openai_client is None:
        load_dotenv()
        load_dotenv(OPENAI_ENV_PATH)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required for paper embeddings")

        from openai import OpenAI

        service_openai_client = OpenAI(api_key=api_key)

    return service_openai_client


def embed_arxiv_papers(
    papers: list[ArxivPaper],
    *,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    embedding_dimensions: int = DEFAULT_EMBEDDING_DIMENSIONS,
) -> list[ArxivPaper]:
    if not papers:
        return []

    openai_client = get_or_create_openai_client()

    embedded_papers = list(papers)
    for start in range(0, len(papers), DEFAULT_EMBEDDING_BATCH_SIZE):
        batch = papers[start:start + DEFAULT_EMBEDDING_BATCH_SIZE]
        embedded_texts = [_paper_to_embedded_text(paper) for paper in batch]
        response = openai_client.embeddings.create(
            model=embedding_model,
            input=embedded_texts,
            dimensions=embedding_dimensions,
            encoding_format="float",
        )

        for embedding_data in response.data:
            paper_index = start + embedding_data.index
            embedded_papers[paper_index] = replace(
                embedded_papers[paper_index],
                embedding=embedding_data.embedding,
                embedded_text=embedded_texts[embedding_data.index],
                embedding_model=embedding_model,
            )

    return embedded_papers


def upsert_paper_embeddings(
    papers: Iterable[ArxivPaper],
    persisted_papers: Iterable[dict],
    *,
    client=None,
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

    if not rows:
        return []

    if client is None:
        from app.supabase.db import get_or_create_service_supabase_client

        supabase_client = get_or_create_service_supabase_client()
    else:
        supabase_client = client

    response = (
        supabase_client.table("paper_embeddings")
        .upsert(rows, on_conflict="paper_id")
        .execute()
    )

    return response.data or []


def _paper_to_embedded_text(paper: ArxivPaper) -> str:
    sections = [f"Title: {paper.title}"]
    if paper.abstract:
        sections.append(f"Abstract: {paper.abstract}")
    if paper.authors_text:
        sections.append(f"Authors: {paper.authors_text}")
    if paper.categories:
        sections.append(f"Categories: {', '.join(paper.categories)}")
    return "\n".join(sections)


def _paper_to_row(paper: ArxivPaper) -> dict:
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

def _normalize_categories(categories: Iterable[str]) -> list[str]:
    normalized = []
    for category in categories:
        clean_category = category.strip()
        if not clean_category:
            continue
        normalized.append(clean_category)

    if not normalized:
        raise ValueError("at least one arXiv category is required")

    return normalized


def _format_arxiv_date(value: datetime) -> str:
    return value.strftime("%Y%m%d%H%M")


def _text(parent: ET.Element, tag: str) -> Optional[str]:
    child = parent.find(f"{ATOM_NS}{tag}")
    if child is None or child.text is None:
        return None
    return child.text.strip()


def _optional_normalized(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    normalized = _normalize_whitespace(value)
    return normalized or None


def _normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _authors_text(entry: ET.Element) -> Optional[str]:
    authors = []
    for author in entry.findall(f"{ATOM_NS}author"):
        author_name = _text(author, "name")
        if author_name:
            authors.append(_normalize_whitespace(author_name))
    return ", ".join(authors) if authors else None


def _pdf_url(entry: ET.Element) -> Optional[str]:
    for link in entry.findall(f"{ATOM_NS}link"):
        if link.attrib.get("title") == "pdf":
            return link.attrib.get("href")
    return None


def _source_id_from_url(source_url: str) -> str:
    source_id = source_url.rstrip("/").rsplit("/", 1)[-1]
    return re.sub(r"v\d+$", "", source_id)


def _feed_error(root: ET.Element) -> Optional[str]:
    total_results = root.find(f"{OPENSEARCH_NS}totalResults")
    if total_results is None or total_results.text != "1":
        return None

    entry = root.find(f"{ATOM_NS}entry")
    if entry is None:
        return None

    title = _text(entry, "title")
    if title != "Error":
        return None

    return _text(entry, "summary") or "unknown error"

# Don't delete the comments below
# [GenAI Usage 1] Response ends
# [GenAI Usage 1] Reflection
# I inspect the code carefully via a top-down approach. I first inspect 3 key functions fetch_arxiv_papers_for_date, ingest_today_cs_ai_papers, build_arxiv_query_url. 
# They are the beacons defining the whole workflow: prepare for query, calling arxiv api to get results, and ingest result into supabase. 
# Then, I look into the ingestion logic to make sure the upsert logic is correct. And they indeed look very clean. 
# Finally, I look into the helper functions like parsing author name, url, etc. 
# In all, since my prompt is clear, the codex written good-quality code that shall be accepted 
# However, this is just for the first version of paper ingestion pipeline, which means it is far from perfect. 
# For instance, it only focuses on one domain (cs.ai), does not have parallelism, and does not have a real embedding model. 
# We will handle in a later version

# [GenAI Usage 1] Debugging Reflection
# I got the 429 -- too many requests error. and then realize there must be some rate-limiting issue. So I searched on Google and found the 3s-retry rule. 
# I tell the rule to codex and ask it fix the error I got. Inspecting the code, the _wait_for_arxiv_rate_limit function achieves the purpose.
# This code can be accepted for now. In the future, we might take further, smoother action for this.

# [GenAI Usage 2] Response ends
# [GenAI Usage 2] Reflection: To add embedding feature to this existing codebase that is complex and large, I inspected the original code carefully with
# a top-down approach looking for beacon functions such as the core function that fetches and paper and persists the fetch result to the database. Then,
# I provided a clear specification to Codex to ingetrate embedding computation. Lastly, after Codex's completion, I thoroughly examined the modified code
# to ensure it met my specification and is correct.
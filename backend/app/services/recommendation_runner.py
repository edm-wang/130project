from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Iterable, Optional, Tuple

from supabase import Client

from app.services.paper_ingestion import get_or_create_openai_client
from app.services.recommendation import (
    CandidatePaper,
    InterestEmbedding,
    RecGenParams,
    UserPaperSignal,
    generate_recommendations,
)

#[GenAI Usage] Prompt: the code below is the result of a series of conversations with Codex. The specific conversation can be found in
# genai_usage_appendix\recommendation_runner_setup.md. The overall content of the conversation involves me proposing a detailed 
# core recommendation algorithm with clearly defined steps and parameters required in each step, and then I asked codex to generate 
# relevant parameters classes to encapsulate the algorithm configuration and runner functions to prepare relevant data (such as 
# different types of embeddings) for the core recommendation algorithm.
#[GenAI Usage] LLM response begins

def generate_recommendations_for_user(
    client: Client,
    user,
    params_template: Optional[RecGenParams] = None,
) -> Tuple[dict, list[dict]]:
    user_id = str(user.id)
    params_template = params_template or RecGenParams()
    active_interests = _fetch_active_interests(client, user_id)
    saved_paper_rows = _fetch_saved_paper_rows(client, user_id)
    feedback_rows = _fetch_feedback_rows(client, user_id)
    user_snapshot_hash = generate_user_snapshot_hash(
        user_id=user_id,
        interests=active_interests,
        saved_papers=saved_paper_rows,
        feedback_rows=feedback_rows,
    )
    batch = _create_pending_batch(
        client,
        user_id,
        params_template,
        user_snapshot_hash=user_snapshot_hash,
    )

    try:
        interest_embeddings = _embed_interests(active_interests, params_template)
        candidate_papers = _retrieve_candidate_papers(
            client,
            interest_embeddings,
            params_template,
        )
        saved_papers = _hydrate_user_paper_signals(client, saved_paper_rows)
        upvoted_papers, downvoted_papers = _feedback_rows_to_paper_signals(
            client,
            feedback_rows,
        )

        params = replace(
            params_template,
            interests=interest_embeddings,
            candidate_papers=candidate_papers,
            saved_papers=saved_papers,
            upvoted_papers=upvoted_papers,
            downvoted_papers=downvoted_papers,
        )
        recommendation_rows = generate_recommendations(params)
        inserted_recommendations = _insert_recommendations(
            client,
            batch["id"],
            recommendation_rows,
        )
        completed_batch = _complete_batch(
            client,
            batch["id"],
            params,
            candidate_count=len(candidate_papers),
            final_count=len(inserted_recommendations),
        )

        recommendation_items =  _fetch_batch_recommendations(client, batch["id"])
        # with open("./recommendation_endpoint_logs.jsonl", "w") as f:
        #     for idx, item in enumerate(recommendation_items):
        #         f.write(json.dumps(item, indent=4))
        #         f.write("\n")

        return completed_batch, recommendation_items
    except Exception as exc:
        _fail_batch(client, batch["id"], exc)
        raise


def _create_pending_batch(
    client: Client,
    user_id: str,
    params: RecGenParams,
    *,
    user_snapshot_hash: str,
) -> dict:
    response = (
        client.table("recommendation_batches")
        .insert(
            {
                "user_id": user_id,
                "status": "pending",
                "algorithm_version": params.algorithm_version,
                "parameters": params.to_batch_parameters(),
                "user_snapshot_hash": user_snapshot_hash,
            }
        )
        .execute()
    )

    if not response.data:
        raise RuntimeError("Failed to create recommendation batch")

    return response.data[0]


def _complete_batch(
    client: Client,
    batch_id: str,
    params: RecGenParams,
    *,
    candidate_count: int,
    final_count: int,
) -> dict:
    response = (
        client.table("recommendation_batches")
        .update(
            {
                "status": "completed",
                "parameters": params.to_batch_parameters(),
                "candidate_count": candidate_count,
                "final_count": final_count,
                "completed_at": _utc_now_iso(),
                "error_message": None,
            }
        )
        .eq("id", batch_id)
        .execute()
    )

    if not response.data:
        raise RuntimeError("Failed to complete recommendation batch")

    return response.data[0]


def _fail_batch(client: Client, batch_id: str, exc: Exception) -> None:
    (
        client.table("recommendation_batches")
        .update(
            {
                "status": "failed",
                "completed_at": _utc_now_iso(),
                "error_message": str(exc),
            }
        )
        .eq("id", batch_id)
        .execute()
    )


def _fetch_active_interests(client: Client, user_id: str) -> list[dict]:
    response = (
        client.table("research_interests")
        .select("id, interest_type, value, normalized_value, preference_weight")
        .eq("user_id", user_id)
        .eq("is_active", True)
        .order("created_at")
        .execute()
    )
    return response.data or []

def _stable_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

def generate_recommentation_parameter_hash(params: RecGenParams | dict) -> str:
    parameters = params.to_batch_parameters() if isinstance(params, RecGenParams) else params
    stable_parameters = {
        key: value
        for key, value in parameters.items()
        if key != "input_counts"
    }
    return _stable_hash(stable_parameters)

def generate_user_snapshot_hash(
    *,
    user_id: str,
    interests: list[dict],
    saved_papers: list[dict],
    feedback_rows: list[dict],
) -> str:
    snapshot = {
        "user_id": user_id,
        "interests": sorted(
            [
                {
                    "interest_type": row.get("interest_type"),
                    "normalized_value": row.get("normalized_value")
                    or str(row.get("value", "")).strip().lower(),
                    "preference_weight": str(row.get("preference_weight", "1.0")),
                }
                for row in interests
            ],
            key=lambda row: (
                row["interest_type"] or "",
                row["normalized_value"] or "",
                row["preference_weight"] or "",
            ),
        ),
        "saved_paper_ids": sorted(
            str(row["paper_id"]) for row in saved_papers if row.get("paper_id")
        ),
        "upvoted_paper_ids": sorted(
            str(row["paper_id"])
            for row in feedback_rows
            if row.get("paper_id") and row.get("feedback_value") == 1
        ),
        "downvoted_paper_ids": sorted(
            str(row["paper_id"])
            for row in feedback_rows
            if row.get("paper_id") and row.get("feedback_value") == -1
        ),
    }
    return _stable_hash(snapshot)

def _embed_interests(
    interests: list[dict],
    params: RecGenParams,
) -> list[InterestEmbedding]:
    if not interests:
        return []

    embedded_texts = [_interest_to_embedded_text(interest) for interest in interests]
    openai_client = get_or_create_openai_client()
    response = openai_client.embeddings.create(
        model=params.embedding_model,
        input=embedded_texts,
        dimensions=params.embedding_dimensions,
        encoding_format="float",
    )

    embedded_interests = []
    for embedding_data in response.data:
        interest = interests[embedding_data.index]
        embedded_interests.append(
            InterestEmbedding(
                interest_id=interest["id"],
                interest_type=interest["interest_type"],
                value=interest["value"],
                preference_weight=_to_float(interest.get("preference_weight"), 1.0),
                embedding=embedding_data.embedding,
                embedded_text=embedded_texts[embedding_data.index],
                embedding_model=params.embedding_model,
            )
        )

    return embedded_interests


def _retrieve_candidate_papers(
    client: Client,
    interests: list[InterestEmbedding],
    params: RecGenParams,
) -> list[CandidatePaper]:
    candidates_by_id: dict[str, CandidatePaper] = {}

    for interest in interests:
        rows = _match_paper_embeddings(client, interest, params)
        for row in rows[:params.keep_top_n_per_interest]:
            candidate = _candidate_from_row(row, interest)
            if candidate is None:
                continue

            existing = candidates_by_id.get(candidate.paper_id)
            if existing is None:
                candidates_by_id[candidate.paper_id] = candidate
            else:
                existing.interest_similarities.update(candidate.interest_similarities)

    return list(candidates_by_id.values())


def _match_paper_embeddings(
    client: Client,
    interest: InterestEmbedding,
    params: RecGenParams,
) -> list[dict]:
    response = (
        client.rpc(
            "match_paper_embeddings",
            {
                "query_embedding": interest.embedding,
                "match_count": params.retrieval_top_n,
            },
        )
        .execute()
    )
    matches = response.data or []
    paper_ids = [str(row["paper_id"]) for row in matches if row.get("paper_id")]
    embeddings_by_id = _fetch_embeddings_by_paper_id(client, paper_ids)
    papers_by_id = _fetch_papers_by_id(client, paper_ids)

    rows = []
    for match in matches:
        paper_id = str(match.get("paper_id") or "")
        embedding_row = embeddings_by_id.get(paper_id)
        if not paper_id or embedding_row is None:
            continue

        rows.append(
            {
                "paper_id": paper_id,
                "similarity": match.get("similarity", 0),
                "embedding": embedding_row.get("embedding"),
                "embedding_model": embedding_row.get("embedding_model"),
                "embedded_text": embedding_row.get("embedded_text"),
                "paper": papers_by_id.get(paper_id, {}),
            }
        )

    return rows


def _candidate_from_row(
    row: dict,
    interest: InterestEmbedding,
) -> Optional[CandidatePaper]:
    paper = row.get("paper") or {}
    paper_id = str(row.get("paper_id") or paper.get("id") or "")
    embedding = _parse_embedding(row.get("embedding"))

    if not paper_id or embedding is None:
        return None

    return CandidatePaper(
        paper_id=paper_id,
        paper=paper,
        embedding=embedding,
        embedded_text=row.get("embedded_text") or "",
        embedding_model=row.get("embedding_model") or "",
        interest_similarities={
            interest.interest_id: _to_float(row.get("similarity"), 0.0)
        },
    )


def _fetch_saved_paper_signals(client: Client, user_id: str) -> list[UserPaperSignal]:
    return _hydrate_user_paper_signals(client, _fetch_saved_paper_rows(client, user_id))


def _fetch_saved_paper_rows(client: Client, user_id: str) -> list[dict]:
    response = (
        client.table("saved_papers")
        .select("paper_id, created_at, updated_at")
        .eq("user_id", user_id)
        .execute()
    )
    return response.data or []


def _fetch_feedback_paper_signals(
    client: Client,
    user_id: str,
) -> tuple[list[UserPaperSignal], list[UserPaperSignal]]:
    return _feedback_rows_to_paper_signals(
        client,
        _fetch_feedback_rows(client, user_id),
    )


def _fetch_feedback_rows(client: Client, user_id: str) -> list[dict]:
    response = (
        client.table("recommendation_feedback")
        .select("paper_id, feedback_value, created_at, updated_at")
        .eq("user_id", user_id)
        .execute()
    )
    return response.data or []


def _feedback_rows_to_paper_signals(
    client: Client,
    feedback_rows: list[dict],
) -> tuple[list[UserPaperSignal], list[UserPaperSignal]]:
    upvoted_rows = [row for row in feedback_rows if row.get("feedback_value") == 1]
    downvoted_rows = [row for row in feedback_rows if row.get("feedback_value") == -1]

    return (
        _hydrate_user_paper_signals(client, upvoted_rows),
        _hydrate_user_paper_signals(client, downvoted_rows),
    )


def _hydrate_user_paper_signals(
    client: Client,
    rows: list[dict],
) -> list[UserPaperSignal]:
    paper_ids = sorted({str(row["paper_id"]) for row in rows if row.get("paper_id")})
    if not paper_ids:
        return []

    embeddings_by_id = _fetch_embeddings_by_paper_id(client, paper_ids)
    papers_by_id = _fetch_papers_by_id(client, paper_ids)
    signals = []

    for row in rows:
        paper_id = str(row.get("paper_id") or "")
        embedding_row = embeddings_by_id.get(paper_id)
        embedding = _parse_embedding(
            embedding_row.get("embedding") if embedding_row else None
        )

        if not paper_id or embedding_row is None or embedding is None:
            continue

        signals.append(
            UserPaperSignal(
                paper_id=paper_id,
                paper=papers_by_id.get(paper_id, {}),
                embedding=embedding,
                embedded_text=embedding_row.get("embedded_text") or "",
                embedding_model=embedding_row.get("embedding_model") or "",
                last_interaction_at=row.get("updated_at") or row.get("created_at"),
            )
        )

    return signals


def _fetch_embeddings_by_paper_id(
    client: Client,
    paper_ids: Iterable[str],
) -> dict[str, dict]:
    paper_ids = list(paper_ids)
    if not paper_ids:
        return {}

    response = (
        client.table("paper_embeddings")
        .select("paper_id, embedding_model, embedding, embedded_text")
        .in_("paper_id", paper_ids)
        .execute()
    )
    return {str(row["paper_id"]): row for row in response.data or []}


def _fetch_papers_by_id(client: Client, paper_ids: Iterable[str]) -> dict[str, dict]:
    paper_ids = list(paper_ids)
    if not paper_ids:
        return {}

    response = client.table("papers").select("*").in_("id", paper_ids).execute()
    return {str(row["id"]): row for row in response.data or []}


def _insert_recommendations(
    client: Client,
    batch_id: str,
    recommendation_rows: list[dict[str, Any]],
) -> list[dict]:
    if not recommendation_rows:
        return []

    rows = []
    for index, recommendation in enumerate(recommendation_rows, start=1):
        rows.append(
            {
                "batch_id": batch_id,
                "paper_id": recommendation["paper_id"],
                "rank_position": recommendation.get("rank_position", index),
                "final_score": recommendation.get("final_score", 0),
                "interest_score": recommendation.get("interest_score", 0),
                "saved_paper_score": recommendation.get("saved_paper_score", 0),
                "upvote_score": recommendation.get("upvote_score", 0),
                "downvote_penalty": recommendation.get("downvote_penalty", 0),
                "freshness_score": recommendation.get("freshness_score", 0),
                #TODO: (for teammate, codex please ignore) integrate explanation summary with LLM service
                "explanation_summary": recommendation.get("explanation_summary", ""),
            }
        )

    response = client.table("recommendations").insert(rows).execute()
    return response.data or []


def _fetch_batch_recommendations(client: Client, batch_id: str) -> list[dict]:
    response = (
        client.table("recommendations")
        .select("*, paper:papers(*)")
        .eq("batch_id", batch_id)
        .order("rank_position", desc=False)
        .execute()
    )
    return response.data or []


def _interest_to_embedded_text(interest: dict) -> str:
    return "\n".join(
        [
            f"Interest Type: {interest.get('interest_type', '')}",
            f"Interest: {interest.get('value', '')}",
        ]
    )


def _parse_embedding(value: Any) -> Optional[list[float]]:
    if value is None:
        return None
    if isinstance(value, list):
        return [float(item) for item in value]
    if isinstance(value, str):
        clean_value = value.strip().strip("[]")
        if not clean_value:
            return []
        return [float(item) for item in clean_value.split(",")]
    return None


def _to_float(value: Any, default: float) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

# [GenAI Usage] LLM response end
# [GenAI Reflection] I have provided a clear specification of the core recommendation algorithm to Codex and explain a clear defined structure 
# of how we should separate the concerns of handling the recommendation generation request from frontend, generating necessary data for the
# core recommendation algorithm, and the execution of the core recommendation algorithm. In addition, I have carefully examined the code to
# ensure it is correct and had detailed subsequent conversation with Codex to modify specific segments of the code that deviated from my 
# specification or introduced unnecessary complexity or code bloating.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from math import sqrt
import re
from typing import Any, Literal, Optional

from app.services.embedding_config import (
    DEFAULT_EMBEDDING_DIMENSIONS,
    DEFAULT_EMBEDDING_MODEL,
)

DecayType = Literal["half_life", "reciprocal"]

@dataclass
class DecayModificationConfig:
    parameter: float = 0.0
    enabled: bool = False

@dataclass
class DecayConfig:
    decay_type: DecayType = "half_life"
    half_life_days: float = 30.0
    tau_days: float = 30.0
    grace_days: float = 0.0
    floor: DecayModificationConfig = field(default_factory=DecayModificationConfig)
    plateau: DecayModificationConfig = field(default_factory=DecayModificationConfig)

DEFAULT_USER_INTEREST_TO_PREFERENCE_WEIGHTS = {
    "topic": 1.0,
    "field": 1.0,
    "keyword": 1.0,
    "author": 1.0,
}

#[GenAI Usage] Prompt: the code below is the result of a series of conversations with Codex. The specific conversation can be found in
# genai_usage_appendix\recommendation_runner_setup.md. The overall content of the conversation involves me proposing a detailed
# core recommendation algorithm with clearly defined steps and parameters required in each step, and then I asked codex to generate
# relevant parameters classes to encapsulate the algorithm configuration and runner functions to prepare relevant data (such as
# different types of embeddings) for the core recommendation algorithm.
#[GenAI Usage] LLM response begins


@dataclass
class InterestEmbedding:
    interest_id: str
    interest_type: str
    value: str
    preference_weight: float
    embedding: list[float]
    embedded_text: str
    embedding_model: str


@dataclass
class CandidatePaper:
    paper_id: str
    paper: dict[str, Any]
    embedding: list[float]
    embedded_text: str
    embedding_model: str
    interest_similarities: dict[str, float] = field(default_factory=dict)


@dataclass
class UserPaperSignal:
    paper_id: str
    paper: dict[str, Any]
    embedding: list[float]
    embedded_text: str
    embedding_model: str
    last_interaction_at: Optional[str] = None


@dataclass
class RecGenParams:
    algorithm_version: str = "multi_vector_v2"
    embedding_model: str = DEFAULT_EMBEDDING_MODEL
    embedding_dimensions: int = DEFAULT_EMBEDDING_DIMENSIONS
    retrieval_top_n: int = 200
    keep_top_n_per_interest: int = 125
    interest_score_mix_eta: float = 0.15
    saved_top_k: int = 5
    upvote_top_k: int = 10
    downvote_top_k: int = 10
    interest_weight: float = 1.0
    saved_paper_weight: float = 0.2
    upvote_weight: float = 0.6
    downvote_weight: float = 0.6
    freshness_weight: float = 0.1
    downvote_penalty_cap: float = 1.0
    downvote_similarity_threshold: float = 0.65
    saved_decay: DecayConfig = field(
        default_factory=lambda: DecayConfig(half_life_days=10.0)
    )
    upvote_decay: DecayConfig = field(
        default_factory=lambda: DecayConfig(half_life_days=10.0)
    )
    downvote_decay: DecayConfig = field(
        default_factory=lambda: DecayConfig(half_life_days=10.0)
    )
    freshness_decay: DecayConfig = field(
        default_factory=lambda: DecayConfig(
            decay_type="half_life",
            half_life_days=30.0,
            plateau=DecayModificationConfig(parameter=14.0, enabled=True),
        )
    )
    enable_diversity_filtering: bool = False
    diversity_gamma: float = 0.8
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    interests: list[InterestEmbedding] = field(default_factory=list)
    candidate_papers: list[CandidatePaper] = field(default_factory=list)
    saved_papers: list[UserPaperSignal] = field(default_factory=list)
    upvoted_papers: list[UserPaperSignal] = field(default_factory=list)
    downvoted_papers: list[UserPaperSignal] = field(default_factory=list)

    def to_batch_parameters(self) -> dict[str, Any]:
        return {
            "embedding_model": self.embedding_model,
            "embedding_dimensions": self.embedding_dimensions,
            "retrieval_top_n": self.retrieval_top_n,
            "keep_top_n_per_interest": self.keep_top_n_per_interest,
            "interest_score_mix_eta": self.interest_score_mix_eta,
            "top_k": {
                "saved": self.saved_top_k,
                "upvote": self.upvote_top_k,
                "downvote": self.downvote_top_k,
            },
            "research_interest_weights": {
                "field": DEFAULT_USER_INTEREST_TO_PREFERENCE_WEIGHTS["field"],
                "topic": DEFAULT_USER_INTEREST_TO_PREFERENCE_WEIGHTS["topic"],
                "author": DEFAULT_USER_INTEREST_TO_PREFERENCE_WEIGHTS["author"],
                "keyword": DEFAULT_USER_INTEREST_TO_PREFERENCE_WEIGHTS["keyword"]
            },
            "weights": {
                "interest": self.interest_weight,
                "saved_paper": self.saved_paper_weight,
                "upvote": self.upvote_weight,
                "downvote": self.downvote_weight,
                "freshness": self.freshness_weight,
            },
            "downvote_penalty_cap": self.downvote_penalty_cap,
            "downvote_similarity_threshold": self.downvote_similarity_threshold,
            "decay": {
                "saved": asdict(self.saved_decay),
                "upvote": asdict(self.upvote_decay),
                "downvote": asdict(self.downvote_decay),
                "freshness": asdict(self.freshness_decay),
            },
            "diversity": {
                "enabled": self.enable_diversity_filtering,
                "gamma": self.diversity_gamma,
            },
            "input_counts": {
                "interests": len(self.interests),
                "candidate_papers": len(self.candidate_papers),
                "saved_papers": len(self.saved_papers),
                "upvoted_papers": len(self.upvoted_papers),
                "downvoted_papers": len(self.downvoted_papers),
            },
        }

# [GenAI Usage] LLM response end
# [GenAI Reflection] I have provided a clear specification of the core recommendation algorithm to Codex and explain a clear defined structure
# of how we should separate the concerns of handling the recommendation generation request from frontend, generating necessary data for the
# core recommendation algorithm, and the execution of the core recommendation algorithm. In addition, I have carefully examined the code to
# ensure it is correct and had detailed subsequent conversation with Codex to modify specific segments of the code that deviated from my
# specification or introduced unnecessary complexity or code bloating.



def _clamp_unit_interval(val: float) -> float:
    return max(0.0, min(1.0, val))


def _decay(val: float, config: DecayConfig) -> float:
    age = max(0.0, float(val))

    if config.plateau.enabled:
        plateau_days = max(0.0, float(config.plateau.parameter))
        age = max(0.0, age - plateau_days)

    if config.decay_type == "half_life":
        if config.half_life_days <= 0:
            raise ValueError("half_life_days must be positive.")
        score = 2 ** (-age / config.half_life_days)
    elif config.decay_type == "reciprocal":
        if config.tau_days <= 0:
            raise ValueError("tau_days must be positive.")
        score = 1 / (1 + age / config.tau_days)
    else:
        raise ValueError(f"Unrecognized decay function type: {config.decay_type}")

    if config.floor.enabled:
        floor = _clamp_unit_interval(float(config.floor.parameter))
        score = floor + (1 - floor) * score

    return _clamp_unit_interval(score)

def _normalize(val: float, refs: list[float], method: Literal["ratio", "min-max"], epsilon: float = 1e-8) -> float:
    if not refs:
        return 0.0

    if(method == "ratio"):
        max_ref = max(refs)
        max_val = max_ref if abs(max_ref) > epsilon else epsilon
        return val / max_val

    elif(method == "min-max"):
        max_val = max(refs)
        min_val = min(refs)
        interval = (max_val - min_val) if (max_val - min_val) != 0 else epsilon
        return (val - min_val) / interval

    else:
        raise ValueError(f"Unrecognized normalization method: {method}")

def _mean(vals: list[float], weights: Optional[list[float]] = None) -> float:
    if(len(vals) == 0):
        return 0.0

    if weights is None:
        return sum(vals) / len(vals)

    if(len(vals) != len(weights)):
        raise ValueError("vals and weights must have the same length.")

    total_weight = sum(weights)
    if total_weight == 0:
        return 0.0

    return sum(val * weight for val, weight in zip(vals, weights)) / total_weight

def _similarity(
        embed_a: list[float],
        embed_b: list[float],
    ) -> float:
    if not embed_a or not embed_b or len(embed_a) != len(embed_b):
        return 0.0

    dot_product = sum(a * b for a, b in zip(embed_a, embed_b))
    norm_a = sqrt(sum(a * a for a in embed_a))
    norm_b = sqrt(sum(b * b for b in embed_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    cosine_similarity = dot_product / (norm_a * norm_b)
    return _clamp_unit_interval((1 + cosine_similarity) / 2)


def _normalize_author_name(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip()).casefold()


def _paper_has_author(paper: dict[str, Any], author_name: str) -> bool:
    normalized_author_name = _normalize_author_name(author_name)
    if not normalized_author_name:
        return False

    authors_text = str(paper.get("authors_text") or "")
    normalized_paper_authors = set()
    for author in authors_text.split(","):
        normalized_paper_author = _normalize_author_name(author)
        if normalized_paper_author:
            normalized_paper_authors.add(normalized_paper_author)

    return normalized_author_name in normalized_paper_authors


def _interest_score(
        paper: CandidatePaper,
        params: RecGenParams
    ) -> float:
    if not params.interests:
        return 0.0

    interest_id_to_weights = {
        interest.interest_id: max(0.0, float(interest.preference_weight))
        for interest in params.interests
    }
    unnormalized_interest_weights = list(interest_id_to_weights.values())

    interest_id_to_normalized_weights = {
        interest.interest_id: _normalize(
            val=interest_id_to_weights[interest.interest_id],
            refs=unnormalized_interest_weights,
            method="ratio"
        ) for interest in params.interests
    }

    interest_id_to_similarities = {}
    for interest in params.interests:
        if interest.interest_type == "author":
            similarity = (
                1.0 if _paper_has_author(paper.paper, interest.value) else 0.0
            )
        else:
            similarity = _similarity(paper.embedding, interest.embedding)
            if similarity == 0.0 and interest.interest_id in paper.interest_similarities:
                similarity = _clamp_unit_interval(
                    float(paper.interest_similarities[interest.interest_id])
                )

        interest_id_to_similarities[interest.interest_id] = _clamp_unit_interval(
            float(similarity)
        )

    interest_max = max(
        interest_id_to_normalized_weights[interest_id] * similarity
        for interest_id, similarity in interest_id_to_similarities.items()
    )

    interest_weighted_mean = _mean(
        vals=list(interest_id_to_similarities.values()),
        weights=[
            interest_id_to_weights[interest_id]
            for interest_id in interest_id_to_similarities
        ],
    )

    eta = _clamp_unit_interval(params.interest_score_mix_eta)
    return (1 - eta) * interest_max + eta * interest_weighted_mean


def _parse_datetime(value: Optional[str | datetime]) -> Optional[datetime]:
    if value is None:
        return None

    if isinstance(value, datetime):
        parsed = value
    else:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)


def _age_days(now: datetime, value: Optional[str | datetime]) -> Optional[float]:
    parsed = _parse_datetime(value)
    if parsed is None:
        return None

    return max(0.0, (now - parsed).total_seconds() / 86400)

def _user_paper_signal_score(
        now: datetime,
        paper: CandidatePaper,
        signal_papers: list[UserPaperSignal],
        decay_config: DecayConfig,
        mean_top_k: int,
        clip_min: Optional[float]=None,
        clip_max: Optional[float]=None,
        valid_sim_min_threshold: float=0.0
        ) -> float:
    if not signal_papers or mean_top_k <= 0:
        return 0.0

    decay_sims = []
    for signal_paper in signal_papers:
        similarity = _similarity(paper.embedding, signal_paper.embedding)
        if similarity < valid_sim_min_threshold:
            similarity = 0.0

        age = _age_days(now, signal_paper.last_interaction_at)
        if age is None:
            continue

        decay_sims.append(similarity * _decay(age, decay_config))

    sorted_decay_sims = sorted(decay_sims, reverse=True)

    mean = _mean(sorted_decay_sims[:mean_top_k])

    if clip_min is not None:
        mean = max(clip_min, mean)
    if clip_max is not None:
        mean = min(clip_max, mean)

    return mean

def _freshness_score(now: datetime, paper: CandidatePaper, decay_config: DecayConfig) -> float:
    age = _age_days(now, paper.paper.get("published_at"))
    if age is None:
        return 0.0

    return _decay(age, decay_config)


def _apply_diversity_filtering(
    rows: list[dict[str, Any]],
    embeddings_by_paper_id: dict[str, list[float]],
    params: RecGenParams,
) -> list[dict[str, Any]]:
    gamma = _clamp_unit_interval(params.diversity_gamma)
    selected: list[dict[str, Any]] = []
    remaining = rows[:]

    while remaining:
        if not selected:
            best_row = max(remaining, key=lambda row: row["final_score"])
        else:
            def mmr_score(row: dict[str, Any]) -> float:
                embedding = embeddings_by_paper_id.get(row["paper_id"], [])
                max_selected_similarity = max(
                    (
                        _similarity(
                            embedding,
                            embeddings_by_paper_id.get(selected_row["paper_id"], []),
                        )
                        for selected_row in selected
                    ),
                    default=0.0,
                )
                return (
                    gamma * row["final_score"]
                    - (1 - gamma) * max_selected_similarity
                )

            best_row = max(remaining, key=mmr_score)

        selected.append(best_row)
        remaining.remove(best_row)

    return selected

def generate_recommendations(params: RecGenParams) -> list[dict[str, Any]]:
    rows = []
    embeddings_by_paper_id = {}
    now = _parse_datetime(params.generated_at) or datetime.now(timezone.utc)

    for paper in params.candidate_papers:
        interest_score = _interest_score(paper, params)

        saved_paper_boost = _user_paper_signal_score(
            now=now,
            paper=paper,
            signal_papers=params.saved_papers,
            decay_config=params.saved_decay,
            mean_top_k=params.saved_top_k
        )

        upvote_paper_boost = _user_paper_signal_score(
            now=now,
            paper=paper,
            signal_papers=params.upvoted_papers,
            decay_config=params.upvote_decay,
            mean_top_k=params.upvote_top_k
        )

        downvote_paper_penalty = _user_paper_signal_score(
            now=now,
            paper=paper,
            signal_papers=params.downvoted_papers,
            decay_config=params.downvote_decay,
            mean_top_k=params.downvote_top_k,
            clip_max=params.downvote_penalty_cap,
            valid_sim_min_threshold=params.downvote_similarity_threshold
        )

        freshness_score = _freshness_score(
            now=now,
            paper=paper,
            decay_config=params.freshness_decay
        )

        weights = [
            params.interest_weight,
            params.saved_paper_weight,
            params.upvote_weight,
            -params.downvote_weight,
            params.freshness_weight
        ]
        scores = [
            interest_score,
            saved_paper_boost,
            upvote_paper_boost,
            downvote_paper_penalty,
            freshness_score
        ]
        final_score = sum(score * weight for score, weight in zip(scores, weights))

        rows.append({
            "paper_id": paper.paper_id,
            "final_score": final_score,
            "interest_score": interest_score,
            "saved_paper_score": saved_paper_boost,
            "upvote_score": upvote_paper_boost,
            "downvote_penalty": downvote_paper_penalty,
            "freshness_score": freshness_score,
        })
        embeddings_by_paper_id[paper.paper_id] = paper.embedding

    rows = sorted(rows, key=lambda row:row["final_score"], reverse=True)
    if params.enable_diversity_filtering:
        rows = _apply_diversity_filtering(rows, embeddings_by_paper_id, params)

    for idx, row in enumerate(rows, start=1):
        row["rank_position"] = idx

    return rows

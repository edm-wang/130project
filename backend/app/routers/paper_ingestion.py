from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional
import os

ingestion_router = APIRouter(prefix='/internal/jobs/paper-ingestion')

class IngestionJobPayload(BaseModel):
    target_date: Optional[date] = None
    categories: Optional[list[str]] = None
    max_results: int = Field(default=1000, gt=0, le=10000)

# Don't delete comments below
# [GenAI Usage] Codex Prompt: 
# I realize a problem right now -- when you define CRON JOB in vercel.json, it requires the end point is GET. However, it is defined as POST right now. Also the custom x-cron-job-secret header might be needed as well
# [GenAI Usage] LLM response begins:
def _verify_cron_secret(
    *,
    authorization: Optional[str],
) -> None:
    expected_cron_job_secret = os.getenv("CRON_SECRET")
    if expected_cron_job_secret is None:
        raise HTTPException(500, detail="Cron job secret is not specified")

    bearer_secret = None
    if isinstance(authorization, str) and authorization.startswith("Bearer "):
        bearer_secret = authorization[7:].strip()

    if bearer_secret != expected_cron_job_secret:
        raise HTTPException(401, detail="Invalid cron job secret")


def _run_paper_ingestion(payload: IngestionJobPayload):
    from app.services.ingestion_runner import run_paper_ingestion_cron

    return run_paper_ingestion_cron(
        target_date=payload.target_date,
        categories=payload.categories,
        max_results=payload.max_results
    )


@ingestion_router.get('')
def run_paper_ingestion_cron_job(
    target_date: Optional[date] = Query(default=None),
    categories: Optional[list[str]] = Query(default=None),
    max_results: int = Query(default=1000, gt=0, le=10000),
    authorization: Optional[str] = Header(default=None),
):
    _verify_cron_secret(
        authorization=authorization,
    )
    return _run_paper_ingestion(
        IngestionJobPayload(
            target_date=target_date,
            categories=categories,
            max_results=max_results,
        )
    )


@ingestion_router.post('')
def run_paper_ingestion_job(
    payload: IngestionJobPayload,
    authorization: Optional[str] = Header(default=None),
):
    _verify_cron_secret(
        authorization=authorization,
    )
    return _run_paper_ingestion(payload)
# Don't delete comments below
# [GenAI Usage] LLM response ends
# [GenAI Usage] Reflection: 
# The code successfully implements
# 1. verify cron secret by reading from .env
# 2. write a GET endpoint for cron job

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional
import os

ingestion_router = APIRouter(prefix='/internal/jobs/paper-ingestion')

class IngestionJobPayload(BaseModel):
    target_date: Optional[date] = None
    categories: Optional[list[str]] = None
    max_results: int = Field(default=1000, gt=0, le=10000)

@ingestion_router.post('')
def run_paper_ingestion_job(payload: IngestionJobPayload, x_cron_job_secret: Optional[str] = Header(default=None)):
    expected_cron_job_secret = os.getenv("SUPABASE_CRON_JOB_SECRET")
    if(expected_cron_job_secret is None):
        raise HTTPException(500, detail="Cron job secret is not specified")
    
    if(x_cron_job_secret != expected_cron_job_secret):
        raise HTTPException(401, detail="Invalid cron job secret")
    
    from app.services.ingestion_runner import run_paper_ingestion_cron
    
    return run_paper_ingestion_cron(
        target_date=payload.target_date,
        categories=payload.categories,
        max_results=payload.max_results
    )
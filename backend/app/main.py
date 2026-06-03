from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import recommendation_batch, paper_ingestion, users, saved_papers, paper_summaries

app = FastAPI(title="PaperArxiv Services")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000', 'https://130project-frontend.vercel.app',],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommendation_batch.rec_router)
app.include_router(recommendation_batch.rec_job_router)
app.include_router(paper_summaries.summary_router)
app.include_router(paper_ingestion.ingestion_router)
app.include_router(users.users_router)
app.include_router(saved_papers.saved_papers_router)

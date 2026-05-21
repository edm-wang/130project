from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import recommendation_batch

app = FastAPI(title="PaperArxiv Services")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommendation_batch.rec_router)

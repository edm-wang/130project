import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client


load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app = FastAPI(title="CS130 FastAPI Services")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_current_user(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing login token")

    token = authorization.replace("Bearer ", "")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    user_response = supabase.auth.get_user(token)

    if not user_response.user:
        raise HTTPException(status_code=401, detail="Invalid login token")

    return user_response.user


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/services/ping")
def service_ping():
    return {"message": "FastAPI service is running"}


@app.get("/auth/me")
def auth_me(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
    }

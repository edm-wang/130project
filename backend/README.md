# FastAPI Backend

This service is for custom Python backend logic. The Next.js app still owns the frontend and Supabase auth UI/database setup.

## Run locally

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open:

```text
http://localhost:8000/docs
```

## Authenticated requests from the frontend

Send the Supabase access token as a bearer token:

```http
Authorization: Bearer <supabase_access_token>
```


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

## app/routers
HTTP Endpoints are defined under /routers. To add a new group of api endpoints, please define your own routers there.  

## app/supabase
db.py defines a service-role Supabase client for trusted backend jobs
auth.py defines get_auth_context function that returns the current user, access token, and authenticated Supabase client for routers

## /tests
create new files to contain unit/integration tests

# Signing-in With Internal User

`POST` to `{{SUPABASE_URL}}/auth/v1/token?grant_type=password` with body:
```json
{
  "email": "email",
  "password": "password"
}
```
and header: 
```
apikey: {{SUPABASE_PUBLISHABLE_KEY}}
Content-Type: application/json
```
Supabase should reply with access token.

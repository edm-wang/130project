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
db.py uses singleton to get a global supabase client instance 
auth.py defines get_user function that returns an user instance that could be used by routers

## /tests
create new files to contain unit/integration tests



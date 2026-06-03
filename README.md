# PaperAgg

Personalized arXiv paper recommendation web app.

## Project structure

| Folder | What it is |
|---|---|
| `frontend-react/` | React + Vite SPA (the active frontend) |
| `backend/` | FastAPI Python backend |
| `supabase-nextjs/` | Supabase migration files (schema source of truth) |

## Quick start

You need **two servers running** at the same time.

### 1. Backend (FastAPI) — port 8000

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. Frontend (React) — port 3000

```bash
cd frontend-react
npm install
npm run dev
```

The local frontend must run on port 3000 (enforced by `vite.config.js`) because the backend's CORS allowlist includes `http://localhost:3000`. The deployed frontend origin `https://130project-frontend.vercel.app` is also allowed.

Open **http://localhost:3000** in your browser.

### Environment variables

The frontend reads from `frontend-react/.env.development`. The required keys are:

```
VITE_SUPABASE_URL=...
VITE_SUPABASE_PUBLISHABLE_KEY=...
VITE_BACKEND_URL=http://localhost:8000
VITE_USE_MOCK_DATA=false
```

Set `VITE_USE_MOCK_DATA=true` to run the frontend entirely on hardcoded mock data without needing the backend or a Supabase connection.

The backend reads from `backend/.env`. See `backend/README.md` for the required keys.

---

For more detail on each piece, see:
- [`frontend-react/README.md`](frontend-react/README.md) — frontend layout and structure
- [`backend/README.md`](backend/README.md) — backend routers, auth, and testing

---

## Database migrations

Use SQL migration files under `supabase-nextjs/supabase/migrations/` to update Supabase tables instead of editing tables directly in the Supabase dashboard.

Run Supabase commands from inside the `supabase-nextjs/` folder:

```bash
cd supabase-nextjs
npm install supabase --save-dev
npx supabase login
npx supabase link
```

After creating or editing SQL files under `supabase/migrations/`, preview and push:

```bash
npx supabase db push --dry-run
npx supabase db push
```

Commit migration files so teammates get the same schema:

```bash
git add supabase/migrations
git commit -m "Add database migration"
```

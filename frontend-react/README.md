# PaperAgg Frontend (React)

Vite + React JavaScript port of the four HTML mocks under `../frontend/`.

## Setup

```bash
cd frontend-react
npm install
cp .env.example .env.development     # if you haven't already
# Fill in VITE_SUPABASE_URL and VITE_SUPABASE_PUBLISHABLE_KEY in .env.development
npm run dev
```

The dev server pins to **port 3000** to match the FastAPI CORS allowlist
(`backend/app/main.py`).

## Routes

| Path | Page | Source HTML |
|---|---|---|
| `/feed` | Daily research feed | `../frontend/index.html` |
| `/reading-list` | Reading list + digest video | `../frontend/reading_list.html` |
| `/profile` | User profile + interests | `../frontend/profile_page.html` |
| `/papers/:id` | Paper detail (text + video summary) | `../frontend/post_recommendation.html` |
| `/auth/login` | Sign-in / sign-up | — |
| `/` | Redirects to `/feed` | — |

All app routes are wrapped in `RequireAuth`. Unauthenticated visits redirect
to `/auth/login?next=<path>` and come back after sign-in.

## Backend integration

`FeedPage` calls `GET ${VITE_BACKEND_URL}/recommendations` with
`Authorization: Bearer <token>` where the token resolution order is:

1. `?token=` URL param (handy for demos)
2. The current Supabase session's access token
3. `localStorage.pa_access_token` (legacy fallback from the original HTML mocks)

`useRecommendations` re-fetches whenever the access token changes, so signing
in / out updates the feed without a manual reload.

### Data sources today

- **FeedPage** — real `/recommendations` call when signed in. Backend is
  defined in `backend/app/routers/recommendation_batch.py`.
- **ReadingListPage / ProfilePage / PaperDetailPage** — still rendered from
  per-page `mockData.js` files because the backend doesn't expose endpoints
  for those features yet. Wire each in as Team 2 / Team 3 ships routes.

### Demoing without a backend

Set `VITE_USE_MOCK_DATA=true` in `.env.development` and the feed page renders
its mock fixtures immediately. Login is still required unless Supabase env
vars are blank, in which case the app runs in "Demo mode" with all routes
accessible.

## Layout

```
src/
├── hooks/                ← useAuth, plus any future cross-page hooks
├── styles/               ← tokens.css, reset.css
├── components/
│   ├── chrome/          ← Navbar, AppShell, PageTabs, RequireAuth
│   ├── atoms/           ← Avatar, InterestTag, Chip, Toggle, …
│   └── widgets/         ← right-column sidebar widgets reused across pages
├── pages/
│   ├── auth/            ← LoginPage (sign-in + sign-up)
│   ├── feed/            ← FeedPage + page-specific components, hook, mocks
│   ├── reading-list/
│   ├── profile/
│   └── paper-detail/
├── lib/                 ← api.js, format.js, supabase.js
└── shapes/shapes.js     ← JSDoc typedefs for Paper, Recommendation, …
```

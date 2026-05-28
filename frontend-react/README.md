# PaperAgg Frontend (React)

```bash
cd frontend-react
npm install
npm run dev
```

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

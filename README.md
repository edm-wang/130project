# Supabase Database Migration Workflow

Use SQL migration files to update Supabase tables instead of editing tables directly in the Supabase dashboard.

From this repository, run Supabase commands inside the app folder:

```bash
cd supabase-nextjs
```

Install the Supabase CLI locally:

```bash
npm install supabase --save-dev
```

Log in and link the local project to the remote Supabase project:

```bash
npx supabase login
npx supabase link
```

After creating or editing SQL files under `supabase/migrations`, preview and push the changes:

```bash
npx supabase db push --dry-run
npx supabase db push
```

Commit migration files so teammates get the same database schema:

```bash
git add supabase/migrations
git commit -m "Add database migration"
```

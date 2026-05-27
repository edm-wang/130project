-- [GenAI Usage] Prompt: Can you implement a minimal RLS policy in 20260527031413_add_rls.sql for the existing schemas as described 
-- in 20260517055912_create_initial_schema.sql so that only authenticated user or client using the service key can conduct operations on the tables?
-- [GenAI Usage] Begin LLM Response:
set search_path = public, extensions;

grant usage on schema public to authenticated, service_role;

do $$
declare
  table_name text;
  table_names text[] := array[
    'app_users',
    'research_interests',
    'research_interest_embeddings',
    'papers',
    'paper_embeddings',
    'saved_papers',
    'recommendation_feedback',
    'recommendation_batches',
    'recommendations'
  ];
begin
  foreach table_name in array table_names
  loop
    execute format('alter table public.%I enable row level security', table_name);

    execute format(
      'revoke all on table public.%I from anon',
      table_name
    );

    execute format(
      'grant select, insert, update, delete on table public.%I to authenticated, service_role',
      table_name
    );

    execute format(
      'drop policy if exists authenticated_full_access on public.%I',
      table_name
    );

    execute format(
      'create policy authenticated_full_access on public.%I for all to authenticated using (true) with check (true)',
      table_name
    );
  end loop;
end $$;
-- [GenAI Usage] End LLM Response
-- [GenAI Use] Reflection:
-- GenAI helped create a minimal dev RLS migration that blocks anon access,
-- allows authenticated users, and preserves service-role backend access.
-- These broad policies are for internal testing and should be tightened before production.
-- I have also thoroughly examined the code to ensure correctness.
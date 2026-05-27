--[GenAI Usage] Prompt: Can you create a minimal migration code to create a paper 
--ingestion run table with the proper rls policies in 20260527064858_add_paper_ingestion_run_table.sql .
--The table should include a source, the date for which the run is target at, the status of the run
--either running, completed, or failed, the categories provided to the run, the max number of paper
--set to be retrieved, and the results of the run (retrieved paper count and actually inserted paper
--count), and then add RLS policy to enable CRUD to this table for service role.
--[GenAI Usage] LLM response begin:
set search_path = public, extensions;

create table public.paper_ingestion_runs (
  id uuid primary key default gen_random_uuid(),

  source text not null default 'arxiv',
  target_date date not null,

  status text not null check (
    status in ('running', 'completed', 'failed')
  ),

  categories text[] not null,
  max_results integer not null check (max_results > 0),

  fetched_count integer check (
    fetched_count is null
    or fetched_count >= 0
  ),
  inserted_count integer check (
    inserted_count is null
    or inserted_count >= 0
  ),

  query_url text,
  error_message text,

  started_at timestamptz not null default now(),
  completed_at timestamptz,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  check (
    completed_at is null
    or completed_at >= started_at
  )
);

create trigger set_paper_ingestion_runs_updated_at
before update on public.paper_ingestion_runs
for each row execute function public.set_updated_at();

create unique index one_completed_arxiv_ingestion_per_date
on public.paper_ingestion_runs(source, target_date)
where status = 'completed';

create index idx_paper_ingestion_runs_status_started
on public.paper_ingestion_runs(status, started_at desc);

alter table public.paper_ingestion_runs enable row level security;

revoke all on table public.paper_ingestion_runs from anon;
revoke all on table public.paper_ingestion_runs from authenticated;

grant select, insert, update, delete
on table public.paper_ingestion_runs
to service_role;

drop policy if exists service_role_full_access
on public.paper_ingestion_runs;

create policy service_role_full_access
on public.paper_ingestion_runs
for all
to service_role
using (true)
with check (true);
--[GenAI Usage] LLM response end
--[GenAI Usage] Reflection: I provided detailed specification of the table to create and the policies to apply
--to the table. Codex provides efficient automation to the creation of this table and relevant policies. In 
--addition, I also thoroughly examined the code to ensure the implemented code follows my specification and 
--is correct.
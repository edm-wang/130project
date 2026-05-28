set search_path = public, extensions;

create table public.paper_summaries(
  id uuid primary key default gen_random_uuid(),
  paper_id uuid not null references public.papers(id) on delete cascade,
  summary_text text not null check (length(btrim(summary_text))>0),
  summary_status text not null default 'completed'
    check (summary_status in ('completed','failed')),

  llm_provider text not null,
  llm_model text not null,
  prompt_version text not null default 'paper_summary_v1',

  error_message text,

  created_by uuid references public.app_users(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (paper_id)
);

create trigger set_paper_summaries_update_at
before update on public.paper_summaries for each row execute function public.set_updated_at();

create index idx_paper_summaries_paper_id
on public.paper_summaries(paper_id);


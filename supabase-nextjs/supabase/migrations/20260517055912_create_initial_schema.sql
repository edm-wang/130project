-- [GenAI Use]: Please see genai_usage_appendix\initial_dataset_setup.md for the specific 
-- conversation that led to the creation of the below code.
-- [GenAI Use]: Selected LLM generated code start
set search_path = public, extensions;

create extension if not exists pgcrypto with schema extensions;
create extension if not exists vector with schema extensions;

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create table public.app_users (
  id uuid primary key references auth.users(id) on delete cascade,

  email text,
  display_name text,
  institution text,
  bio text,

  digest_enabled boolean not null default false,
  onboarding_completed boolean not null default false,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.research_interests (
  id uuid primary key default gen_random_uuid(),

  user_id uuid not null references public.app_users(id) on delete cascade,

  interest_type text not null check (
    interest_type in ('topic', 'field', 'author', 'keyword', 'category')
  ),

  value text not null check (length(btrim(value)) > 0),
  normalized_value text not null check (length(btrim(normalized_value)) > 0),

  preference_weight numeric(3,2) not null default 1.00 check (
    preference_weight >= 0
    and preference_weight <= 5
  ),

  is_active boolean not null default true,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  unique (user_id, interest_type, normalized_value)
);

create table public.research_interest_embeddings (
  research_interest_id uuid primary key
    references public.research_interests(id) on delete cascade,

  embedding_model text not null,
  embedding vector(1536) not null,

  embedded_text text not null,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.papers (
  id uuid primary key default gen_random_uuid(),

  source text not null check (
    source in ('arxiv', 'semantic_scholar', 'manual')
  ),
  source_id text not null check (length(btrim(source_id)) > 0),

  title text not null check (length(btrim(title)) > 0),
  abstract text,
  authors_text text,
  categories text[] not null default '{}'::text[],

  source_url text not null,
  pdf_url text,

  published_at timestamptz,
  source_updated_at timestamptz,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  unique (source, source_id)
);

create table public.paper_embeddings (
  paper_id uuid primary key references public.papers(id) on delete cascade,

  embedding_model text not null,
  embedding vector(1536) not null,

  embedded_text text not null,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.saved_papers (
  id uuid primary key default gen_random_uuid(),

  user_id uuid not null references public.app_users(id) on delete cascade,
  paper_id uuid not null references public.papers(id) on delete cascade,

  category text,
  category_source text not null default 'auto' check (
    category_source in ('auto', 'manual')
  ),
  category_confidence numeric(4,3) check (
    category_confidence is null
    or category_confidence between 0 and 1
  ),

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  unique (user_id, paper_id)
);

create table public.recommendation_feedback (
  id uuid primary key default gen_random_uuid(),

  user_id uuid not null references public.app_users(id) on delete cascade,
  paper_id uuid not null references public.papers(id) on delete cascade,

  feedback_value smallint not null check (feedback_value in (-1, 1)),

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  unique (user_id, paper_id)
);

create table public.recommendation_batches (
  id uuid primary key default gen_random_uuid(),

  user_id uuid not null references public.app_users(id) on delete cascade,

  status text not null default 'pending' check (
    status in ('pending', 'completed', 'failed')
  ),

  algorithm_version text not null default 'multi_vector_v1',

  parameters jsonb not null default '{}'::jsonb,
  candidate_count integer check (candidate_count is null or candidate_count >= 0),
  final_count integer check (final_count is null or final_count >= 0),

  error_message text,

  created_at timestamptz not null default now(),
  completed_at timestamptz
);

create table public.recommendations (
  id uuid primary key default gen_random_uuid(),

  batch_id uuid not null
    references public.recommendation_batches(id) on delete cascade,

  paper_id uuid not null
    references public.papers(id) on delete cascade,

  rank_position integer not null check (rank_position > 0),

  final_score numeric(10,5) not null default 0,

  interest_score numeric(10,5) not null default 0,
  saved_paper_score numeric(10,5) not null default 0,
  upvote_score numeric(10,5) not null default 0,
  downvote_penalty numeric(10,5) not null default 0,
  freshness_score numeric(10,5) not null default 0,

  explanation_summary text,

  created_at timestamptz not null default now(),

  unique (batch_id, paper_id),
  unique (batch_id, rank_position)
);

create trigger set_app_users_updated_at
before update on public.app_users
for each row execute function public.set_updated_at();

create trigger set_research_interests_updated_at
before update on public.research_interests
for each row execute function public.set_updated_at();

create trigger set_research_interest_embeddings_updated_at
before update on public.research_interest_embeddings
for each row execute function public.set_updated_at();

create trigger set_papers_updated_at
before update on public.papers
for each row execute function public.set_updated_at();

create trigger set_paper_embeddings_updated_at
before update on public.paper_embeddings
for each row execute function public.set_updated_at();

create trigger set_saved_papers_updated_at
before update on public.saved_papers
for each row execute function public.set_updated_at();

create trigger set_recommendation_feedback_updated_at
before update on public.recommendation_feedback
for each row execute function public.set_updated_at();

create index idx_research_interests_user_active
on public.research_interests(user_id, is_active);

create index idx_papers_source
on public.papers(source, source_id);

create index idx_papers_published_at
on public.papers(published_at desc);

create index idx_saved_papers_user
on public.saved_papers(user_id);

create index idx_saved_papers_paper
on public.saved_papers(paper_id);

create index idx_feedback_user
on public.recommendation_feedback(user_id);

create index idx_feedback_user_value
on public.recommendation_feedback(user_id, feedback_value);

create index idx_batches_user_created
on public.recommendation_batches(user_id, created_at desc);

create index idx_recommendations_batch_rank
on public.recommendations(batch_id, rank_position);

create index idx_recommendations_paper
on public.recommendations(paper_id);

create index idx_paper_embeddings_vector
on public.paper_embeddings
using hnsw (embedding vector_cosine_ops);

create index idx_interest_embeddings_vector
on public.research_interest_embeddings
using hnsw (embedding vector_cosine_ops);

--[GenAI Use]: Selected LLM generated code end
--[GenAI Use] Reflection: I thoroughly explored various approaches of implementing our database 
-- (e.g. using native PostgresSQL, or library on top of PostgresSQL, or Supabase) and theier potential drawbacks.
-- then, I clearly specified the various components in our system (e.g. User, Paper, RecommendationBatch) and the
-- required information within each component. Codex offers efficient automation of the repetitive declaration
-- of schema and attributes within each schema. 
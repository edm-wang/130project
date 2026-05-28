set search_path = public, extensions;

create or replace function public.match_paper_embeddings(
  query_embedding vector(1536),
  match_count int default 50
)
returns table (
  paper_id uuid,
  similarity double precision
)
language sql
stable
as $$
  select
    pe.paper_id,
    1 - (pe.embedding <=> query_embedding) as similarity
  from public.paper_embeddings pe
  order by pe.embedding <=> query_embedding
  limit least(greatest(coalesce(match_count, 50), 1), 200);
$$;

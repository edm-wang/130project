delete from public.papers p
where not exists (
  select 1
  from public.paper_embeddings pe
  where pe.paper_id = p.id
);

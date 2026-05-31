-- Remove papers that were inserted without a corresponding embedding row.
-- Dependent rows are removed by the existing foreign keys with ON DELETE CASCADE.
delete from public.papers p
where not exists (
  select 1
  from public.paper_embeddings pe
  where pe.paper_id = p.id
);

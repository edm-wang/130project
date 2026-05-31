set search_path = public, extensions;
set statement_timeout = 0;

-- Delete arXiv papers that were inserted without embeddings.
-- The ingest code writes arXiv rows to public.papers first, then writes
-- public.paper_embeddings rows separately. If the embedding upsert fails, the
-- paper remains orphaned and should not be used by recommendation retrieval.
do $$
declare
  deleted_count integer;
begin
  loop
    with invalid_papers as (
      select p.id
      from public.papers p
      where p.source = 'arxiv'
        and not exists (
          select 1
          from public.paper_embeddings pe
          where pe.paper_id = p.id
        )
      order by p.created_at, p.id
      limit 1000
    )
    delete from public.papers p
    using invalid_papers ip
    where p.id = ip.id;

    get diagnostics deleted_count = row_count;
    exit when deleted_count = 0;
  end loop;
end $$;

analyze public.papers;

reset statement_timeout;

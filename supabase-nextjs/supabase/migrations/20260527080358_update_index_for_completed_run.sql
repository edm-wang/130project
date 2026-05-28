--[GenAI Usage] Prompt: Can you also formulate an update code in 20260527080358_update_index_for_completed_run.sql to minimally update the 
--create unique index one_completed_arxiv_ingestion_per_date 
--on public.paper_ingestion_runs(source, target_date)
--where status = 'completed';
--in 20260527064858_add_paper_ingestion_run_table.sql so that it matches how we find existing run here?
--[GenAI Usage] LLM response begin
set search_path = public, extensions;

drop index if exists public.one_completed_arxiv_ingestion_per_date;

create unique index one_completed_arxiv_ingestion_per_run_parameters
on public.paper_ingestion_runs(source, target_date, categories, max_results)
where status = 'completed';
--[GenAI Usage] LLM response end
--[GenAI Usage] Reflection: I used Codex to perform an update to one of our index after realizing the potential bug in it when 
--implementing a backend service. I thoroughly examined the code and ensured it is correct and achieved the desired effect.
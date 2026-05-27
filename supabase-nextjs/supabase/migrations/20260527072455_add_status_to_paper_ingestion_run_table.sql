--[GenAI Usage] Prompt: If I want to add a skipper literal to the paper ingestion runs, 
-- can I just modify the existing migration file 20260527064858_add_paper_ingestion_run_table.sql and push it again?
--[GenAI Usage] LLM response begin
set search_path = public, extensions;

alter table public.paper_ingestion_runs
drop constraint if exists paper_ingestion_runs_status_check;

alter table public.paper_ingestion_runs
add constraint paper_ingestion_runs_status_check
check (
  status in ('running', 'completed', 'failed', 'skipped')
);
--[GenAI Usage] LLM response end
--[GenAI Usage] Reflection: I used Codex to add a new status to one of our existing table. I thoroughly 
--examined the code to ensure it is correct and achieves the desired purpose.
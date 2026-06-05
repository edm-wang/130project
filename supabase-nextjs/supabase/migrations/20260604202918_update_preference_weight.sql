begin;

-- Drop the existing auto-generated CHECK constraint if it has the usual name.
alter table public.research_interests
drop constraint if exists research_interests_preference_weight_check;

-- Widen the column so it can store values like 1000.00.
alter table public.research_interests
alter column preference_weight type numeric(10,2)
using preference_weight::numeric(10,2);

-- Keep the default compatible.
alter table public.research_interests
alter column preference_weight set default 1.00;

-- Add a wider validation range for testing.
alter table public.research_interests
add constraint research_interests_preference_weight_check
check (
  preference_weight >= 0
  and preference_weight <= 1000
);

commit;
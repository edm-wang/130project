# Conversation: Add recommendation API

<span style="color:red">**Note**: The content displayed below User [X] is the user prompt; the content displayed below Assistant [X] is the response by Codex to the user prompt User [X].<span style="color:red">

### User 16

<environment_context>
  <cwd>c:\Users\Danie\Desktop\CS_130_Project</cwd>
  <shell>powershell</shell>
  <current_date>2026-05-27</current_date>
  <timezone>America/Los_Angeles</timezone>
</environment_context>

I want to now implement the `generate_recommendations_for_user` in [recommendation_runner.py](backend/app/services/recommendation_runner.py) . Specifically, can you implement the function such that it first creates recommendation batch with pending stats and other appropriate parameters; then, it computes a vector embedding for each user (assume that we will be doing this everytime we generate a rec batch because currenlty I don't own user interest endpoint so I don't want to introduce aditional complexity of persisting the user interest embedding), and then either retrieve all paper embeddings or partly (I have a dilemma here - we don't want to retrieve the entire paper embedding for eveyr paper because that can be humongous, instead, we can run the first step in our algorithm, by retrieving top N similar papers for each interest, and then providing the N * M paper embeddings along with the user interest embedding, downvoted paper embedding, upvoted paper embedding (along with their source id of course), and the saved paper embedding via the paper object. Then, please implement the RecGenParams in [recommendation.py](backend/app/models/recommendation.py) to act as a parameter passing from the runner to the core logic so that it includes all parameters required for our recommendation algorithm with appropriate default - but don't generate the actual algorithm. Our high level algorithm can be described as below - feel free to reference it to extract appropriate parameters: ```Algorithm
Let user u have active interests:

I_u = {(q_m, w_m)} for m = 1 ... M
where q_m is the embedding of interest m, and w_m is its preference weight.

Let each paper p have embedding v_p, publication time t_p, and metadata. Use a normalized similarity function:

σ(a, b) ∈ [0, 1]
For example, this can be cosine similarity transformed into [0, 1].

1. Candidate Retrieval
For each interest vector q_m, query the vector database:

R_m = top_N papers by σ(q_m, v_p)
Then keep only the top N' from each interest:

C_m = top_N' papers from R_m
Merge them into one global candidate set:

C = C_1 ∪ C_2 ∪ ... ∪ C_M
If a paper appears for multiple interests, keep one copy of the paper, but preserve all its interest similarities. This is useful because a paper matching multiple interests should potentially receive extra credit.

2. Generic Decay Function
Use a generic decay function:

D(a; θ) ∈ [0, 1]
where a is an age value and θ represents parameters. The only required properties are:

D(0; θ) = 1
D(a; θ) decreases or stays flat as a increases
You can swap in different curves later:

half-life:      D(a; θ) = 2^(-a / h)
reciprocal:     D(a; θ) = 1 / (1 + a / τ)
plateau-decay:  D(a; θ) = 1 if a <= g, otherwise decay(a - g)
floor decay:    D(a; θ) = δ_min + (1 - δ_min) * decay(a)
So the algorithm does not depend on one fixed decay curve.

3. Interest Score
For candidate paper p, compute its similarity to each user interest:

x_m(p) = σ(q_m, v_p)
Normalize interest weights so they stay comparable:

ŵ_m = w_m / max_j(w_j)
A good interest score combines “best matching interest” with a small “multi-interest coverage” bonus:

interest_max(p) = max_m [ŵ_m * x_m(p)]
interest_avg(p) = Σ_m w_m * x_m(p) / Σ_m w_m
Then:

interest_score(p) =
  (1 - η) * interest_max(p)
  + η * interest_avg(p)
where η ∈ [0, 1].

For MVP, I would keep η small, maybe around 0.1 or 0.2. This means a paper mainly wins by strongly matching one important interest, but it gets a small bonus if it is relevant to multiple interests.

4. Saved Paper Boost
Let the user’s saved papers be:

S_u = {s_1, s_2, ..., s_A}
Each saved paper has embedding v_sj and save time t_sj.

For each saved paper, compute:

saved_similarity_j(p) = σ(v_p, v_sj)
Compute the age of the user interaction:

age_sj = now - t_sj
Then apply behavior recency decay:

ρ_sj = D(age_sj; θ_saved)
The evidence from saved paper s_j is:

e_sj(p) = ρ_sj * saved_similarity_j(p)
Now take the top k_s saved-paper evidence values:

TopSaved_k(p) = top k_s values of e_sj(p)
Then:

saved_paper_score(p) =
  mean(TopSaved_k(p))
If the user has no saved papers, this score is 0.

This gives more influence to saved papers that are both similar to the candidate and recently saved.

5. Upvote Boost
Let the user’s upvoted papers be:

U_u = {u_1, u_2, ..., u_B}
For each upvoted paper:

e_uj(p) =
  D(now - t_uj; θ_upvote) * σ(v_p, v_uj)
Then:

upvote_score(p) =
  mean(top k_u values of e_uj(p))
Usually, upvotes should be stronger than saves, because an upvote is an explicit positive preference. So later, its final weight should usually be larger than the saved-paper weight.

6. Downvote Penalty
Let the user’s downvoted papers be:

D_u = {d_1, d_2, ..., d_C}
For each downvoted paper:

e_dj(p) =
  D(now - t_dj; θ_downvote) * σ(v_p, v_dj)
Then:

raw_downvote_penalty(p) =
  mean(top k_d values of e_dj(p))
Cap the penalty:

downvote_penalty(p) =
  min(raw_downvote_penalty(p), penalty_cap)
This is important. A downvote should not permanently destroy an entire research area. It should mostly suppress papers very similar to things the user disliked.

You can make this even safer by applying a threshold:

σ'(v_p, v_dj) = 0 if σ(v_p, v_dj) < τ_d
so only sufficiently similar downvoted papers contribute to the penalty.

7. Freshness Score
Let candidate paper age be:

age_p = now - published_at(p)
Then:

freshness_score(p) = D(age_p; θ_freshness)
This should usually be an additive boost, not a multiplier. That way, a highly relevant older paper can still beat a weak recent paper.

8. Final Score
Now combine the components:

final_score(p) =
  λ_i * interest_score(p)
  + λ_s * saved_paper_score(p)
  + λ_u * upvote_score(p)
  - λ_d * downvote_penalty(p)
  + λ_f * freshness_score(p)
where:

λ_i = interest weight
λ_s = saved-paper weight
λ_u = upvote weight
λ_d = downvote weight
λ_f = freshness weight
A reasonable starting relationship is:

λ_i > λ_u >= λ_s
λ_d roughly similar to λ_u, but capped
λ_f smaller than λ_i
Then sort candidates by:

final_score(p) descending
and return the top K.

Optional Final Diversity Stage
After scoring, you may apply diversity filtering with MMR:

MMR(p) =
  γ * final_score(p)
  - (1 - γ) * max_{p' already selected} σ(v_p, v_p')
Pick papers one by one using this score. With γ = 0.75 or 0.8, relevance remains dominant, but near-duplicate papers are less likely to fill the whole recommendation feed.```

### Assistant 16

I’ll build this as scaffolding rather than the scoring algorithm itself: the runner will own batch lifecycle and data collection, while `RecGenParams` will package everything the future scorer needs. I’m going to inspect the current schema/runner files once more so the queries line up with your tables.

### Assistant 16

I found a `RecGenParams` stub already in `backend/app/services/recommendation.py`, which is the right home for core-logic DTOs. I’ll fill that service DTO and keep `backend/app/models/recommendation.py` focused on SQLModel table adapters unless we truly need a DB model change.

I’m about to add the runner scaffold. One practical wrinkle: this repo does not currently have a Supabase RPC for pgvector nearest-neighbor lookup, so I’ll make the runner try `match_paper_embeddings` first and fall back to a bounded recent embedding pool scored in Python. That keeps the endpoint usable now without fetching the whole table.

### Assistant 16

The scaffold is in: pending batch, interest embedding, candidate retrieval, saved/upvote/downvote signal hydration, and batch completion/failure. I’m running syntax checks and reading the diff now; if there are edge-case issues I’ll tighten them before handing it back.

### Assistant 16

The syntax checks passed. One intentional boundary choice: I kept the SQLModel table file untouched and used the existing `services/recommendation.py` stub for `RecGenParams`, since that object is algorithm input rather than a persisted table model.

### Assistant 16

One more small hardening pass: I’m going to let candidate hydration tolerate either direct RPC rows or joined rows, so a future `match_paper_embeddings` RPC does not have to return exactly the same shape as the fallback query.

### Assistant 16

Implemented the recommendation-generation scaffold.

Main changes:
- [recommendation_runner.py](C:/Users/Danie/Desktop/CS_130_Project/backend/app/services/recommendation_runner.py:19) now creates a `pending` batch, embeds active user interests, retrieves candidate paper embeddings, loads saved/upvoted/downvoted paper signals, calls the core recommendation function, inserts returned recommendation rows, and marks the batch `completed` or `failed`.
- [recommendation.py](C:/Users/Danie/Desktop/CS_130_Project/backend/app/services/recommendation.py:53) now defines `RecGenParams` plus DTOs for interests, candidate papers, user paper signals, and decay configs.
- [generate_recommendations](C:/Users/Danie/Desktop/CS_130_Project/backend/app/services/recommendation.py:140) is intentionally still a placeholder returning `[]`, per your request not to implement the actual scoring algorithm yet.

For candidate retrieval, the runner first tries a Supabase RPC named `match_paper_embeddings`. Since that RPC/migration does not exist yet in the repo, it falls back to a bounded recent pool from `paper_embeddings` using `fallback_candidate_pool_limit=500`, then computes cosine similarity in Python and keeps top candidates. That avoids pulling the entire embedding table while keeping local/dev behavior possible.

One design note: I implemented `RecGenParams` in `backend/app/services/recommendation.py` because there was already a stub there and it belongs to the core recommendation logic layer, not the SQLModel table adapter file.

Verified with:

```powershell
python -m py_compile backend\app\services\recommendation.py backend\app\services\recommendation_runner.py backend\app\routers\recommendation_batch.py
```

I did not run live OpenAI/Supabase calls.

### User 17

Can you explain what is about the RPC and the fallback match paper embeddings? Why would you expect that we have a Supabase RPC? I thought we 
were able to directy use a vectory and query a vector column in Supabase based on similarity (or atleast form a postgres perspective).

In addition, for the interaciton_created-at and interaction_updated_at, is it better to isntead just store a last_interaction_date to eliminate
ambiguity - again, miniality is key here, I don't expect we will be interating/scaling/expanding this project after it is completed. So you dont
need to put excessive emphasis on scalability/flexibility - currently it is minimality and readability that fulfills our basic functionality.

### Assistant 17

That’s a fair push. The RPC is not because Postgres cannot do vector similarity; it’s because the current backend talks to Supabase through the PostgREST client, which cannot conveniently express `embedding <=> query_vector` ordering inline. I’ll simplify the interaction timestamp shape now, and I’ll also make the vector retrieval assumption clearer in the code rather than hiding it behind too much hydration logic.

### Assistant 17

I agree with the timestamp point. I’m simplifying `UserPaperSignal` to a single `last_interaction_at` and trimming some extra RPC hydration flexibility so the runner is easier to read.

### Assistant 17

You’re right on the database side: Postgres/pgvector can directly do vector similarity, e.g. order by `embedding <=> query_embedding`.

The reason I used an RPC is specifically because this backend currently uses the Supabase Python/PostgREST client:

```python
client.table("paper_embeddings").select(...)
```

That client is good for normal filters/orders, but it does not cleanly express:

```sql
order by embedding <=> query_embedding
```

So the usual Supabase pattern is to expose that SQL as a Postgres function, then call it with:

```python
client.rpc("match_paper_embeddings", ...)
```

So: Postgres can do it directly; the Supabase REST client needs an RPC wrapper unless we switch to a direct Postgres connection.

The fallback matcher exists only because we do not have that RPC migration yet. It grabs a bounded recent pool from `paper_embeddings`, computes cosine similarity in Python, and keeps the top results. It is not the ideal final vector retrieval path, just a dev/MVP fallback so the runner can work before the SQL function exists.

I also simplified the interaction timestamp like you suggested. [UserPaperSignal](C:/Users/Danie/Desktop/CS_130_Project/backend/app/services/recommendation.py:42) now has only:

```python
last_interaction_at
```

and [recommendation_runner.py](C:/Users/Danie/Desktop/CS_130_Project/backend/app/services/recommendation_runner.py:333) sets it as:

```python
row.get("updated_at") or row.get("created_at")
```

I also removed the extra candidate-row hydration flexibility around RPC results to keep the code easier to read. The RPC, when added, should return rows shaped like the fallback rows: `paper_id`, `embedding`, `embedding_model`, `embedded_text`, `similarity`, and ideally joined `paper` metadata.

Verified syntax with:

```powershell
python -m py_compile backend\app\services\recommendation.py backend\app\services\recommendation_runner.py backend\app\routers\recommendation_batch.py
```

### User 18

Does it mean implementing the rpc simply requires us to setup an rpc on the supabase side and invoke the <=> in postgres in our rpc? If so, can you suggest how we can implement this so we can get rid of the fallback code.

### Assistant 18

Yes. The clean implementation is:

1. Add a Supabase SQL migration that defines `public.match_paper_embeddings`.
2. Inside that function, use pgvector cosine distance with `<=>`.
3. Call that function with `client.rpc(...)` from Python.
4. Delete the Python fallback code.

Supabase’s own vector docs recommend this exact pattern because PostgREST/Supabase client libraries do not directly support pgvector similarity operators in normal `.table(...).order(...)` calls, so vector search is wrapped in a Postgres function and invoked with `rpc()`.

A minimal migration could be:

```sql
set search_path = public, extensions;

create or replace function public.match_paper_embeddings(
  query_embedding vector(1536),
  match_count int default 50
)
returns table (
  paper_id uuid,
  embedding_model text,
  embedding vector(1536),
  embedded_text text,
  similarity double precision,
  paper jsonb
)
language sql
stable
as $$
  select
    pe.paper_id,
    pe.embedding_model,
    pe.embedding,
    pe.embedded_text,
    greatest(
      0,
      least(1, 1 - ((pe.embedding <=> query_embedding) / 2))
    ) as similarity,
    to_jsonb(p) as paper
  from public.paper_embeddings pe
  join public.papers p on p.id = pe.paper_id
  order by pe.embedding <=> query_embedding
  limit least(greatest(coalesce(match_count, 50), 1), 200);
$$;

grant execute on function public.match_paper_embeddings(vector, integer)
to authenticated, service_role;
```

Then the runner becomes simpler:

```python
def _match_paper_embeddings(client, interest, params):
    response = (
        client.rpc(
            "match_paper_embeddings",
            {
                "query_embedding": interest.embedding,
                "match_count": params.retrieval_top_n,
            },
        )
        .execute()
    )
    return response.data or []
```

After that, you can remove:

```python
_fallback_match_paper_embeddings
_cosine_similarity_01
sqrt import
fallback_candidate_pool_limit
```

The similarity formula above matches our Python normalization:

```text
python:   (cosine_similarity + 1) / 2
postgres: 1 - cosine_distance / 2
```

because cosine distance is:

```text
1 - cosine_similarity
```

One small note: the RPC should return the same shape the runner expects: `paper_id`, `embedding`, `embedding_model`, `embedded_text`, `similarity`, and `paper`.

Sources: Supabase documents pgvector’s `<=>` cosine distance operator and says PostgREST does not support pgvector similarity operators directly, so wrapping the query in a Postgres function and calling it through `rpc()` is the recommended approach: [Supabase vector columns](https://supabase.com/docs/guides/ai/vector-columns), [Supabase semantic search](https://supabase.com/docs/guides/ai/semantic-search).

### User 19

Is it possible to further simplify the RPC to only return the paper id for paper relevant information and the backend can fetch the paper itself? In addition, please xplain whether <=> is the cosine distaince (1 - sim) or the cosine similarity and what does the greatest keyword do.

### Assistant 19

Yes, you can simplify the RPC to return only the vector-search essentials:

```sql
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
```

Then the backend can take the returned `paper_id`s and fetch:

```text
papers
paper_embeddings
```

itself. This is more readable and keeps the RPC focused on one job: nearest-neighbor lookup.

`<=>` is cosine distance, not cosine similarity.

So:

```text
pe.embedding <=> query_embedding = cosine_distance
```

For normalized intuition:

```text
cosine_distance = 1 - cosine_similarity
```

That means:

```text
smaller distance = more similar
```

So we sort ascending:

```sql
order by pe.embedding <=> query_embedding
```

To turn distance into similarity:

```sql
1 - (pe.embedding <=> query_embedding) as similarity
```

So:

```text
distance 0.0 -> similarity 1.0
distance 0.2 -> similarity 0.8
distance 1.0 -> similarity 0.0
```

The `greatest` keyword returns the largest value among its arguments.

Example:

```sql
greatest(5, 1)
-- returns 5

greatest(-3, 1)
-- returns 1
```

In this expression:

```sql
limit least(greatest(coalesce(match_count, 50), 1), 200)
```

it means:

```text
if match_count is null, use 50
make sure it is at least 1
make sure it is at most 200
```

So:

```text
match_count = null -> 50
match_count = -10  -> 1
match_count = 500  -> 200
match_count = 30   -> 30
```

That just prevents accidental bad limits. For maximum minimality, you could write:

```sql
limit match_count;
```

But the bounded version is safer without adding much complexity.

### User 20

I have now implemented the RPC that returns a list of paper id and similarity given the query embedding and match count. Can you remove all code related to the fallback embedding fetch function and make the code in the recommendation runner minimal.

### Assistant 20

I’ll trim the runner to assume the RPC exists now: call `match_paper_embeddings`, fetch the returned paper IDs plus embeddings/metadata in one backend pass, and remove the Python similarity fallback helpers.

### Assistant 20

I’m going to keep only one retrieval path: RPC returns `{paper_id, similarity}`, then the runner hydrates those IDs with `paper_embeddings` and `papers`. The shared paper/embedding fetch helpers stay because saved/upvoted/downvoted signals need them too.

### Assistant 20

The fallback path and Python cosine scorer are removed. I’ll run checks and search for any leftover fallback references before I call it done.

### Assistant 20

The cleanup is mostly done. I noticed one tiny edge case while checking: if the RPC returns no matches, we should avoid calling `.in_(..., [])`, so I’ll add a small guard in the shared fetch helpers.

### Assistant 20

Done. I removed the fallback vector-search path from [recommendation_runner.py](C:/Users/Danie/Desktop/CS_130_Project/backend/app/services/recommendation_runner.py:201).

What changed:
- `_match_paper_embeddings` now only calls the Supabase RPC `match_paper_embeddings`.
- Removed `_fallback_match_paper_embeddings`.
- Removed Python cosine similarity logic and the `sqrt` import.
- Removed `fallback_candidate_pool_limit` from [RecGenParams](C:/Users/Danie/Desktop/CS_130_Project/backend/app/services/recommendation.py:50).
- Kept the shared `_fetch_embeddings_by_paper_id` / `_fetch_papers_by_id` helpers because the RPC only returns paper IDs and similarity, so the backend still needs to hydrate candidate papers and user saved/upvoted/downvoted papers.

Verified with:

```powershell
python -m py_compile backend\app\services\recommendation.py backend\app\services\recommendation_runner.py backend\app\routers\recommendation_batch.py
```

No live Supabase/OpenAI calls were run.

### User 21
Can you create a user snapshot has generaor either in recommendation_batch.py  or recommendation_runner.py to generate a deterministic hash of the user (e.g. using user's id, deterministic formating of the interest, saved papers, upvoted papers, downvoted papers. And then in recommendation_runner.py , create and persist the user snapshot hash when we create a pending recommendation batch. No need to modify the endpoint handling in recommendation_batch.py  now - I will be implementing the logic later.

### Assistant 21
Implemented the snapshot hash generation in recommendation_runner.py (line 169).
What changed:
Added generate_user_snapshot_hash(...), which deterministically hashes:user_id
active interests as interest_type, normalized value, preference weight
saved paper IDs
upvoted paper IDs
downvoted paper IDs

Uses sorted JSON + SHA-256, so row ordering does not affect the hash.
generate_recommendations_for_user now fetches the raw user snapshot first, computes the hash, and persists it when creating the pending batch.
_create_pending_batch now inserts user_snapshot_hash.
I did not modify endpoint handling logic.
Verification:
py_compile passes.
Added a small determinism smoke check showing reordered interests/saved/feedback rows produce the same hash.
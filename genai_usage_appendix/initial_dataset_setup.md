# Conversation: Choose local Python database

<span style="color:red">**Note**: The content displayed below User [X] is the user prompt; the content displayed below Assistant [X] is the response by Codex to the user prompt User [X].<span style="color:red">

### User 1

<environment_context>
  <cwd>c:\Users\Danie\Desktop\CS_130_Project</cwd>
  <shell>powershell</shell>
  <current_date>2026-05-16</current_date>
  <timezone>America/Los_Angeles</timezone>
</environment_context>

I want to build a web-application as described in [README.md](README.md) . For the database, can you suggest what would be the most suitable database we should use, and is it possible to just do it locally (host the database locally) - we just want the database that is minimal sufficient for our project (not overly complex) and is compatible for python.

### Assistant 1

I’ll read the project README first so the database recommendation fits the actual app rather than guessing from the title.

### Assistant 1

Yes, you can absolutely host the database locally.

For your project, the best choice depends on how “minimal” you want to be:

**Recommended for MVP/demo: SQLite**

Use **SQLite** if your priority is simplicity. It is built into Python, runs as a single local `.db` file, needs no separate server, and is enough for:

- Users and profiles
- Research interests
- Saved papers
- Votes
- Recommendation history
- Stored AI summaries
- arXiv paper metadata

It works very well with FastAPI using `SQLAlchemy` or `SQLModel`.

Example local database URL:

```env
DATABASE_URL=sqlite:///./research_app.db
```

This is probably the minimal sufficient option for a capstone demo.

**Recommended if you want closer-to-real deployment: PostgreSQL**

Your README currently lists **PostgreSQL**, and it is a strong fit because your data is relational and you’ll have many linked tables. It is more production-ready and better for multiple users, duplicate paper checks, search features, and future scaling.

You can still run PostgreSQL locally using Docker:

```bash
docker run --name research-db \
  -e POSTGRES_USER=research_user \
  -e POSTGRES_PASSWORD=research_pass \
  -e POSTGRES_DB=research_app \
  -p 5432:5432 \
  -d postgres:16
```

Database URL:

```env
DATABASE_URL=postgresql+psycopg://research_user:research_pass@localhost:5432/research_app
```

**My suggestion**

Use **SQLite for the first working version**, especially if you want the simplest setup. Build the backend with `SQLAlchemy` or `SQLModel` so you can switch to PostgreSQL later by changing the `DATABASE_URL`.

Avoid MongoDB or anything NoSQL here. Your app has clear relationships between users, interests, papers, recommendations, votes, saved papers, and summaries, so a relational database is the right fit.

A good stack would be:

```txt
FastAPI
SQLModel or SQLAlchemy
SQLite locally for MVP
Alembic for migrations, optional but useful
PostgreSQL later if needed
```

### User 2

For postgresSQL and SQLite, is there anythin that postgres can achieve but SQLite cannot for our web app?

### Assistant 2

Yes. For your specific app, **SQLite can handle the MVP**, but PostgreSQL can do several things better or more safely once the app has multiple users or more advanced search/recommendation needs.

**What PostgreSQL can do better than SQLite:**

| Area | PostgreSQL Advantage | Does it matter for your app? |
|---|---|---|
| Multiple users writing at once | Handles many simultaneous reads/writes well | Useful if several demo users or teammates use the app at once |
| Real server database | Runs as a database server that multiple backend instances can connect to | Important if deployed or shared by the team |
| Stronger data validation | Better column types, constraints, enums, relational rules | Helpful for users, papers, votes, saved papers |
| Full-text search | Strong built-in search over titles, abstracts, authors, keywords | Useful for paper search/recommendations |
| Advanced indexing | Better indexes for larger datasets | Useful if you store many arXiv papers |
| User permissions | Database-level users, roles, access control | Mostly not needed for MVP |
| Extensions | Can add `pgvector`, trigram search, etc. | Useful if you later do embedding-based recommendations |
| Production readiness | More common for deployed FastAPI apps | Useful if final demo is hosted online |

**What SQLite can still do fine:**

SQLite can store all of your core tables:

- users
- profiles
- interests
- papers
- saved papers
- votes
- recommendations
- summaries

It can also support a simple recommendation algorithm, local development, and a capstone demo. It is not “toy” software. It is just more limited when many users write to it at the same time or when the app grows.

**Biggest practical limitation of SQLite**

SQLite is a file-based database. It allows many reads, but write concurrency is limited. For example, if multiple users are saving papers, voting, editing profiles, and generating summaries at the same time, PostgreSQL handles that much better.

**Recommendation for your project**

For the simplest path:

```txt
Use SQLite for local MVP development.
Use SQLAlchemy or SQLModel so you can switch to PostgreSQL later.
```

For the most realistic capstone setup:

```txt
Use PostgreSQL locally with Docker from the start.
```

My honest recommendation: if your team is comfortable installing Docker, use **PostgreSQL** because your README already assumes it and it better matches a real web app. If setup simplicity matters more, use **SQLite first** and migrate later.

### User 3

Will the code complexity differ significantly for postgreSQL and SQLite?

### Assistant 3

Not significantly, **if you use an ORM like SQLAlchemy or SQLModel**.

Most of your app code would look the same for both SQLite and PostgreSQL:

```python
session.add(user)
session.commit()
session.query(Paper).filter(...)
```

The main difference is usually the database connection URL.

SQLite:

```env
DATABASE_URL=sqlite:///./research_app.db
```

PostgreSQL:

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/research_app
```

Where complexity can differ:

| Area | SQLite | PostgreSQL |
|---|---|---|
| Setup | Very simple, just a local `.db` file | Requires installing PostgreSQL or Docker |
| App code | Almost the same with ORM | Almost the same with ORM |
| Migrations | Similar with Alembic | Similar with Alembic |
| Data types | Fewer advanced types | More advanced types |
| Full-text search | Possible, but different | Better built-in support |
| Deployment | Less common for web apps | Standard for web apps |
| Concurrency | Simpler but more limited | Better, no extra app complexity |

For your MVP, code complexity is basically the same if you avoid database-specific features.

A clean setup would be:

```txt
FastAPI
SQLAlchemy or SQLModel
Alembic migrations
DATABASE_URL in .env
```

Then your backend can switch between SQLite and PostgreSQL mostly by changing configuration.

The bigger difference is **operational complexity**, not code complexity:

- SQLite: easier to start
- PostgreSQL: more setup, better long-term fit

For a 6-person capstone team, I’d lean **PostgreSQL if everyone can use Docker**, because it avoids migration surprises later. Otherwise, SQLite is totally fine for the first demo.

### User 4

Is we were to use PostgreSQL. Is it recommended to use it direclty, or to use some plaforms such as supabase?

### Assistant 4

Short answer: for your capstone MVP, I’d use **PostgreSQL directly**, probably through Docker, unless your team specifically wants **Supabase Auth** or a hosted shared database.

Supabase is not a different database. It gives you a real **Postgres database** plus extra platform features like Auth, auto-generated APIs, Storage, Realtime, dashboard tools, and hosted deployment. Supabase’s own docs describe each project as coming with a full Postgres database, and their platform also includes Auth and auto-generated APIs. Sources: [Supabase Database docs](https://supabase.com/docs/guides/database), [Supabase docs overview](https://supabase.com/docs/), [Supabase Data APIs](https://supabase.com/docs/guides/api/data-apis).

For your app:

| Option | Best When | Tradeoff |
|---|---|---|
| **Direct local PostgreSQL** | You want a minimal backend-controlled FastAPI app | You manage DB setup yourself |
| **Supabase** | You want hosted Postgres, built-in Auth, dashboard, maybe easier deployment | More platform concepts: Supabase keys, RLS policies, project config |
| **Local Supabase** | You want Supabase features but still develop locally | Requires Docker and runs a larger local stack |

My recommendation:

```txt
Use direct PostgreSQL + FastAPI + SQLAlchemy/SQLModel for the MVP.
```

That keeps your architecture simple:

```txt
React frontend
  -> FastAPI backend
    -> PostgreSQL database
```

Supabase becomes more attractive if you want this architecture:

```txt
React frontend
  -> Supabase Auth
  -> FastAPI backend
  -> Supabase-hosted PostgreSQL
```

or even:

```txt
React frontend
  -> Supabase client
  -> Supabase database/Auth APIs
```

But since your README already says **FastAPI backend**, I would avoid making the frontend talk directly to Supabase for core app data. Let FastAPI own the business logic: recommendations, arXiv ingestion, saved papers, votes, summaries.

One nice middle path: you can start with **local PostgreSQL directly**, and later move the same schema to **Supabase-hosted Postgres** if you want easier deployment. Supabase also supports local development with Docker, but that is more setup than just running one Postgres container. Source: [Supabase local development docs](https://supabase.com/docs/guides/local-development).

So the practical answer:

```txt
For class/demo simplicity: direct local PostgreSQL.
For easiest hosted database + built-in auth: Supabase.
For your specific project: direct PostgreSQL first, Supabase later only if deployment/auth convenience becomes valuable.
```

### User 5

THe reason why we considered Supabase is because it provides Auth and auth is a key feature of our platofmr so we can reduce complexity in setting up the Auth system ourselves. But for other parts of the feature, e.g. doing CRUD to the database, does using supabase introduce sigificantly more complexity than posgreSQL alone?

### Assistant 5

No, Supabase does **not** add significant CRUD complexity if you use it in the right way.

For your project, the cleanest setup is:

```txt
React frontend
  -> Supabase Auth for login/logout/session
  -> FastAPI backend for app logic
  -> Supabase-hosted PostgreSQL database
```

In this setup, Supabase is mostly giving you:

- OAuth / third-party login
- User sessions
- JWT access tokens
- Hosted PostgreSQL
- A dashboard for viewing/editing tables

Your CRUD code in FastAPI can still look like normal PostgreSQL code using `SQLAlchemy` or `SQLModel`. Supabase’s database is still Postgres.

The extra complexity comes only if you make the frontend directly CRUD the database through Supabase APIs. Then you need to think carefully about:

- Row Level Security policies
- Supabase client permissions
- Which tables the frontend can access
- Preventing users from reading/updating other users’ data

That can be powerful, but for your app I would keep CRUD in FastAPI because recommendation logic, arXiv ingestion, voting, and LLM summaries all belong on the backend anyway.

Recommended architecture:

```txt
Frontend:
- Uses Supabase JS for sign in/sign out
- Gets the current user's access token
- Sends token to FastAPI in Authorization header

FastAPI:
- Verifies the Supabase JWT
- Gets the user's Supabase user ID
- Runs normal CRUD using SQLAlchemy/SQLModel

Database:
- Supabase PostgreSQL
- profiles.user_id references Supabase auth user UUID
```

So compared to plain local PostgreSQL:

| Area | Plain PostgreSQL | Supabase |
|---|---|---|
| Database CRUD from FastAPI | Normal ORM code | Same normal ORM code |
| Auth | You build/integrate yourself | Supabase handles most of it |
| Hosted DB | You set it up | Built in |
| Dashboard | Need pgAdmin/DBeaver/etc. | Built in |
| Security model | Mostly backend-controlled | Backend-controlled, plus optional RLS |
| Setup complexity | Lower locally | Slightly more platform setup |
| Auth complexity | Higher | Much lower |

My recommendation for your capstone:

```txt
Use Supabase for Auth and hosted PostgreSQL.
Use FastAPI + SQLAlchemy/SQLModel for all application CRUD.
Do not use Supabase frontend database CRUD unless you really need it.
```

That gives you the biggest benefit of Supabase without letting the platform take over your whole architecture.

### User 6

How hard is to integrate with third party authentication, eg. sign in using google, directly using postgreSQL?

### Assistant 6

Directly with PostgreSQL, it is **moderately hard**, because PostgreSQL itself does **not** provide Google login. PostgreSQL would only store the result of authentication.

You would need your FastAPI backend to handle Google OAuth/OpenID Connect. Google’s sign-in system uses OAuth 2.0 / OpenID Connect, and Google’s docs describe it as usable for authentication and authorization: [Google Identity docs](https://developers.google.com/identity/authentication), [Google OpenID Connect docs](https://developers.google.com/identity/openid-connect/openid-connect?hl=en-US).

A direct setup would look like this:

```txt
React
  -> FastAPI auth route
    -> Google login
      -> FastAPI callback
        -> store/find user in PostgreSQL
        -> create app session or JWT
```

You would need to implement:

- Google OAuth app setup
- Redirect/callback route in FastAPI
- Token validation
- User lookup/create in PostgreSQL
- Session or JWT creation
- Logout behavior
- Protected route middleware
- Tables like `users` and `auth_provider_identities`

PostgreSQL tables might look like:

```txt
users
- id
- email
- display_name
- created_at

auth_provider_identities
- id
- user_id
- provider        # "google"
- provider_user_id # Google's stable user id / sub
- created_at
```

You would probably use a library like **Authlib**, which supports OAuth/OpenID Connect clients for Starlette/FastAPI-style apps: [Authlib Starlette client docs](https://docs.authlib.org/en/v1.6.9/client/starlette.html).

So the difficulty is roughly:

```txt
Supabase Auth: easier
FastAPI + Authlib + PostgreSQL: doable, moderate complexity
Manual OAuth without a library: not recommended
```

For a capstone, I’d personally lean **Supabase Auth** if login is a key feature. It saves you from spending too much time on auth plumbing and security edge cases. You can still keep all your app CRUD in FastAPI with normal PostgreSQL access.

Best architecture for you:

```txt
React uses Supabase Auth for Google sign-in
React sends Supabase JWT to FastAPI
FastAPI verifies the user
FastAPI performs CRUD in Supabase PostgreSQL
```

That gives you the benefit of Supabase where it matters most, while keeping recommendation logic, arXiv ingestion, voting, summaries, and profile CRUD in your own backend.

### User 7

Below contains the schemas we want to implement in our database for the project: "
User
The User entity represents a registered individual using the application. Since authentication is delegated to a third-party provider, this entity does not store credential-specific data such as passwords. Instead, it stores the application-level identity and profile information needed to personalize recommendations, deliver digest emails, and support profile-based features. The User entity serves as the anchor for most user-facing functionality, including onboarding, profile management, paper recommendation, and similar-user discovery.

Research Interest
The ResearchInterest entity captures the topics, fields, authors, and keywords that a user wants the system to prioritize when generating recommendations. This entity is separated from User because each user may define multiple interests, and these interests may vary in type and strength. ResearchInterest is the main personalization entity in the system and is directly used by the recommendation pipeline to filter, rank, and explain candidate papers. It also provides an important signal for identifying users with similar research preferences.

Paper
The Paper entity represents an academic paper ingested from an external source such as arXiv or Semantic Scholar. It is the main content object in the application and is referenced by nearly all recommendation-related features. The entity stores bibliographic and descriptive metadata needed for feed generation, recommendation explanation, redirection to the original source, and downstream LLM-based processing such as summarization or categorization. The design intentionally keeps the paper model lightweight by storing author information as text rather than fully normalizing authors into separate entities at the initial stage.

RecommendationBatch
The RecommendationBatch entity represents one execution of the recommendation pipeline for a specific user. It groups together all papers selected for that user in a single feed-generation run, such as a daily scheduled recommendation refresh. This entity allows the system to persist a consistent snapshot of the generated feed so that the same results can be reused by both the frontend and the email delivery service, rather than recomputing recommendations on every request. It also provides lightweight tracking metadata for whether the batch generation succeeded.

Recommendation
The Recommendation entity represents a single paper recommended to a specific user as part of a recommendation batch. Each record stores the paper selected for the user, its ranking score and position in the generated feed, and a brief explanation of why it was recommended. This entity is necessary because a paper may exist in the system without being recommended to every user, so personalized feed items must be modeled separately from raw paper metadata.

RecommendationReason
The RecommendationReason entity represents why a particular recommendation was made. During recommendation generation, the service compares each candidate paper against the user’s research interests. It stores an explanation based on matched topics, authors, keywords, categories, or similarity scores.

RecommendationFeedback
The RecommendationFeedback entity represents the feedback for a particular recommendation. When ranking future batches, the service also reads the user’s past feedback. Upvoted papers slightly increase the weight of similar topics/authors, while downvoted papers reduce them. " Can you provide a detailed schema definition for each entity such that it is minimal in complexity but is sufficient to support our features?

### User 8

Assume that we will be using supabase. Below contains the schemas we want to implement in our database for the project: " 
User
The User entity represents a registered individual using the application. Since authentication is delegated to a third-party provider, this entity does not store credential-specific data such as passwords. Instead, it stores the application-level identity and profile information needed to personalize recommendations, deliver digest emails, and support profile-based features. The User entity serves as the anchor for most user-facing functionality, including onboarding, profile management, paper recommendation, and similar-user discovery.

Research Interest
The ResearchInterest entity captures the topics, fields, authors, and keywords that a user wants the system to prioritize when generating recommendations. This entity is separated from User because each user may define multiple interests, and these interests may vary in type and strength. ResearchInterest is the main personalization entity in the system and is directly used by the recommendation pipeline to filter, rank, and explain candidate papers. It also provides an important signal for identifying users with similar research preferences.

Paper
The Paper entity represents an academic paper ingested from an external source such as arXiv or Semantic Scholar. It is the main content object in the application and is referenced by nearly all recommendation-related features. The entity stores bibliographic and descriptive metadata needed for feed generation, recommendation explanation, redirection to the original source, and downstream LLM-based processing such as summarization or categorization. The design intentionally keeps the paper model lightweight by storing author information as text rather than fully normalizing authors into separate entities at the initial stage.

RecommendationBatch
The RecommendationBatch entity represents one execution of the recommendation pipeline for a specific user. It groups together all papers selected for that user in a single feed-generation run, such as a daily scheduled recommendation refresh. This entity allows the system to persist a consistent snapshot of the generated feed so that the same results can be reused by both the frontend and the email delivery service, rather than recomputing recommendations on every request. It also provides lightweight tracking metadata for whether the batch generation succeeded.

Recommendation
The Recommendation entity represents a single paper recommended to a specific user as part of a recommendation batch. Each record stores the paper selected for the user, its ranking score and position in the generated feed, and a brief explanation of why it was recommended. This entity is necessary because a paper may exist in the system without being recommended to every user, so personalized feed items must be modeled separately from raw paper metadata.

RecommendationReason
The RecommendationReason entity represents why a particular recommendation was made. During recommendation generation, the service compares each candidate paper against the user’s research interests. It stores an explanation based on matched topics, authors, keywords, categories, or similarity scores.

RecommendationFeedback
The RecommendationFeedback entity represents the feedback for a particular recommendation. When ranking future batches, the service also reads the user’s past feedback. Upvoted papers slightly increase the weight of similar topics/authors, while downvoted papers reduce them. " Can you provide a detailed schema definition for each entity such that it is minimal in complexity but is sufficient to support our features?

### Assistant 8

Yes. Since you’re using Supabase, I’d design the database around **Supabase Auth’s built-in `auth.users` table**, then create your own app-level user table in `public`.

Important: avoid naming your table `User`. In Postgres, use snake_case plural names like `app_users`.

## Recommended Tables

```txt
auth.users                -- managed by Supabase Auth
public.app_users          -- your app-level user/profile data
public.research_interests
public.papers
public.recommendation_batches
public.recommendations
public.recommendation_reasons
public.recommendation_feedback
```

## 1. `app_users`

Represents an authenticated user in your app. The `id` should match the Supabase Auth user ID.

```sql
create table public.app_users (
  id uuid primary key references auth.users(id) on delete cascade,

  email text,
  display_name text,
  avatar_url text,
  institution text,
  bio text,

  digest_enabled boolean not null default false,
  onboarding_completed boolean not null default false,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

Notes:

- `id` comes from Supabase Auth.
- Do **not** store passwords.
- `email` is technically available in Supabase Auth, but storing a copy here is convenient for app queries and digest emails.

## 2. `research_interests`

Stores topics, fields, authors, and keywords for each user.

```sql
create table public.research_interests (
  id uuid primary key default gen_random_uuid(),

  user_id uuid not null references public.app_users(id) on delete cascade,

  interest_type text not null check (
    interest_type in ('topic', 'field', 'author', 'keyword', 'category')
  ),

  value text not null,
  normalized_value text not null,

  weight numeric(3,2) not null default 1.00 check (weight >= 0 and weight <= 5),

  is_active boolean not null default true,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  unique (user_id, interest_type, normalized_value)
);
```

Example records:

```txt
topic     | machine learning
author    | Yoshua Bengio
keyword   | transformer
category  | cs.CL
```

Use `normalized_value` for matching, usually lowercase and trimmed.

## 3. `papers`

Stores arXiv or Semantic Scholar paper metadata.

```sql
create table public.papers (
  id uuid primary key default gen_random_uuid(),

  source text not null check (source in ('arxiv', 'semantic_scholar')),
  source_id text not null,

  title text not null,
  abstract text,
  authors_text text,
  categories text[],

  source_url text not null,
  pdf_url text,

  published_at timestamptz,
  updated_at timestamptz,

  created_at timestamptz not null default now(),

  unique (source, source_id)
);
```

Notes:

- `authors_text` is intentionally simple.
- `categories text[]` works nicely for arXiv categories like `cs.AI`, `cs.CL`, `stat.ML`.
- `unique (source, source_id)` prevents duplicate paper ingestion.

## 4. `recommendation_batches`

Represents one recommendation run for one user.

```sql
create table public.recommendation_batches (
  id uuid primary key default gen_random_uuid(),

  user_id uuid not null references public.app_users(id) on delete cascade,

  status text not null default 'pending' check (
    status in ('pending', 'completed', 'failed')
  ),

  algorithm_version text,
  candidate_count integer,
  error_message text,

  created_at timestamptz not null default now(),
  completed_at timestamptz
);
```

This lets you persist a stable feed instead of recomputing recommendations every page load.

## 5. `recommendations`

Represents one recommended paper inside a batch.

```sql
create table public.recommendations (
  id uuid primary key default gen_random_uuid(),

  batch_id uuid not null references public.recommendation_batches(id) on delete cascade,
  paper_id uuid not null references public.papers(id) on delete cascade,

  rank_position integer not null check (rank_position > 0),
  score numeric(8,4) not null default 0,

  explanation_summary text,

  created_at timestamptz not null default now(),

  unique (batch_id, paper_id),
  unique (batch_id, rank_position)
);
```

Example `explanation_summary`:

```txt
Matched your interests in "machine learning" and "transformers".
```

## 6. `recommendation_reasons`

Stores specific reasons behind a recommendation.

```sql
create table public.recommendation_reasons (
  id uuid primary key default gen_random_uuid(),

  recommendation_id uuid not null references public.recommendations(id) on delete cascade,
  research_interest_id uuid references public.research_interests(id) on delete set null,

  reason_type text not null check (
    reason_type in ('topic', 'field', 'author', 'keyword', 'category', 'similarity', 'feedback')
  ),

  matched_value text not null,
  score_contribution numeric(8,4),

  created_at timestamptz not null default now()
);
```

Example reasons:

```txt
keyword  | transformer
author   | Geoffrey Hinton
category | cs.CL
```

This gives you explainable recommendations without making the main `recommendations` table too crowded.

## 7. `recommendation_feedback`

Stores upvotes/downvotes from users.

```sql
create table public.recommendation_feedback (
  id uuid primary key default gen_random_uuid(),

  user_id uuid not null references public.app_users(id) on delete cascade,
  paper_id uuid not null references public.papers(id) on delete cascade,
  recommendation_id uuid references public.recommendations(id) on delete set null,

  feedback_value smallint not null check (feedback_value in (-1, 1)),

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  unique (user_id, paper_id)
);
```

Use:

```txt
1  = upvote
-1 = downvote
```

I recommend `unique (user_id, paper_id)` instead of `unique (user_id, recommendation_id)` because your app probably cares about whether the user likes the paper, even if the paper appears in multiple recommendation batches.

## Useful Indexes

Add these for performance:

```sql
create index idx_research_interests_user_id
on public.research_interests(user_id);

create index idx_papers_source
on public.papers(source, source_id);

create index idx_papers_published_at
on public.papers(published_at desc);

create index idx_recommendation_batches_user_created
on public.recommendation_batches(user_id, created_at desc);

create index idx_recommendations_batch_rank
on public.recommendations(batch_id, rank_position);

create index idx_recommendations_paper_id
on public.recommendations(paper_id);

create index idx_recommendation_reasons_recommendation_id
on public.recommendation_reasons(recommendation_id);

create index idx_recommendation_feedback_user_id
on public.recommendation_feedback(user_id);
```

## Missing But Probably Needed

Your listed entities do not include two important MVP features from the README:

```txt
saved_papers
paper_summaries
```

Minimal versions:

```sql
create table public.saved_papers (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.app_users(id) on delete cascade,
  paper_id uuid not null references public.papers(id) on delete cascade,
  created_at timestamptz not null default now(),
  unique (user_id, paper_id)
);
```

```sql
create table public.paper_summaries (
  id uuid primary key default gen_random_uuid(),
  paper_id uuid not null references public.papers(id) on delete cascade,
  summary_text text not null,
  model_name text,
  created_at timestamptz not null default now(),
  unique (paper_id)
);
```

## Final Recommendation

This schema is minimal but enough for:

- Supabase Auth login
- User profiles
- Research interests
- Paper ingestion
- Deduplication
- Recommendation batches
- Ranked recommendation feeds
- Explanation reasons
- Upvote/downvote feedback
- Saved papers
- AI summaries

The biggest design choice is: **use Supabase for Auth, but let FastAPI handle CRUD and recommendation logic**. That keeps the app understandable for a capstone team.

### User 9

Can you explain what does the score in each recommendation entity and research interest entity mean? Because it seems like we are currently allowing user to upvote/downvote a recommended paper, but not a specific research interest. In addition, please make the following changes to the entitites: i) we don't need user profile picture, 2) we want to implement auto-categorization for saved paper, so saved paper should ahve autocategorization.

### User 10

Can you explain what does the score in each recommendation entity and research interest entity mean? Because it seems like we are currently allowing user to upvote/downvote a recommended paper, but not a specific research interest. In addition, please make the following changes to the entitites: i) we don't need user profile picture, 2) we want to implement auto-categorization for saved paper, so saved paper should have category.

### Assistant 10

Good catch. There are really **two different ideas** here:

1. **`recommendations.score`** = how strongly the system recommends a specific paper to a user.
2. **`research_interests.weight`** = how important a user’s stated interest is when ranking papers.

They are related, but they are not the same.

## Recommendation Score

In `recommendations`, the `score` is generated by your recommendation algorithm.

Example:

```txt
Paper A matches 3 user interests -> score 8.50
Paper B matches 1 user interest  -> score 3.20
Paper C matches no strong signals -> score 0.75
```

You use this to sort the feed:

```txt
highest score = shown first
```

So this field belongs in `recommendations`.

```sql
score numeric(8,4) not null default 0
```

This is not something the user directly edits.

## Research Interest Weight

In `research_interests`, `weight` means:

```txt
How important this interest is to the user.
```

Example:

```txt
machine learning | weight 2.00
biology          | weight 1.00
robotics         | weight 0.50
```

Then a paper matching “machine learning” would get a stronger boost than one matching “robotics.”

But your point is right: if your UI only allows users to add/delete interests, and only allows upvote/downvote on papers, then interest weights may be unnecessary for the MVP.

My recommendation: **keep `weight`, but treat it as an internal field**.

For MVP:

```txt
Every interest starts with weight = 1.00
Users do not directly edit it
Upvotes/downvotes can influence future recommendation scoring indirectly
```

Example:

```txt
User upvotes a paper that matched "transformers"
-> future transformer-related papers may score slightly higher

User downvotes a paper that matched "cryptography"
-> future cryptography-related papers may score slightly lower
```

You do not need to store that feedback as a vote on the interest itself. The feedback stays attached to the paper/recommendation, and the recommendation algorithm can interpret it later.

## Updated Schema Changes

### 1. Remove Profile Picture

Updated `app_users`:

```sql
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
```

Removed:

```sql
avatar_url text
```

### 2. Add Category to Saved Papers

For auto-categorization, update `saved_papers`:

```sql
create table public.saved_papers (
  id uuid primary key default gen_random_uuid(),

  user_id uuid not null references public.app_users(id) on delete cascade,
  paper_id uuid not null references public.papers(id) on delete cascade,

  category text,
  category_source text not null default 'auto' check (
    category_source in ('auto', 'manual')
  ),

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  unique (user_id, paper_id)
);
```

Example categories:

```txt
Machine Learning
Natural Language Processing
Computer Vision
Robotics
Saved for Later
```

The `category_source` field lets you support this later:

```txt
auto   = system categorized it
manual = user changed the category
```

That is still minimal, but gives you room to let users override the category later.

## Small Naming Suggestion

To avoid confusion, you could rename `research_interests.weight` to:

```sql
preference_weight numeric(3,2) not null default 1.00
```

That makes it clearer that it is not a vote score. So the updated field would be:

```sql
preference_weight numeric(3,2) not null default 1.00
check (preference_weight >= 0 and preference_weight <= 5)
```

I’d keep:

- `recommendations.score`
- `recommendation_reasons.score_contribution`
- `research_interests.preference_weight`

That gives you a clean separation between ranking, explanation, and user preference strength.

### User 11

For the recommendation, we are actually thinking of doing something more complex - rather than matching the keyword/field/category of the paper to that os the user's. For instance, we are thinking of using vector datrabases to store embeddings of user, or user's paper history, and when we generate ranking, we compute the paper embedding and try to get top k recommendation. Can you suggest what are some approaches of recommendation that introduces more complexity, but not a lot? Ideally, we will want to incorporate the research interest, maybe also the upvote/downvote, and potentially user's view history (i.e. what paper they clicked on).

### Assistant 11

Yes, this is a very good direction. Since you’re using Supabase, you probably do **not** need a separate vector database. Supabase/Postgres can use the `pgvector` extension for storing embeddings and doing vector similarity search. Supabase documents `pgvector` for embeddings/vector similarity, and pgvector itself supports exact and approximate nearest-neighbor search with cosine/L2/inner-product distance plus HNSW/IVFFlat indexes. Sources: [Supabase pgvector docs](https://supabase.com/docs/guides/database/extensions/pgvector), [pgvector project](https://github.com/pgvector/pgvector).

I’d suggest this as your “more complex, but not too much” recommendation ladder.

**Best Fit Approach**
Use a **hybrid vector recommender**:

```txt
Explicit research interests
+ paper embeddings
+ saved/upvoted/downvoted papers
+ view/click history
= user profile vector

Then retrieve top-k papers by vector similarity
Then rerank using metadata and feedback signals
```

This gives you a real recommendation system without jumping into heavy ML training.

## Approach 1: Paper Embeddings + Interest Query

Start simple:

1. For each paper, generate an embedding from:

```txt
title + abstract + authors + categories
```

2. For each user, generate a query text from their interests:

```txt
User is interested in:
- machine learning
- transformers
- natural language processing
- Yoshua Bengio
```

3. Embed that query.
4. Search for papers whose embeddings are closest to the user embedding.

This is already much better than exact keyword matching because it can find semantically related papers.

Example:

```txt
User interest: "large language models"
Paper title: "Scaling Instruction-Tuned Transformers"
```

Even without exact keyword overlap, embeddings should place them near each other.

## Approach 2: Feedback-Weighted User Vector

This is probably the best capstone-level upgrade.

Instead of representing a user only by stated interests, represent them by a weighted combination of:

| Signal | Suggested Weight |
|---|---:|
| Research interest | `1.0` |
| Viewed/clicked paper | `0.2` |
| Saved paper | `0.8` |
| Upvoted paper | `1.2` |
| Downvoted paper | `-1.0` |

Conceptually:

```txt
user_vector =
  interest vectors
+ saved paper vectors
+ upvoted paper vectors
+ clicked paper vectors
- downvoted paper vectors
```

So if a user upvotes several NLP papers, their profile vector moves closer to NLP papers. If they downvote a robotics paper, future robotics-heavy papers become less likely.

This is a known simple pattern, often called a **Rocchio-style** relevance feedback approach. It is easy to explain in a final presentation and easy to implement.

## Approach 3: Multi-Vector Retrieval

Averaging all interests into one vector can blur the user’s preferences.

Example:

```txt
User likes:
- computer vision
- medical imaging
- reinforcement learning
```

One average vector may not represent all three cleanly.

Instead, query separately:

```txt
Top 20 papers for computer vision
Top 20 papers for medical imaging
Top 20 papers for reinforcement learning
Top 20 papers for user history vector
```

Then merge and rerank the results.

This helps with explanation too:

```txt
Recommended because it matched your interest in "medical imaging".
```

This fits nicely with your existing `recommendation_reasons` table.

## Approach 4: Hybrid Reranking

Use vector search to get candidate papers, then rerank them in Python.

Example scoring formula:

```txt
final_score =
  0.55 * semantic_similarity
+ 0.15 * explicit_interest_match
+ 0.10 * author/category_match
+ 0.10 * freshness_score
+ 0.10 * feedback_score
```

Then store `final_score` in:

```sql
recommendations.score
```

So `recommendations.score` becomes the final ranking score, not just the vector similarity score.

You can also store reason-level contributions:

```txt
semantic similarity: +0.55
matched category cs.CL: +0.10
upvoted similar paper: +0.20
recent publication: +0.05
```

Those can go into `recommendation_reasons`.

## Approach 5: Similar-User Recommendations

This is a good extra feature, but I would not start here.

Once every user has a profile vector, you can find similar users:

```txt
Find users whose profile vectors are close to this user's vector.
Recommend papers those users saved/upvoted.
```

This supports your “similar researchers” feature too.

However, it only works well after you have enough users and interaction data. For the MVP, content-based vector recommendation is more reliable.

## Recommended Implementation

For your project, I’d implement this:

```txt
Phase 1:
- Store paper embeddings
- Generate user vector from research interests
- Recommend top-k papers with pgvector

Phase 2:
- Add saved/upvoted/downvoted papers into user vector
- Add click/view history with low weight

Phase 3:
- Rerank candidates with metadata, recency, and feedback
- Store recommendation reasons

Phase 4:
- Optional similar-user recommendations
```

## Minimal Schema Additions

You can add embeddings without changing everything.

```sql
create extension if not exists vector;
```

Assuming your embedding model outputs `1536` dimensions, though this depends on the model you choose:

```sql
create table public.paper_embeddings (
  paper_id uuid primary key references public.papers(id) on delete cascade,

  embedding_model text not null,
  embedding vector(1536) not null,

  embedded_text text,
  created_at timestamptz not null default now()
);
```

For user vectors:

```sql
create table public.user_recommendation_profiles (
  user_id uuid primary key references public.app_users(id) on delete cascade,

  embedding_model text not null,
  profile_embedding vector(1536) not null,

  updated_at timestamptz not null default now()
);
```

For view/click history:

```sql
create table public.paper_interactions (
  id uuid primary key default gen_random_uuid(),

  user_id uuid not null references public.app_users(id) on delete cascade,
  paper_id uuid not null references public.papers(id) on delete cascade,
  recommendation_id uuid references public.recommendations(id) on delete set null,

  interaction_type text not null check (
    interaction_type in ('view', 'click', 'save', 'upvote', 'downvote')
  ),

  created_at timestamptz not null default now()
);
```

Even if you already have `saved_papers` and `recommendation_feedback`, this table is useful as an event log.

## My Recommendation

The best balance for your team is:

```txt
Hybrid content-based vector recommendation
+ feedback-weighted user profile vector
+ simple Python reranking
```

That is meaningfully more advanced than keyword matching, but still very buildable in a capstone timeline. It also gives you a strong demo story: the app learns from explicit interests, saved papers, upvotes/downvotes, and clicked papers.

### User 12

Can you suggest an approach that uses multi-vector retrieval with reranking based on user's research interest in profile, user's saved paper, user's upvote/downvote (no need for view history now as it could be too complex), and then explain in detail how it will work from a high level.

### Assistant 12

Yes. I’d use a **multi-vector retrieval + lightweight reranking** approach.

The key idea is: don’t compress the user into one embedding too early. Instead, retrieve candidate papers from several signals separately, then merge and rerank them.

This works well with Supabase because Supabase Postgres supports `pgvector`, so you can store paper embeddings inside the same database as the rest of your app. See: [Supabase pgvector docs](https://supabase.com/docs/guides/database/extensions/pgvector), [pgvector GitHub](https://github.com/pgvector/pgvector).

## High-Level Flow

```txt
1. Store embeddings for all papers
2. Build multiple recommendation queries for one user
3. Retrieve candidate papers from each query
4. Merge duplicate candidates
5. Rerank candidates using interests, saved papers, upvotes, and downvotes
6. Store final ranked results in recommendation_batches / recommendations
7. Store explanations in recommendation_reasons
```

## 1. Store Paper Embeddings

For every paper, create an embedding from text like:

```txt
Title: ...
Abstract: ...
Authors: ...
Categories: ...
```

Then store it in a `paper_embeddings` table.

Each paper now has a semantic representation, so papers about related ideas can match even when they do not share exact keywords.

Example:

```txt
User interest: "AI agents"
Paper text: "autonomous language model planning"
```

Keyword matching may miss this. Embedding search can still find it.

## 2. Use Multiple User Signals

For one user, collect these signals:

```txt
A. Research interests
B. Saved papers
C. Upvoted papers
D. Downvoted papers
```

Each signal plays a different role.

### Research Interests

These are the user’s explicit preferences.

Example:

```txt
machine learning
natural language processing
AI safety
```

For each research interest, generate or store an embedding.

Then retrieve papers similar to each interest separately:

```txt
Top 30 papers similar to "machine learning"
Top 30 papers similar to "natural language processing"
Top 30 papers similar to "AI safety"
```

This is better than averaging all interests together because it preserves separate interests.

### Saved Papers

Saved papers are stronger than generic clicks because they mean:

```txt
The user found this paper worth keeping.
```

For each saved paper, use that paper’s existing embedding to retrieve similar papers.

Example:

```txt
User saved a paper about transformer interpretability
-> retrieve similar papers about mechanistic interpretability, attention analysis, model behavior
```

You probably only need the most recent or most relevant saved papers, such as the latest 10-20.

### Upvoted Papers

Upvotes are strong positive feedback.

Use upvoted paper embeddings similarly to saved paper embeddings, but give them a higher weight during reranking.

```txt
Upvoted paper similarity = strong boost
Saved paper similarity = medium boost
Research interest similarity = baseline signal
```

### Downvoted Papers

Downvotes should usually **not** be used to retrieve recommendations.

Instead, use them as a penalty during reranking.

Example:

```txt
Candidate paper is very similar to a downvoted paper
-> subtract from final score
```

This avoids recommending papers that are semantically close to things the user disliked.

## 3. Candidate Retrieval

For each signal, retrieve top-k papers using vector similarity.

Conceptually:

```txt
interest candidates:
- top 30 per research interest

saved-paper candidates:
- top 20 per saved paper

upvote candidates:
- top 20 per upvoted paper
```

Then combine all results into one candidate pool.

Example:

```txt
Research interest retrieval found:
Paper A, Paper B, Paper C

Saved paper retrieval found:
Paper B, Paper D, Paper E

Upvote retrieval found:
Paper A, Paper F

Merged candidates:
Paper A, Paper B, Paper C, Paper D, Paper E, Paper F
```

Duplicates are useful. If a paper appears from multiple signals, that should improve its final score.

## 4. Reranking Formula

After retrieval, compute a final score in Python.

Example formula:

```txt
final_score =
  0.45 * interest_similarity_score
+ 0.25 * upvote_similarity_score
+ 0.20 * saved_similarity_score
- 0.30 * downvote_similarity_penalty
+ 0.10 * freshness_score
```

You can tune the numbers later.

A candidate paper gets a higher score if:

- It matches one or more research interests
- It is similar to saved papers
- It is similar to upvoted papers
- It is recent
- It is not similar to downvoted papers

A candidate paper gets penalized if:

- It is similar to downvoted papers
- It was already saved
- It was already recommended recently

## 5. Example

Suppose the user profile has:

```txt
Research interests:
- natural language processing
- model interpretability

Saved papers:
- "Attention is All You Need"

Upvoted papers:
- "Mechanistic Interpretability of Transformer Models"

Downvoted papers:
- "Robot Motion Planning with Reinforcement Learning"
```

The system retrieves candidates from:

```txt
Vector search for "natural language processing"
Vector search for "model interpretability"
Vector search near "Attention is All You Need"
Vector search near "Mechanistic Interpretability of Transformer Models"
```

Then during reranking:

```txt
Paper about transformer interpretability:
+ high interest match
+ high upvote similarity
+ high saved-paper similarity
= ranked high

Paper about robotics reinforcement learning:
+ maybe some AI similarity
- high downvote similarity
= ranked lower
```

## 6. Recommendation Reasons

Your `recommendation_reasons` table becomes very useful here.

For each final recommendation, store reasons like:

```txt
Matched research interest: natural language processing
Similar to saved paper: Attention is All You Need
Similar to upvoted paper: Mechanistic Interpretability of Transformer Models
Penalized because similar to downvoted paper: ...
```

You do not have to show negative reasons to the user, but storing them can help debugging.

For the UI, show friendly explanations:

```txt
Recommended because it matches your interest in NLP and is similar to a paper you saved.
```

## 7. Recommended MVP Version

For a capstone, I would implement this version:

```txt
Use pgvector for paper embeddings.
Generate embeddings for research interests.
Retrieve top-k papers per interest.
Retrieve top-k papers from saved and upvoted paper embeddings.
Penalize candidates similar to downvoted papers.
Rerank in Python.
Store final results in recommendation_batches and recommendations.
```

This is advanced enough to be impressive, but still manageable. You avoid training a machine learning model, and you keep all recommendation logic understandable and debuggable.

### User 13

Based on this recommendation algorithm, can you provide a full, thorough definition of each relevant entities such that we can integrate smoothly ino supabase database.

### Assistant 13

Yes. For your Supabase setup, I’d use this schema shape:

```txt
Supabase Auth:
auth.users

App tables:
app_users
research_interests
research_interest_embeddings
papers
paper_embeddings
saved_papers
recommendation_feedback
recommendation_batches
recommendations
recommendation_reasons
```

This supports:

- Supabase Auth
- user interests
- paper ingestion
- paper embeddings
- multi-vector retrieval
- saved-paper similarity
- upvote/downvote feedback
- reranking
- recommendation explanations
- auto-categorized saved papers

Below is a full practical schema.

## Extensions

```sql
create extension if not exists vector;
create extension if not exists pgcrypto;
```

Use `vector(N)` where `N` is your embedding model’s dimension. I’ll use `1536` as an example. If your model outputs a different size, replace all `vector(1536)` fields.

## 1. `app_users`

App-level user profile connected to Supabase Auth.

```sql
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
```

Purpose:

```txt
Stores non-password user data.
Supabase Auth owns login credentials and providers.
```

## 2. `research_interests`

Explicit user interests.

```sql
create table public.research_interests (
  id uuid primary key default gen_random_uuid(),

  user_id uuid not null references public.app_users(id) on delete cascade,

  interest_type text not null check (
    interest_type in ('topic', 'field', 'author', 'keyword', 'category')
  ),

  value text not null,
  normalized_value text not null,

  preference_weight numeric(3,2) not null default 1.00
    check (preference_weight >= 0 and preference_weight <= 5),

  is_active boolean not null default true,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  unique (user_id, interest_type, normalized_value)
);
```

Purpose:

```txt
Used as one retrieval source.
Each active interest can produce its own vector search.
```

Example:

```txt
topic    | natural language processing
keyword  | transformer interpretability
category | cs.CL
author   | Yoshua Bengio
```

## 3. `research_interest_embeddings`

Stores embeddings for user interests.

```sql
create table public.research_interest_embeddings (
  research_interest_id uuid primary key
    references public.research_interests(id) on delete cascade,

  embedding_model text not null,
  embedding vector(1536) not null,

  embedded_text text not null,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

Purpose:

```txt
Avoids regenerating embeddings every recommendation run.
Each research interest can independently retrieve similar papers.
```

`embedded_text` might be:

```txt
User research interest: natural language processing
```

or:

```txt
Research topic: transformer interpretability
```

## 4. `papers`

Stores paper metadata from arXiv or another source.

```sql
create table public.papers (
  id uuid primary key default gen_random_uuid(),

  source text not null check (
    source in ('arxiv', 'semantic_scholar', 'manual')
  ),

  source_id text not null,

  title text not null,
  abstract text,
  authors_text text,
  categories text[],

  source_url text not null,
  pdf_url text,

  published_at timestamptz,
  source_updated_at timestamptz,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  unique (source, source_id)
);
```

Purpose:

```txt
Raw paper metadata.
A paper can exist even if it has not been recommended yet.
```

For arXiv:

```txt
source = 'arxiv'
source_id = arXiv ID
categories = ['cs.CL', 'cs.AI']
```

## 5. `paper_embeddings`

Stores semantic embeddings for papers.

```sql
create table public.paper_embeddings (
  paper_id uuid primary key references public.papers(id) on delete cascade,

  embedding_model text not null,
  embedding vector(1536) not null,

  embedded_text text not null,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

Purpose:

```txt
Main vector-search table.
Recommendation retrieval searches against this table.
```

`embedded_text` should be consistent, for example:

```txt
Title: ...
Abstract: ...
Authors: ...
Categories: ...
```

## 6. `saved_papers`

Stores papers saved by users, including auto-categorization.

```sql
create table public.saved_papers (
  id uuid primary key default gen_random_uuid(),

  user_id uuid not null references public.app_users(id) on delete cascade,
  paper_id uuid not null references public.papers(id) on delete cascade,

  category text,
  category_source text not null default 'auto' check (
    category_source in ('auto', 'manual')
  ),

  category_confidence numeric(4,3)
    check (category_confidence is null or category_confidence between 0 and 1),

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  unique (user_id, paper_id)
);
```

Purpose:

```txt
Saved papers are a positive recommendation signal.
Their paper embeddings can retrieve similar papers.
```

Example categories:

```txt
Natural Language Processing
Computer Vision
AI Safety
To Read Later
```

## 7. `recommendation_feedback`

Stores upvotes and downvotes.

```sql
create table public.recommendation_feedback (
  id uuid primary key default gen_random_uuid(),

  user_id uuid not null references public.app_users(id) on delete cascade,
  paper_id uuid not null references public.papers(id) on delete cascade,

  feedback_value smallint not null check (feedback_value in (-1, 1)),

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  unique (user_id, paper_id)
);
```

Purpose:

```txt
Upvoted papers are strong positive signals.
Downvoted papers are negative reranking signals.
```

Use:

```txt
1  = upvote
-1 = downvote
```

I would attach feedback to `paper_id`, not only `recommendation_id`, because a user’s opinion about a paper should survive across recommendation batches.

## 8. `recommendation_batches`

One recommendation-generation run for one user.

```sql
create table public.recommendation_batches (
  id uuid primary key default gen_random_uuid(),

  user_id uuid not null references public.app_users(id) on delete cascade,

  status text not null default 'pending' check (
    status in ('pending', 'completed', 'failed')
  ),

  algorithm_version text not null default 'multi_vector_v1',

  parameters jsonb,
  candidate_count integer,
  final_count integer,

  error_message text,

  created_at timestamptz not null default now(),
  completed_at timestamptz
);
```

Purpose:

```txt
Stores one stable recommendation feed.
The frontend loads from the latest completed batch instead of recomputing every page refresh.
```

Example `parameters`:

```json
{
  "interest_top_k": 30,
  "saved_top_k": 20,
  "upvote_top_k": 20,
  "final_top_k": 20,
  "weights": {
    "interest": 0.45,
    "saved": 0.20,
    "upvote": 0.25,
    "downvote_penalty": 0.30,
    "freshness": 0.10
  }
}
```

## 9. `recommendations`

Final ranked papers in a batch.

```sql
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
```

Purpose:

```txt
Stores the actual ranked feed shown to the user.
```

`final_score` is the final result after reranking.

Example formula:

```txt
final_score =
  interest_score
+ saved_paper_score
+ upvote_score
- downvote_penalty
+ freshness_score
```

## 10. `recommendation_reasons`

Detailed explanation signals for each recommendation.

```sql
create table public.recommendation_reasons (
  id uuid primary key default gen_random_uuid(),

  recommendation_id uuid not null
    references public.recommendations(id) on delete cascade,

  reason_type text not null check (
    reason_type in (
      'research_interest',
      'saved_paper',
      'upvoted_paper',
      'downvoted_paper_penalty',
      'category_match',
      'freshness'
    )
  ),

  research_interest_id uuid
    references public.research_interests(id) on delete set null,

  source_paper_id uuid
    references public.papers(id) on delete set null,

  matched_value text,
  similarity_score numeric(10,5),
  score_contribution numeric(10,5),

  display_text text,

  created_at timestamptz not null default now()
);
```

Purpose:

```txt
Stores why each paper was recommended.
Supports explainable recommendations in the UI.
```

Example reasons:

```txt
reason_type: research_interest
matched_value: natural language processing
display_text: Matches your interest in natural language processing.

reason_type: saved_paper
source_paper_id: <saved paper id>
display_text: Similar to a paper you saved.

reason_type: upvoted_paper
source_paper_id: <upvoted paper id>
display_text: Similar to a paper you upvoted.
```

You probably should not show downvote reasons to the user, but storing them is helpful for debugging.

## Useful Indexes

```sql
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

create index idx_reasons_recommendation
on public.recommendation_reasons(recommendation_id);
```

For vector search:

```sql
create index idx_paper_embeddings_vector
on public.paper_embeddings
using hnsw (embedding vector_cosine_ops);

create index idx_interest_embeddings_vector
on public.research_interest_embeddings
using hnsw (embedding vector_cosine_ops);
```

## How Recommendation Generation Works

At a high level:

```txt
1. Get active research interests for the user.
2. Get the user’s saved papers.
3. Get the user’s upvoted papers.
4. Get the user’s downvoted papers.
5. Run vector retrieval separately for each positive signal.
6. Merge duplicate candidate papers.
7. Penalize candidates similar to downvoted papers.
8. Add freshness score.
9. Sort by final score.
10. Store results in recommendation_batches and recommendations.
11. Store explanations in recommendation_reasons.
```

The schema above supports each step directly.

## Minimal Query Logic

Research interest retrieval:

```txt
For each active research_interest_embedding:
find papers whose paper_embedding is closest to it.
```

Saved paper retrieval:

```txt
For each saved paper:
use its paper embedding to find similar papers.
```

Upvote retrieval:

```txt
For each upvoted paper:
use its paper embedding to find similar papers.
```

Downvote penalty:

```txt
For each candidate:
compare it against downvoted paper embeddings.
if similarity is high, subtract from score.
```

## Final Recommendation

This is the schema I’d use for your capstone:

```txt
Keep user/profile data simple.
Store embeddings separately from core entities.
Use multi-vector retrieval from interests, saved papers, and upvotes.
Use downvotes only during reranking.
Store score components in recommendations.
Store human-readable explanations in recommendation_reasons.
```

It is advanced enough to demonstrate a real recommendation system, but still simple enough that a 6-person team can implement it cleanly.

### User 14

Curretly I created a project in supabase. Can you suggest what is the most appropriate way of adding tables you just created

### Assistant 14

Use **SQL migrations**, not manual table-by-table creation.

For your project, the most appropriate workflow is:

```txt
Supabase CLI migration files
  -> committed to GitHub
  -> pushed to your Supabase project
```

This is better than clicking tables together in the Supabase UI because your schema has foreign keys, constraints, indexes, `pgvector`, and will likely change as the project evolves.

Supabase’s migration docs recommend this team workflow: create migration files locally, test them, commit them, and have one person push migrations to the remote project. They also warn that changing the remote database directly through the Dashboard can bypass migration history and cause sync issues later. Source: [Supabase Database Migrations](https://supabase.com/docs/guides/deployment/database-migrations).

## Recommended Workflow

1. Install and initialize Supabase CLI in your repo:

```bash
supabase init
```

2. Log in and link your remote Supabase project:

```bash
supabase login
supabase link
```

3. Create a migration file:

```bash
supabase migration new create_initial_schema
```

4. Put the SQL schema into the generated file:

```txt
supabase/migrations/<timestamp>_create_initial_schema.sql
```

5. Push it to your Supabase project:

```bash
supabase db push
```

6. Commit the migration file:

```bash
git add supabase/migrations
git commit -m "Add initial database schema"
```

## Why Not Table Editor?

The Table Editor is okay for quick experimenting, but I would avoid it for your real schema because you need:

- `pgvector` extension
- foreign keys to `auth.users`
- `check` constraints
- unique constraints
- vector indexes
- recommendation-related indexes
- future schema versioning

Those are much easier and safer to manage in SQL.

## SQL Editor Alternative

For a one-time class prototype, you *can* paste the schema into the Supabase **SQL Editor** and run it.

But for a 6-person team, I would only use SQL Editor for quick tests. Once multiple people are working, migrations are the cleaner path.

## Important Supabase Security Note

Because your tables are in the `public` schema, you should enable **Row Level Security** on app tables. Supabase says RLS should be enabled on exposed schemas like `public`; tables created through raw SQL or SQL Editor need RLS enabled manually. Source: [Supabase RLS docs](https://supabase.com/docs/guides/database/postgres/row-level-security).

For your architecture, I’d do this:

```txt
Frontend:
- uses Supabase Auth only

FastAPI:
- verifies Supabase JWT
- handles app CRUD and recommendation logic

Database:
- has RLS enabled
- no direct frontend CRUD unless you intentionally add policies
```

So your migration should include table creation, indexes, and RLS setup. The next practical step is to create one migration called something like:

```txt
create_initial_schema
```

and put all initial tables/extensions/indexes in that file. Later changes should each get their own migration, like:

```txt
add_paper_summaries
add_saved_paper_categories
add_recommendation_indexes
```

### User 15

Can you add the tables you created above into the file supabase\migrations\20260517055912_create_initial_schema.sql?

### Assistant 15

I’ll inspect the existing migration file first so I can add the schema without accidentally trampling anything already there.

### Assistant 15

It looks like that exact `supabase/migrations` path does not exist in the current workspace yet. I’m going to check the repo layout and look for any similarly named migration file before creating the missing path/file.

### Assistant 15

I found the migration under `supabase-nextjs/supabase/migrations/...`, not at the repo root. I’m going to populate that file with the Supabase/Postgres schema, including `pgvector`, constraints, indexes, update timestamp triggers, and basic RLS policies so it’s ready for Supabase rather than just plain Postgres.

### Assistant 15

The migration is now populated. I’m doing a quick verification pass on the generated SQL and checking whether the Supabase CLI is available locally for a stronger validation.

### Assistant 15

The local machine doesn’t currently have `supabase` or `psql` on PATH, so I can’t run the migration here. I’ll still do one last structural check from the file itself and then I’ll summarize exactly what was added and how to apply it from a machine with the Supabase CLI.

### Assistant 15

Done. I populated [20260517055912_create_initial_schema.sql](C:/Users/Danie/Desktop/CS_130_Project/supabase-nextjs/supabase/migrations/20260517055912_create_initial_schema.sql:1) with the Supabase schema.

Added:

- `pgcrypto` and `pgvector`
- `app_users`
- `research_interests`
- `research_interest_embeddings`
- `papers`
- `paper_embeddings`
- `saved_papers` with auto/manual category support
- `recommendation_feedback`
- `recommendation_batches`
- `recommendations`
- `recommendation_reasons`
- indexes, including HNSW vector indexes
- `updated_at` trigger helper
- basic RLS policies for user-owned data and recommendation reads

One note: the file was under `supabase-nextjs/supabase/migrations`, not root-level `supabase/migrations`.

I could not run the migration locally because neither `supabase` nor `psql` is currently available on PATH. To apply it from a machine with the Supabase CLI installed, run from `supabase-nextjs`:

```bash
supabase db push
```

This migration focuses on the recommendation/auth/profile schema we just designed; `paper_summaries` can be added as a small follow-up migration when Team 3 starts the LLM summary feature.

### User 16

Can you dothe below things:i) remove the recommendation reason table for now, we will ad later if needed, ii) explain what the triggers are, iii) explain what the indices are and why we need them

### Assistant 16

I’ll simplify the migration by removing `recommendation_reasons` and every dependent index/RLS policy. After that I’ll explain the remaining triggers and indexes in plain project terms.

### Assistant 16

The only objects tied to that table are the table itself, one index, one RLS enable line, and one read policy. I’m removing exactly those pieces and leaving the compact `explanation_summary` field on `recommendations` for now.

### Assistant 16

The migration has been simplified. I’ll quickly scan for any leftover `recommendation_reasons` references so it doesn’t fail later from a dangling policy or index.

### Assistant 16

Done. I removed `recommendation_reasons` from [20260517055912_create_initial_schema.sql](C:/Users/Danie/Desktop/CS_130_Project/supabase-nextjs/supabase/migrations/20260517055912_create_initial_schema.sql:1), including its table, index, RLS enable line, and policy. The recommendation table still has `explanation_summary`, so you can show a simple reason in the UI now and add the detailed reason table later.

**Triggers**

A trigger is database logic that automatically runs when something happens to a table.

In this migration, the trigger setup is:

```sql
create or replace function public.set_updated_at()
```

Then tables like `app_users`, `papers`, `saved_papers`, and `recommendation_feedback` have triggers like:

```sql
before update on public.saved_papers
for each row execute function public.set_updated_at();
```

That means whenever an existing row is updated, Postgres automatically sets:

```sql
updated_at = now()
```

Why this is useful:

- Backend/frontend code does not need to remember to update `updated_at`.
- You get reliable “last modified” timestamps.
- It helps debugging and future features like “recently updated interests” or “last feedback update.”

I only used triggers on tables that actually have an `updated_at` column.

**Indexes**

An index is like a lookup shortcut for the database. Without indexes, Postgres may need to scan many rows to answer common queries. With indexes, it can jump directly to the relevant rows.

The important indexes here are:

```sql
idx_research_interests_user_active
```

Used when loading a user’s active interests for recommendations.

```sql
idx_papers_source
```

Used to quickly find/deduplicate papers by source, like `arxiv` + arXiv ID.

```sql
idx_papers_published_at
```

Used when sorting/filtering papers by newest first.

```sql
idx_saved_papers_user
```

Used to quickly load a user’s saved papers.

```sql
idx_saved_papers_paper
```

Useful when checking which users saved a paper or joining saved papers to paper metadata.

```sql
idx_feedback_user
idx_feedback_user_value
```

Used to quickly find a user’s upvotes/downvotes during recommendation reranking.

```sql
idx_batches_user_created
```

Used to get a user’s latest recommendation batch.

```sql
idx_recommendations_batch_rank
```

Used to load a recommendation feed in ranked order.

```sql
idx_recommendations_paper
```

Useful when joining recommendations to papers or checking if a paper was recommended before.

The vector indexes are especially important:

```sql
idx_paper_embeddings_vector
idx_interest_embeddings_vector
```

These use HNSW indexes from `pgvector`, which makes similarity search much faster. They support queries like:

```txt
Find papers whose embeddings are closest to this research interest embedding.
Find papers similar to this saved/upvoted paper.
```

Without those vector indexes, the database may need to compare against every paper embedding, which gets slow as your paper collection grows.

### User 17

Can you explain the grammar of the index creation command and use an example to suggest what the index mens?

### Assistant 17

Sure. A basic Postgres index command has this shape:

```sql
create index index_name
on table_name(column_name);
```

Meaning:

```txt
Create a lookup shortcut named index_name
for table_name
using column_name.
```

Example from your migration:

```sql
create index idx_saved_papers_user
on public.saved_papers(user_id);
```

This means:

```txt
Create an index called idx_saved_papers_user
on the saved_papers table
using the user_id column.
```

So when your app runs a query like:

```sql
select *
from public.saved_papers
where user_id = 'some-user-id';
```

Postgres can use `idx_saved_papers_user` to quickly find only that user’s saved papers.

Without the index, Postgres may need to scan the whole `saved_papers` table row by row.

## Multi-Column Index

Some indexes use more than one column:

```sql
create index idx_batches_user_created
on public.recommendation_batches(user_id, created_at desc);
```

This means:

```txt
Create an index on recommendation_batches
first organized by user_id,
then by created_at from newest to oldest.
```

This helps queries like:

```sql
select *
from public.recommendation_batches
where user_id = 'some-user-id'
order by created_at desc
limit 1;
```

That is exactly how you would fetch a user’s latest recommendation batch.

## Vector Index

This one looks a little different:

```sql
create index idx_paper_embeddings_vector
on public.paper_embeddings
using hnsw (embedding vector_cosine_ops);
```

Breakdown:

```txt
create index idx_paper_embeddings_vector
```

Create an index with this name.

```txt
on public.paper_embeddings
```

Put the index on the `paper_embeddings` table.

```txt
using hnsw
```

Use the HNSW algorithm, which is designed for fast nearest-neighbor vector search.

```txt
(embedding vector_cosine_ops)
```

Index the `embedding` column using cosine similarity.

This helps queries like:

```sql
select paper_id
from public.paper_embeddings
order by embedding <=> '[0.12, 0.08, ...]'::vector
limit 20;
```

Meaning:

```txt
Find the 20 papers whose embeddings are most similar to this query embedding.
```

So, in plain English:

```sql
create index idx_paper_embeddings_vector
on public.paper_embeddings
using hnsw (embedding vector_cosine_ops);
```

means:

```txt
Make semantic paper search fast.
```

## Rule of Thumb

You usually create indexes on columns that are often used in:

```sql
where
join
order by
```

For your app:

```sql
user_id
```

because you often load data for one user.

```sql
paper_id
```

because you often join saved papers, feedback, and recommendations to papers.

```sql
created_at
```

because you often want latest data first.

```sql
embedding
```

because you want fast semantic similarity search.

### User 18

Also for the policies you created - would it be better to keep the policy part on the backend from a separation fo concerns perspective or for a minimal complexity perspective, as it is also more flexible to change policies on teh backend than in teh database.

### Assistant 18

Yes, your instinct is right: **for your project, most authorization logic should live in the backend**, not in a large set of Supabase RLS policies.

I’d think of it this way:

```txt
Backend policies = main application logic
Database RLS policies = safety guardrails
```

For your architecture:

```txt
React
  -> Supabase Auth
  -> FastAPI backend
  -> Supabase Postgres
```

I would recommend:

```txt
Use Supabase Auth for login.
Use FastAPI for CRUD authorization.
Keep database RLS minimal and conservative.
```

Why this is cleaner:

- Your recommendation logic already lives in FastAPI.
- Backend checks are easier to change, test, and debug.
- You avoid writing complicated SQL policies for every table relationship.
- It keeps app behavior in one place instead of split between Python and Postgres RLS.

However, I would **not remove RLS entirely** if your tables are in Supabase’s public schema. RLS is still useful as a protective layer in case someone accidentally uses the frontend Supabase client to query app tables directly.

A good minimal setup is:

```txt
Frontend:
- Supabase Auth only
- No direct table CRUD, or very limited table reads/writes

FastAPI:
- verifies Supabase JWT
- checks user owns the resource
- performs CRUD

Database:
- RLS enabled
- simple user-owned policies only if direct frontend access is needed
- otherwise rely on backend/service role for app operations
```

For example, this kind of policy is fine:

```sql
user_id = auth.uid()
```

But I would avoid complex policies like:

```txt
Users can read recommendation reasons if they belong to recommendations
inside batches that belong to the user...
```

That gets hard to maintain. Since we removed `recommendation_reasons`, this is less of an issue now.

For minimal complexity, I’d simplify the current policies to cover only tables the frontend may directly access. If your frontend only talks to FastAPI, you could keep just:

- `app_users`
- maybe `research_interests`
- maybe `saved_papers`
- maybe `recommendation_feedback`

And let FastAPI handle:

- paper ingestion
- embeddings
- recommendation batches
- recommendations
- vector search
- reranking

One important warning: if your FastAPI backend uses the Supabase **service role key**, that key can bypass RLS. That is normal, but it means your backend must enforce user ownership carefully. Never expose the service role key to the frontend.

My recommendation:

```txt
Keep RLS enabled.
Reduce RLS to simple guardrail policies.
Put real authorization/business rules in FastAPI.
Do not let the frontend directly write recommendation, embedding, or paper-ingestion tables.
```

That gives you the best balance: simple backend control, fewer fragile SQL policies, and still a database-level safety net.

### User 19

Can ou explain what is RLS - currenlty I think we have RLS disabled on supabase. Then please make the policies more concise - as you mentioned, only for those where the frontend can direclty access, and for authentication purpose.

### Assistant 19

I’ll tighten the migration so RLS is still enabled as a guardrail, but only the user-facing tables get frontend policies. Backend-owned tables like papers, embeddings, batches, and recommendations will have RLS enabled with no client policies, so FastAPI/service-role access can manage them.

### Assistant 19

I’m going to replace the longer policy set with four small user-owned policies: profile, interests, saved papers, and feedback. The recommendation and embedding tables will stay locked down to frontend clients by having RLS enabled but no frontend policies.

### Assistant 19

The policy section is now much shorter. I’ll scan it once to make sure only the intended policies remain.

### Assistant 19

Done. I made the policy section more concise in [20260517055912_create_initial_schema.sql](C:/Users/Danie/Desktop/CS_130_Project/supabase-nextjs/supabase/migrations/20260517055912_create_initial_schema.sql:255).

**What RLS Is**

RLS means **Row Level Security**. It is a Postgres/Supabase security feature that controls which rows a logged-in user can read, insert, update, or delete.

Example:

```sql
using (user_id = auth.uid())
```

means:

```txt
Only allow the current logged-in user to access rows where user_id equals their Supabase Auth user ID.
```

`auth.uid()` comes from the signed-in Supabase user’s JWT.

If RLS is enabled and there is **no policy**, frontend clients cannot access that table. That is useful for backend-owned tables. Your FastAPI backend can still manage those tables if it uses the service role key or a backend database connection.

**Current Migration Behavior**

The migration enables RLS on all app tables:

```sql
alter table public.app_users enable row level security;
...
```

So if RLS is currently disabled in your Supabase dashboard, running this migration will enable it for these tables.

But I reduced frontend policies to only these user-facing tables:

```txt
app_users
research_interests
saved_papers
recommendation_feedback
```

The backend-owned tables now have RLS enabled but no frontend policies:

```txt
research_interest_embeddings
papers
paper_embeddings
recommendation_batches
recommendations
```

That means the frontend cannot directly access them through Supabase client APIs. FastAPI should handle those.

**Remaining Policies**

Profile/auth-related table:

```sql
app_users
```

Users can read, create, and update only their own profile row. I did not add delete access.

User-editable app data:

```sql
research_interests
saved_papers
recommendation_feedback
```

Each now has one concise `for all` policy:

```sql
using (user_id = auth.uid())
with check (user_id = auth.uid())
```

Meaning:

```txt
Users can only read/change their own rows.
Users can only create/update rows assigned to themselves.
```

This keeps Supabase RLS as a simple safety layer while leaving the main business rules in FastAPI, which is cleaner for your project.

### User 20

I see. So if we have our own backend service that we will be communicating with supabase - do we still need RLS and the policies?

### Assistant 20

Strictly speaking: **no, you do not need RLS policies if only your backend talks to Supabase**.

But in a Supabase project, I would still recommend enabling RLS as a safety guardrail.

The important distinction is:

```txt
Frontend using Supabase client directly
-> RLS policies are necessary

Frontend only talks to your FastAPI backend
-> backend authorization is the main protection
-> RLS policies are optional guardrails
```

For your architecture:

```txt
React frontend
  -> FastAPI backend
    -> Supabase Postgres
```

you can keep it very simple:

```txt
FastAPI verifies the Supabase Auth token.
FastAPI checks user ownership.
FastAPI reads/writes Supabase Postgres.
```

If FastAPI uses the **service role key**, it bypasses RLS. In that case, RLS policies will not protect you from backend mistakes. Your backend code must enforce authorization carefully.

So you have two reasonable options:

**Option A: Backend-only, minimal DB policies**

```txt
Enable RLS on all public tables.
Add no frontend policies, or only app_users profile policies if needed.
Use FastAPI/service role for all real CRUD.
```

This prevents accidental frontend access through Supabase.

**Option B: Hybrid frontend/backend**

```txt
Enable RLS.
Add policies for tables the frontend directly accesses.
Use FastAPI for complex/backend-owned tables.
```

This is what the current migration now does.

For your project, if you are sure the frontend will **not** directly CRUD tables with Supabase, I’d simplify further:

```txt
Keep RLS enabled.
Remove most policies.
Let FastAPI own CRUD.
Use Supabase Auth only on the frontend.
```

That would mean:

- React uses Supabase only for login/logout/session.
- React sends the Supabase access token to FastAPI.
- FastAPI validates the token.
- FastAPI does database operations.
- Supabase table access from the frontend is blocked by RLS.

This is probably the cleanest separation of concerns.

### User 21

Can you remove the RLS and policy part for now - if we need it we will add it later.

### Assistant 21

Got it. I’ll strip out the RLS enable statements and all policies from the migration so the initial schema stays focused on tables, constraints, triggers, and indexes only.

### Assistant 21

The RLS section is gone. I’ll do a quick scan for any leftover `row level security` or `create policy` lines so we don’t leave half a security block behind.

### Assistant 21

Done. I removed all RLS and policy statements from [20260517055912_create_initial_schema.sql](C:/Users/Danie/Desktop/CS_130_Project/supabase-nextjs/supabase/migrations/20260517055912_create_initial_schema.sql:1).

The migration now contains only:

- extensions
- tables
- constraints
- triggers
- regular indexes
- vector indexes

No remaining `enable row level security` or `create policy` statements were found.

### User 22

Can you suggest how I should update this to supabase?

### Assistant 22

I’ll tailor this to your current repo shape: your migration lives under `supabase-nextjs/supabase/migrations`, so the commands should be run from `supabase-nextjs`, not the outer project folder.

### Assistant 22

I checked the local Supabase config and package file. The CLI is not installed in this project yet, so the cleanest path is to add/use the Supabase CLI, link the remote project, dry-run the migration, then push it.

### Assistant 22

Use the **Supabase CLI migration flow**. Since your migration file is already here:

```txt
supabase-nextjs/supabase/migrations/20260517055912_create_initial_schema.sql
```

run commands from:

```bash
cd supabase-nextjs
```

**Recommended Steps**

1. Install/use the Supabase CLI.

From the Supabase docs, you can run it with `npx`, or install it locally as a dev dependency. The docs note that global npm install is not supported, and Node.js 20+ is required when using npm/npx. Source: [Supabase CLI docs](https://supabase.com/docs/guides/local-development/cli/getting-started).

```bash
npm install supabase --save-dev
```

2. Log in.

```bash
npx supabase login
```

3. Link your local project to your remote Supabase project.

Get your project ref from the Supabase dashboard URL:

```txt
https://supabase.com/dashboard/project/<project-ref>
```

Then run:

```bash
npx supabase link --project-ref <project-ref>
```

4. Preview what will be pushed.

```bash
npx supabase db push --dry-run
```

5. Push the migration.

```bash
npx supabase db push
```

Supabase’s docs describe `db push` as the command that pushes local migrations to the linked remote database, and it tracks applied migrations in `supabase_migrations.schema_migrations`. Source: [Supabase db push reference](https://supabase.com/docs/reference/cli/supabase-db-push).

6. Check Supabase Dashboard.

Go to:

```txt
Supabase Dashboard -> Table Editor
```

You should see tables like:

```txt
app_users
research_interests
papers
paper_embeddings
saved_papers
recommendation_feedback
recommendation_batches
recommendations
```

**Important Note**

If you already manually created tables in the Supabase dashboard, `db push` may fail because the migration tries to create them again. For the cleanest setup, use migrations as the source of truth and avoid editing the remote schema manually. Supabase’s migration docs recommend this team workflow. Source: [Supabase database migrations](https://supabase.com/docs/guides/deployment/database-migrations).

For your project, the short version is:

```bash
cd supabase-nextjs
npm install supabase --save-dev
npx supabase login
npx supabase link --project-ref <project-ref>
npx supabase db push --dry-run
npx supabase db push
```

### User 23

Can you write a brief PR comment and a brief approval mesage for the PR

### Assistant 23

PR comment:

```md
Adds the initial Supabase/Postgres schema for the research paper recommendation app. This includes user/profile data, research interests, paper metadata, embeddings for vector retrieval, saved papers with categorization, recommendation feedback, recommendation batches, and ranked recommendations. Also adds update timestamp triggers and indexes for common user, paper, recommendation, and vector-search queries.

RLS/policies and detailed recommendation reasons are intentionally left out for now so backend authorization and recommendation logic can stay simpler in the MVP.
```

Approval message:

```md
Approved. The migration is a solid initial schema for the MVP and keeps the database design focused without overcommitting to policies or detailed explanation tables too early.
```

### User 24

Can you add a README.MD under the root directory to very briefly explain the process of pushing table modifications through SQL using supabase (i.e. npx install supabase, npx supabase login, npx supabase link, ....).

### Assistant 24

There’s already a root [README.md](C:/Users/Danie/Desktop/CS_130_Project/README.md:1), so on this Windows workspace `README.MD` would refer to the same file. I’ll add a short Supabase migration section there without disturbing the existing project plan.

### Assistant 24

Huh, the file I saw earlier is no longer at the root under that exact name. I’m going to re-list the workspace so I write the note in the right place rather than guessing.

### Assistant 24

The root project description is now `Project_Description.md`, and there is no root README currently. I’ll create a new root `README.md` with just the Supabase SQL migration workflow.

### Assistant 24

The new root README is in place. I’ll quickly read it back to make sure it stayed brief and points to the correct subfolder.

### Assistant 24

Added a new root [README.md](C:/Users/Danie/Desktop/CS_130_Project/README.md:1) with a brief Supabase SQL migration workflow:

- install Supabase CLI locally
- login
- link project
- dry-run migration push
- push migration
- commit migration files

I also noted that commands should be run from `supabase-nextjs`, since that is where the `supabase/` directory lives.

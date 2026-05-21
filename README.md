// [GenAI Use] Prompt: "Based on the design doc, can you come up wth an executable plan for the team. We plan to divide into 3 team as stated in our design doc. Provide the features that each team needs to own and elaborate"
// [GenAI Use] LLM Response Start: 
# CS Capstone Project Plan

## Project Idea

We are building a web app that helps users find research papers that match their interests.

Users can:

- Sign in with a third-party login provider.
- Create a profile.
- Add research interests like topics, fields, authors, and keywords.
- See recommended papers from arXiv.
- Save papers to a reading list.
- Upvote or downvote recommendations.
- View AI-generated summaries for papers.
- Find other researchers with similar interests.

## Main Goal

By the end of the capstone, we should have a working demo where a user can sign in, add research interests, get paper recommendations, save a paper, and view a summary.

## Tech Stack

- Frontend: React and TypeScript
- Backend: Python FastAPI
- Database: PostgreSQL
- Paper source: arXiv API
- Authentication: third-party login provider
- AI feature: LLM API for paper summaries

## Workload Assignment

We will split the 6 people into 3 teams of 2. Each team owns a clear product slice so the recommendation and LLM work is not concentrated in one group.

- Team 1 owns the user-facing app, profile flow, and authentication.
- Team 2 owns paper ingestion, recommendation data, scoring, and feedback.
- Team 3 owns LLM-powered features, summary generation, generated explanations, and AI quality checks.

### Team 1: Frontend UI and User Auth Team

Members: Person 1 and Person 2

Main job: Build the user-facing app, third-party login flow, authenticated user experience, and core profile/interest screens.

Tasks:

- Create and manage the GitHub project board.
- Break the project into weekly tasks.
- Set up the React and TypeScript frontend.
- Build the main pages:
  - Login page
  - Profile page
  - Research interests page
  - Recommendation feed page
  - Reading list page
  - Paper summary page
  - Similar researchers page if time allows
- Create reusable UI components:
  - Paper card
  - Interest tag
  - Profile form
  - Loading message
  - Error message
  - Authenticated page layout
- Add frontend routing and protected pages.
- Integrate a third-party authentication provider.
- Add login, logout, session loading, and current-user UI states.
- Create backend support for current user, profile, and research interest CRUD.
- Set up PostgreSQL tables for:
  - Users
  - Auth provider identities
  - User profiles
  - Research interests
- Connect profile, interest, recommendation, reading list, voting, and summary screens to backend APIs.
- Coordinate with the other teams on API request/response formats.
- Make the app usable on desktop and mobile.
- Prepare the final demo script and presentation flow.

How the two people can split work:

- Person 1: Project board, routing, page layout, auth screens, protected routes, demo flow, final presentation.
- Person 2: UI components, forms, frontend API calls, loading/error states, responsive design.

Final deliverables:

- Project schedule
- GitHub task board
- Working authenticated frontend pages
- Login/logout flow
- Current-user, profile, and interest API routes
- User/profile/interest database tables and migrations
- Reusable UI components
- Connected API calls
- Final demo script

Tech stack/tools:

- React
- TypeScript
- HTML/CSS
- Frontend routing
- Third-party authentication SDK
- Python
- FastAPI
- PostgreSQL
- REST API calls using `fetch` or Axios
- Browser developer tools
- GitHub Projects
- Markdown documentation

### Team 2: Recommendation and Paper Data Team

Members: Person 3 and Person 4

Main job: Build the paper ingestion pipeline, recommendation backend, recommendation storage, saved-paper flow, and feedback logic.

Tasks:

- Set up the FastAPI routes needed for recommendation features.
- Set up PostgreSQL tables for:
  - Papers
  - Recommendation batches
  - Recommendations
  - Saved papers
  - Votes/feedback
- Create migrations and seed data for papers and recommendation testing.
- Connect to the arXiv API.
- Fetch papers based on topics, keywords, authors, or fields.
- Store paper information in the database:
  - Title
  - Authors
  - Abstract
  - arXiv link
  - Published date
  - Categories
- Avoid storing duplicate papers.
- Build a simple recommendation algorithm.
- Match papers to user interests.
- Read user interest data from Team 1's profile/interest APIs or database tables.
- Create recommendation reasons, such as:
  - Matched keyword
  - Matched author
  - Matched topic
- Save recommendations so the feed does not change every time the page reloads.
- Create backend routes for:
  - Recommended papers
  - Saved papers
  - Paper feedback
  - Recommendation refresh
- Add request validation and error responses for recommendation endpoints.
- Provide API documentation for Team 1 and Team 3.

How the two people can split work:

- Person 3: arXiv ingestion, paper storage, duplicate detection, paper seed data.
- Person 4: recommendation scoring, recommendation reasons, saved papers, votes/feedback, recommendation API routes.

Final deliverables:

- arXiv ingestion script/service
- Paper database tables and migrations
- Recommendation database tables and migrations
- Paper matching logic
- Recommendation scoring logic
- Recommendation explanation logic
- Saved-paper and feedback endpoints
- API documentation for recommendation endpoints

Tech stack/tools:

- Python
- FastAPI
- PostgreSQL
- SQL
- Database migrations
- ORM or query layer used by the backend
- Pydantic
- REST APIs
- arXiv API
- Basic text matching
- Recommendation scoring logic

### Team 3: LLM Features and AI Quality Team

Members: Person 5 and Person 6

Main job: Build the LLM-backed features, including paper summaries, generated recommendation explanations, summary storage, prompt design, and AI feature testing.

Tasks:

- Choose and configure the LLM API used by the project.
- Create the paper summary feature.
- Generate short summaries from paper title and abstract.
- Save summaries in the database.
- Create PostgreSQL tables for:
  - Paper summaries
  - LLM requests/responses metadata
  - AI feature error logs if time allows
- Create backend routes for:
  - Generate paper summary
  - Retrieve stored paper summary
  - Regenerate summary if needed
- Design prompts for concise, useful, student-friendly paper summaries.
- Add safeguards for missing abstracts, long abstracts, API failures, and rate limits.
- Work with Team 2 to use paper and recommendation data as LLM input.
- Optionally generate richer recommendation explanations from matched interests and paper metadata.
- Add loading, success, and failure behavior requirements for Team 1.
- Write a manual testing checklist for LLM features.
- Test summary quality against sample papers.
- Help the team find and fix bugs before the final demo.

How the two people can split work:

- Person 5: LLM API integration, prompt design, summary generation endpoint, summary storage.
- Person 6: AI feature QA, error handling, generated explanation experiments, manual testing checklist, final demo testing.

Final deliverables:

- Paper summary feature
- LLM API integration
- Prompt templates
- Summary storage table and migrations
- Summary generation and retrieval endpoints
- AI error handling
- Summary quality checklist
- Manual testing checklist
- Bug report list
- Final demo test results

Tech stack/tools:

- Python
- FastAPI
- PostgreSQL
- LLM API for summaries
- Prompt engineering
- Pydantic
- REST APIs
- Manual testing checklist
- Frontend/backend integration testing

## Team Overlap Plan

The teams should not work completely separately. These are the main overlap points:

- Team 1 and Team 2 work together on the interest data model, recommendation feed API, saved-paper API, and voting API.
- Team 1 and Team 3 work together on summary UI states, summary API responses, and how AI-generated text appears in the app.
- Team 2 and Team 3 work together on paper metadata, recommendation reasons, summary inputs, and generated explanation inputs.
- All teams agree on user IDs, paper IDs, shared API response formats, and database relationships before implementation.
- All teams test the final demo flow together every week.

## MVP Features

These are the features we should finish first:

- User login
- User profile
- Add/edit/delete research interests
- Fetch papers from arXiv
- Generate paper recommendations
- Show recommendation feed
- Show why each paper was recommended
- Save papers to reading list
- Upvote/downvote papers
- Generate text summaries

## Extra Features If Time Allows

- Email notification settings
- Similar researcher discovery
- Public/private profile setting
- Automatic paper categories
- Video summaries
- Scheduled daily or weekly recommendation updates

## Simple Timeline

| Week | Goal | Main Work |
| --- | --- | --- |
| 1 | Setup | Repo setup, team roles, API contracts, frontend/backend/database skeleton |
| 2 | User basics | Login, logout, user profile, users/profiles tables |
| 3 | Interests | Add, edit, delete research interests and expose interest data to recommendations |
| 4 | Papers | Fetch, de-duplicate, and store papers from arXiv |
| 5 | Recommendations | Match papers to user interests, store recommendation batches, and show feed |
| 6 | Reading list and voting | Save papers, upvote/downvote papers, and use feedback in recommendations |
| 7 | AI summaries | Generate, store, retrieve, and display paper summaries |
| 8 | LLM explanations / polish | Improve generated explanations, refine UI states, and add extra features if time allows |
| 9 | Testing | Fix bugs, test main flows, prepare demo data |
| 10 | Final demo | Finish report, slides, and presentation |

## Weekly Team Workflow

- Monday: Assign tasks for the week.
- During the week: Each team works on its assigned part.
- Before merging: At least one teammate reviews the pull request.
- Friday: Run the app together and check what works.
- End of week: Update the project board and move unfinished tasks to next week.

## Final Demo Flow

1. User signs in.
2. User creates a profile.
3. User adds research interests.
4. App fetches papers from arXiv.
5. App shows recommended papers.
6. User sees why a paper was recommended.
7. User saves a paper.
8. User upvotes or downvotes a paper.
9. User views an AI-generated summary.
10. User views similar researchers if that feature is finished.

## Definition of Done

A task is done when:

- The feature works in the browser or API.
- The data is saved correctly.
- Errors are handled.
- Another teammate reviewed it.
- It can be shown in the final demo.
- Setup instructions are updated if needed.

// [GenAI Use] LLM Response End
// [GenAI Use] Reflection: I've been read through the this markdown file and believes that it is correct and it is exactly what I want. First, the design decisions are based on your design doc and are clear. The division of labor makes sense and fair. Our everyone in the team internally agrees with this division of labor, and believe this markdown would be a great tracker. 
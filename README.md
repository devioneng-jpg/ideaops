# IdeaOps v1

Turn a raw idea into a structured, actionable project brief using a multi-agent AI pipeline.

## How It Works

Submit an idea via web form or SMS. A **supervisor + specialists** workflow
(LangGraph) dispatches one specialist agent at a time and routes deterministically
between them:

1. **Classifies** it (category, audience, effort, urgency)
2. **Scores** it (novelty, feasibility, portfolio value, business value)
3. **Plans** an MVP (scope, 30-day plan, risks, metrics)
4. **Breaks it into tasks** (8-15 prioritized, estimated tasks)
5. **Publishes** everything to a Notion page

All data is persisted in Supabase. Results are returned as JSON (web) or SMS.

## Architecture

```
Next.js Web Form ──→ POST /api/ideas ──→ FastAPI ──→ LangGraph Supervisor ──→ Supabase
Twilio SMS ────────→ POST /api/twilio/inbound ──┘     (classify → score →     │
                                                       plan → tasks →          ▼
                                                       publish)           Notion Page
```

## Project Structure

```
ideaops/
├── apps/
│   ├── api/                        # FastAPI backend + LangGraph agents
│   │   ├── app/
│   │   │   ├── main.py             # FastAPI app entry point
│   │   │   ├── config.py           # Settings (env vars, Pydantic)
│   │   │   ├── agents/             # Specialist agent implementations
│   │   │   │   ├── base.py         # Shared LLM client + structured call helper
│   │   │   │   ├── classifier.py   # Step 1: Classify idea
│   │   │   │   ├── scoring.py      # Step 2: Score idea
│   │   │   │   ├── planner.py      # Step 3: Generate MVP brief
│   │   │   │   ├── task_breakdown.py  # Step 4: Break into tasks
│   │   │   │   └── notion_publisher.py  # Step 5: Publish to Notion
│   │   │   ├── prompts/            # LLM prompt templates per agent
│   │   │   ├── models/             # Pydantic request/response schemas
│   │   │   ├── routes/             # API route handlers
│   │   │   │   ├── ideas.py        # POST/GET /api/ideas
│   │   │   │   ├── twilio.py       # POST /api/twilio/inbound
│   │   │   │   └── health.py       # GET /api/health
│   │   │   └── services/           # Business logic
│   │   │       ├── workflow.py     # LangGraph supervisor + specialist nodes
│   │   │       ├── supabase.py     # DB operations
│   │   │       ├── notion.py       # Notion API client + page builder
│   │   │       └── twilio.py       # SMS client
│   │   ├── tests/                  # Unit tests (all LLM/DB mocked)
│   │   └── evals/                  # Golden set evaluation runner
│   │
│   └── web/                        # Next.js 15 frontend
│       └── src/
│           ├── app/                # Pages (home, ideas history)
│           ├── components/         # UI (form, progress steps, results, task table)
│           └── lib/api.ts          # API client + polling logic
│
├── supabase/
│   └── migrations/                 # Postgres schema (4 tables)
└── packages/shared/                # Shared utilities (future)
```

## Agents

The pipeline uses a **supervisor + specialists** architecture built on LangGraph. The supervisor is a deterministic, rule-based router (no LLM) — it inspects the workflow state and dispatches the next specialist that hasn't run yet. Every specialist (except the Notion publisher) is a single-shot LLM call using Claude Sonnet at temperature 0.0.

### Pipeline

```
Supervisor ─→ Classifier ─→ Supervisor ─→ Scorer ─→ Supervisor ─→ Planner
           ─→ Supervisor ─→ Task Breakdown ─→ Supervisor ─→ Notion Publisher
           ─→ Supervisor ─→ Finalize
```

The supervisor checks which outputs exist in the run state and always routes to the first missing step. If any step sets `status="failed"`, the supervisor short-circuits to `finalize`. If Notion fails, the run completes as `partial_success` (all structured outputs are already saved).

### Specialist Agents

| # | Agent | File | Input | Output | Max Tokens |
|---|-------|------|-------|--------|------------|
| 1 | **Classifier** | `agents/classifier.py` | Raw idea text | `category`, `audience`, `problem_statement`, `effort_level`, `urgency`, `confidence` | 1024 |
| 2 | **Scorer** | `agents/scoring.py` | Idea text + classifier output | `novelty_score`, `feasibility_score`, `portfolio_value_score`, `business_value_score`, `total_score`, `rationale` | 1024 |
| 3 | **Planner** | `agents/planner.py` | Idea text + classifier + scoring | `one_sentence_summary`, `problem`, `target_user`, `proposed_solution`, `mvp_scope`, `non_goals`, `thirty_day_plan`, `risks`, `success_metrics` | 2048 |
| 4 | **Task Breakdown** | `agents/task_breakdown.py` | Planning output | 8-15 `TaskItem`s, each with `title`, `description`, `priority`, `order_index`, `estimated_hours` | 2048 |
| 5 | **Notion Publisher** | `agents/notion_publisher.py` | All previous outputs | `notion_page_id`, `notion_url` | N/A |

### Agent Details

**Classifier** — Categorizes the idea into one of 7 types (`saas`, `internal_tool`, `ai_agent`, `content`, `marketplace`, `workflow_automation`, `other`), identifies the target audience, distills the core problem, and estimates effort and urgency.

**Scorer** — Rates the idea on four dimensions (1-10 each): novelty, feasibility, portfolio value, and business value. The total score is a weighted average (0.2 novelty + 0.3 feasibility + 0.2 portfolio + 0.3 business) with a rationale explaining the scores.

**Planner** — Generates a full MVP project brief: one-sentence summary, problem/user/solution definition, 4-8 MVP scope features, explicit non-goals, a week-by-week 30-day plan, 3-5 risks, and 3-5 success metrics.

**Task Breakdown** — Decomposes the plan into 8-15 concrete, ordered tasks. Each task has a priority (high/medium/low) and an estimated hours figure. Tasks are ordered logically: setup, core features, testing, deployment.

**Notion Publisher** — Not an LLM agent. Calls the Notion API to create a page under the configured parent page with the full project brief, scoring, tasks (as to-do items), and all metadata. Failures are non-fatal (`partial_success`).

### Shared Infrastructure (`agents/base.py`)

All LLM agents use `call_structured()`, which:
1. Sends the prompt to Claude via `ChatAnthropic`
2. Extracts JSON from the response (strips markdown fences and surrounding prose)
3. Parses it into a typed Pydantic model
4. Retries up to 2 times on transient errors or JSON parse failures

### Run Statuses

| Status | Meaning |
|--------|---------|
| `running` | Pipeline is actively executing |
| `completed` | All 5 steps succeeded, including Notion publish |
| `partial_success` | Analysis succeeded but Notion publish failed — all structured outputs are saved |
| `failed` | A core step (classify/score/plan/tasks) failed; pipeline short-circuited |

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- A Supabase project
- Anthropic API key
- Notion integration + parent page ID
- (Optional) Twilio account for SMS

### 1. Database

Run the migration against your Supabase database:

```sql
-- Copy contents of supabase/migrations/001_initial_schema.sql
-- and execute in Supabase SQL Editor
```

### 2. Backend

```bash
cd apps/api
cp .env.example .env
# Fill in all values in .env

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd apps/web
cp .env.example .env.local
# Set NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

npm install
npm run dev
```

The frontend runs at `http://localhost:3000`.

### 4. Twilio SMS (Optional)

1. Configure your Twilio phone number's webhook URL to `POST https://<your-host>/api/twilio/inbound`
2. For local dev, use ngrok: `ngrok http 8000`
3. Text your idea to the Twilio number — you'll get an instant "on it" reply, then a second SMS with the brief once the run finishes.

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/ideas` | Submit idea; runs the pipeline in the background and returns `{idea_id, run_id, status: "processing"}` to poll |
| `GET` | `/api/ideas` | List all submitted ideas |
| `GET` | `/api/ideas/{id}` | Get idea with full run details (poll this for terminal status) |
| `POST` | `/api/twilio/inbound` | Twilio SMS webhook (acks instantly, texts the brief when ready) |
| `GET` | `/api/health` | Health check |

**Execution model:** the workflow runs as a FastAPI background task, so submissions
return immediately. The web UI polls `GET /api/ideas/{id}` until the run reaches a
terminal status (`completed` / `failed` / `partial_success`); SMS callers get the
result pushed back as an outbound message.

## Development

Run from `apps/api`:

```bash
# Unit tests — mock all LLM/DB calls, no secrets needed
pip install -r requirements-dev.txt
python -m pytest

# Eval the agents against the golden set — needs a real ANTHROPIC_API_KEY in .env
python -m evals.run_evals
```

CI (`.github/workflows/ci.yml`) runs the unit tests on every PR.

## Environment Variables

### Backend (`apps/api/.env`)

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `NOTION_API_KEY` | Notion integration token |
| `NOTION_PARENT_ID` | Notion page ID to create sub-pages under |
| `TWILIO_ACCOUNT_SID` | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | Twilio auth token |
| `TWILIO_PHONE_NUMBER` | Twilio phone number (E.164 format) |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key |

### Frontend (`apps/web/.env.local`)

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_BASE_URL` | Backend URL (default: `http://localhost:8000`) |

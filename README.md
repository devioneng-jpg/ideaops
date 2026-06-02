# IdeaOps v1

Turn a raw idea into a structured, actionable project brief using a multi-agent AI pipeline.

## How It Works

Submit an idea via web form or SMS. A sequential agent pipeline:

1. **Classifies** it (category, audience, effort, urgency)
2. **Scores** it (novelty, feasibility, portfolio value, business value)
3. **Plans** an MVP (scope, 30-day plan, risks, metrics)
4. **Breaks it into tasks** (8-15 prioritized, estimated tasks)
5. **Publishes** everything to a Notion page

All data is persisted in Supabase. Results are returned as JSON (web) or SMS.

## Architecture

```
Next.js Web Form ──→ POST /api/ideas ──→ FastAPI ──→ LangGraph Workflow ──→ Supabase
Twilio SMS ────────→ POST /api/twilio/inbound ──┘        │
                                                          ▼
                                                     Notion Page
```

## Project Structure

```
ideaops/
├── apps/
│   ├── web/          # Next.js 15 frontend
│   └── api/          # FastAPI backend + LangGraph agents
├── supabase/
│   └── migrations/   # Postgres schema
└── README.md
```

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
3. Text your idea to the Twilio number

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/ideas` | Submit idea, run pipeline, return result |
| `GET` | `/api/ideas` | List all submitted ideas |
| `GET` | `/api/ideas/{id}` | Get idea with full run details |
| `POST` | `/api/twilio/inbound` | Twilio SMS webhook |
| `GET` | `/api/health` | Health check |

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

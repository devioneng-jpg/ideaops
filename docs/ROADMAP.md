# IdeaOps — Architecture & Roadmap

**Pattern:** Supervisor + specialists (deterministic, no autonomous loops).
**Audience:** Personal / single-product infra — no multi-tenancy, OAuth, or RLS in v1.

> This supersedes an earlier draft that proposed tool-using agents with live web
> research. Per the v1 spec, web research and tool loops are **out of scope** — v1
> is a deterministic supervisor over single-shot specialist agents.

---

## Multi-agent design (implemented)

A central `supervisor` node owns orchestration. It runs no LLM: it inspects run
state and deterministically dispatches the next specialist, then each specialist
returns to the supervisor.

```
supervisor → classify → supervisor → score → supervisor → plan
          → supervisor → break_down_tasks → supervisor → publish_notion
          → supervisor → finalize → END
```

| Specialist | In | Out |
|------------|----|----|
| Classifier | raw idea | category (fixed taxonomy), audience, problem, effort, urgency, confidence |
| Scoring | idea + classifier | novelty / feasibility / portfolio / business / total (1–10) + rationale |
| Planning | idea + classifier + scoring | summary, problem, user, solution, MVP scope, non-goals, 30-day plan, risks, metrics |
| Task Breakdown | planning | 8–15 prioritized, estimated tasks |
| Notion Publisher | full plan | Notion page + URL (side-effect) |

**Failure handling:** any specialist failure sets `status=failed` and the
supervisor routes straight to `finalize`. A Notion failure is softer — the
structured outputs are already persisted, so the run ends `partial_success`.

**Shared agent runtime:** `app/agents/base.py` centralizes the LLM client,
structured JSON parsing, retry-on-transient/parse-error, and clean failure logging.
Every specialist is a pure typed function on top of it.

---

## Done

- Supervisor + specialists LangGraph workflow (`services/workflow.py`)
- Fixed classifier taxonomy enum (`saas, internal_tool, ai_agent, content, marketplace, workflow_automation, other`)
- Retry + structured-parse helper around every LLM call (`agents/base.py`)
- Per-step observability in `agent_step_logs`
- Two intake channels (web form + Twilio inbound), Notion publishing, Supabase persistence
- Bug fixes: valid model id, deterministic temperature, TwiML output escaping
- **Async execution** — `POST /api/ideas` runs the pipeline as a FastAPI
  background task and returns `processing`; the web UI polls for the terminal
  status, and SMS callers get an instant ack plus an outbound result message.
  (Lightweight: no external job queue.)
- **Eval harness + CI** — golden set + offline runner (`evals/`), mocked-LLM unit
  tests for the supervisor, retry helper, and full graph wiring (`tests/`), and a
  GitHub Actions workflow that runs them on every PR.

---

## Candidate next steps (post-v1, not started)

Kept here so they aren't lost — none are in the v1 scope.

1. **Per-step cost/latency/token capture** — extend `agent_step_logs` with
   `model`, `input_tokens`, `output_tokens`, `latency_ms`, `cost_usd`. Would also
   let the eval runner report tokens/$ per idea.
2. **Twilio signature validation** — verify `X-Twilio-Signature` to stop
   unauthenticated webhook hits burning credits.
3. **Durable async** — if single-user background tasks become a bottleneck, move
   to a real queue (Redis/RQ) with retry/visibility. Not needed at current scale.

## Explicitly out of scope for v1

OAuth / multi-user auth · web research agent · tool-using/autonomous loops ·
Slack/Linear/Calendar integrations · approval queues · async job queue · RAG/vector
memory · MCP.

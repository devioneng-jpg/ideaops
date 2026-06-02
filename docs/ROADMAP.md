# IdeaOps → Agentic Harness: Roadmap

**Direction:** Make IdeaOps genuinely agentic (single-purpose).
**Audience:** Personal / single-product infra — skip multi-tenancy, RLS, heavy auth.
**Status:** Plan only. No implementation has landed yet.

---

## Framing decision

Don't make *every* step an agent. A tool-using loop is the right tool for steps
where the model needs **external facts or iteration**, and pure overhead for steps
that are deterministic transforms.

| Step | Today | Recommend | Why |
|------|-------|-----------|-----|
| Classify | single-shot | **structured single-shot** (keep) | Pure categorization, no external facts needed |
| Score | single-shot | **agentic (tools)** | Novelty/feasibility genuinely need prior-art & competitor lookup |
| Plan | single-shot | **agentic (light tools)** | Benefits from tech/risk/market lookups, but bounded |
| Break down tasks | single-shot | **structured single-shot** (keep) | Deterministic decomposition |
| Publish Notion | direct API | **keep as a service** (or a single tool call) | Deterministic side-effect, no reasoning |

The "harness" is the shared machinery underneath *both* modes. That's the real deliverable.

---

## Phase 0 — Bug fixes & safety (half day, do first)

Independent of the agentic refactor; should land regardless.

1. **`config.py:18`** — `"sonnet-4-20250514"` → `"claude-sonnet-4-20250514"` (missing `claude-` prefix → 404s).
2. **`twilio.py:62`** — XML-escape `reply_body` before interpolating into TwiML (injection / invalid XML on `<`/`&`).
3. **`twilio.py:15`** — validate `X-Twilio-Signature` (Twilio `RequestValidator`). Cheap; stops randoms burning Anthropic credits.
4. **`supabase.py:10`** — memoize the client (module-level singleton) instead of rebuilding per call.
5. SMS length guard: truncate `reply_body` to Twilio's 1600-char limit.

---

## Phase 1 — The harness core: an `Agent` abstraction (1–2 days)

Today every node in `workflow.py` hand-rolls the same try/except/log/update. Replace with one wrapper.

**New: `app/runtime/agent.py`** — a base every agent runs through, providing:
- LLM client construction + reuse (one client, not per-call)
- **Structured output** via `.with_structured_output(Model)` (kills brittle `json.loads`) + **one repair retry** on validation failure
- **Retries w/ exponential backoff** on 429/529/timeouts (tenacity)
- **Per-call timeout**
- **Metric capture**: input/output tokens, latency, model, estimated $ — written to step logs
- Uniform step logging so `workflow.py` nodes shrink to ~3 lines each

**New: `app/runtime/types.py`** — `AgentResult` (output + usage + tool trace).

**Schema add (`002_*.sql`)**: extend `agent_step_logs` with `model`, `input_tokens`,
`output_tokens`, `latency_ms`, `cost_usd`, `tool_calls jsonb`.

**Outcome:** the five agent files collapse to "prompt + output model + (optional) tools."
Reliability and cost tracking come for free.

---

## Phase 2 — Tools + tool registry + agent loop (2–3 days)

What makes them *agents*.

**New: `app/runtime/tools.py`** — registry + base `Tool` (name, description, args schema, `run()`).

**Starter tools:**
- `web_search` — prior-art / competitor lookup (drives Scoring's novelty + feasibility).
- `fetch_url` — read a competitor/landing page.
- *(optional later)* `notion_search` — check if a similar brief already exists before publishing.

**New: `app/runtime/loop.py`** — bounded reason-act-observe loop: call model with tools →
execute tool calls → feed results back → repeat until final structured answer or
`max_iterations` (hard cap, e.g. 5). Every tool call logged to the trace.

**Refactor Score & Plan** onto the loop with tools; Classify & Task-breakdown stay
structured single-shot on the Phase-1 base. Same `Agent` interface, two execution strategies.

---

## Phase 3 — Async execution (1–2 days, prerequisite for agentic UX)

Agent loops make runs *longer*, and Twilio already can't survive a 30–60s synchronous
run (`twilio.py:34`). For a single-user setup, avoid heavy infra:

- **Submit returns `run_id` immediately**; pipeline runs in a background task
  (FastAPI `BackgroundTasks` or a worker thread/`asyncio` task). The DB run row is the truth.
- **Web**: `page.tsx` polls `GET /api/ideas/{id}` for status. Optional SSE later.
- **Twilio**: reply instantly ("Got it — brief incoming"), then **send the result via a
  second outbound SMS** when the run finishes (reuse `send_sms`). Removes the timeout entirely.
- Add an **idempotency key** (hash of phone+body within N minutes) so Twilio retries don't double-spend.

---

## Phase 4 — Eval harness (1–2 days)

Without this you can't tell whether "agentic" beats single-shot — you'd just pay more on faith.

- **`evals/` golden set**: ~15–20 sample ideas with expected category / score ranges / sanity checks.
- A runner reporting: schema-validity rate, score distribution, **tokens & $ per run**,
  latency, tool-call counts.
- **Unit tests** (mocked LLM): retry fires on 529, repair retry on bad JSON, loop respects
  `max_iterations`, Twilio signature rejects bad sigs.
- **CI**: `.github/workflows/ci.yml` running lint + mocked unit tests on PRs (none exists today).
- **`Dockerfile`** for the API so runs are reproducible.

---

## Sequencing

```
Phase 0  (fixes)        -- independent, do now
Phase 1  (Agent core)   -- foundation everything else sits on
Phase 3  (async)        -- can run parallel to Phase 1; unblocks Twilio
Phase 2  (tools/loop)   -- depends on Phase 1
Phase 4  (eval)         -- after Phase 2 so you can A/B agentic vs single-shot
```

Phases 0/1/3 alone lift the "runtime" grade from C– to a solid B. Phase 2 earns the
word "agentic." Phase 4 keeps it honest.

---

## Open questions before building

1. **Search provider** — Tavily / Brave / Exa / SerpAPI / Anthropic native web search?
   Default pick: Anthropic's server-side web search tool (least plumbing).
2. **Background execution** — FastAPI `BackgroundTasks` / worker thread now, or a real
   queue (Redis/RQ) from the start? For "just me," start with the former.
3. **Per-run cost ceiling** — hard `max_iterations` + token budget per run so an agent
   loop can't runaway-spend? Default: yes.

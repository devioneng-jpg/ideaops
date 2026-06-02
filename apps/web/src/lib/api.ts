const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export interface IdeaSubmissionResponse {
  idea_id: string;
  run_id: string;
  status: string;
  summary: string | null;
  category: string | null;
  total_score: number | null;
  notion_url: string | null;
}

export interface TaskItem {
  title: string;
  description: string;
  priority: "high" | "medium" | "low";
  order_index: number;
  estimated_hours: number;
}

export interface WorkflowRunResponse {
  idea_id: string;
  run_id: string;
  raw_text: string;
  source: string;
  status: string;
  classifier_output: {
    category: string;
    audience: string;
    problem_statement: string;
    effort_level: string;
    urgency: string;
    confidence: number;
  } | null;
  scoring_output: {
    novelty_score: number;
    feasibility_score: number;
    portfolio_value_score: number;
    business_value_score: number;
    total_score: number;
    rationale: string;
  } | null;
  planning_output: {
    one_sentence_summary: string;
    problem: string;
    target_user: string;
    proposed_solution: string;
    mvp_scope: string[];
    non_goals: string[];
    thirty_day_plan: string[];
    risks: string[];
    success_metrics: string[];
  } | null;
  task_output: {
    tasks: TaskItem[];
  } | null;
  notion_page_id: string | null;
  notion_url: string | null;
  error_message: string | null;
}

export async function submitIdea(
  ideaText: string
): Promise<IdeaSubmissionResponse> {
  const res = await fetch(`${API_BASE}/api/ideas`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ idea_text: ideaText, source: "web" }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function getIdea(ideaId: string): Promise<WorkflowRunResponse> {
  const res = await fetch(`${API_BASE}/api/ideas/${ideaId}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

const TERMINAL_STATUSES = new Set(["completed", "failed", "partial_success"]);

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Poll the idea endpoint until its run reaches a terminal status.
 * The pipeline now runs in the background, so the client waits here.
 */
export async function pollIdea(
  ideaId: string,
  { intervalMs = 2000, timeoutMs = 180000 }: { intervalMs?: number; timeoutMs?: number } = {}
): Promise<WorkflowRunResponse> {
  const deadline = Date.now() + timeoutMs;
  for (;;) {
    try {
      const run = await getIdea(ideaId);
      if (TERMINAL_STATUSES.has(run.status)) return run;
    } catch (err) {
      // The run row may not be queryable for a beat after submit — keep polling until the deadline.
      if (Date.now() > deadline) throw err;
    }
    if (Date.now() > deadline) {
      throw new Error("Timed out waiting for the workflow to finish.");
    }
    await sleep(intervalMs);
  }
}

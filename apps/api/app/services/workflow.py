"""LangGraph supervisor + specialists workflow for IdeaOps.

A deterministic `supervisor` node routes to one specialist at a time, and every
specialist returns to the supervisor, which decides what runs next:

    supervisor → classify → supervisor → score → supervisor → plan
              → supervisor → break_down_tasks → supervisor → publish_notion
              → supervisor → finalize

Routing is rule-based (no LLM, no autonomous loops) so v1 runs are reproducible.
Each specialist logs to agent_step_logs. A failure short-circuits the pipeline:
the supervisor routes straight to `finalize`. A Notion failure is softer — the
structured outputs are already saved, so the run ends as `partial_success`.
"""

import logging
from typing import Any, TypedDict

from langgraph.graph import StateGraph, END

from app.models.agent_outputs import (
    ClassifierOutput,
    ScoringOutput,
    PlanningOutput,
    TaskBreakdownOutput,
)
from app.agents.classifier import run_classifier
from app.agents.scoring import run_scoring
from app.agents.planner import run_planner
from app.agents.task_breakdown import run_task_breakdown
from app.agents.notion_publisher import run_notion_publisher
from app.services import supabase as db

logger = logging.getLogger(__name__)


# ── State ─────────────────────────────────────────────────────────────────────

class WorkflowState(TypedDict, total=False):
    # Inputs
    idea_text: str
    run_id: str
    idea_id: str

    # Agent outputs
    classifier_output: ClassifierOutput
    scoring_output: ScoringOutput
    planning_output: PlanningOutput
    task_output: TaskBreakdownOutput
    notion_page_id: str
    notion_url: str

    # Control
    next: str
    status: str
    error_message: str


# ── Supervisor ────────────────────────────────────────────────────────────────

# The specialists, in the fixed order the supervisor dispatches them.
SPECIALISTS = ["classify", "score", "plan", "break_down_tasks", "publish_notion"]


def supervisor(state: WorkflowState) -> dict[str, Any]:
    """Pick the next specialist to run, or finalize on completion/failure.

    Deterministic and rule-based: it inspects which outputs already exist and
    routes to the first missing step. A failed status routes straight to finalize.
    """
    if state.get("status") == "failed":
        nxt = "finalize"
    elif "classifier_output" not in state:
        nxt = "classify"
    elif "scoring_output" not in state:
        nxt = "score"
    elif "planning_output" not in state:
        nxt = "plan"
    elif "task_output" not in state:
        nxt = "break_down_tasks"
    elif "notion_page_id" not in state and state.get("status") != "partial_success":
        nxt = "publish_notion"
    else:
        nxt = "finalize"

    logger.info("Supervisor → %s (run %s)", nxt, state.get("run_id"))
    return {"next": nxt}


def route(state: WorkflowState) -> str:
    """Conditional-edge selector — hands control to the node the supervisor chose."""
    return state["next"]


# ── Specialist nodes ──────────────────────────────────────────────────────────
# The supervisor guarantees a node only runs when its turn comes, so these don't
# re-check upstream status — they just do their work and report back.

def classify(state: WorkflowState) -> dict[str, Any]:
    run_id = state["run_id"]
    idea_text = state["idea_text"]

    db.log_step(run_id, "classify", "started", input_json={"idea_text": idea_text})
    try:
        output = run_classifier(idea_text)
        db.log_step(run_id, "classify", "completed", output_json=output.model_dump())
        db.update_run(run_id, classifier_output=output.model_dump())
        return {"classifier_output": output}
    except Exception as e:
        logger.exception("Classifier failed")
        db.log_step(run_id, "classify", "failed", error_message=str(e))
        return {"status": "failed", "error_message": f"Classifier failed: {e}"}


def score(state: WorkflowState) -> dict[str, Any]:
    run_id = state["run_id"]
    db.log_step(run_id, "score", "started")
    try:
        output = run_scoring(state["idea_text"], state["classifier_output"])
        db.log_step(run_id, "score", "completed", output_json=output.model_dump())
        db.update_run(run_id, scoring_output=output.model_dump())
        return {"scoring_output": output}
    except Exception as e:
        logger.exception("Scoring failed")
        db.log_step(run_id, "score", "failed", error_message=str(e))
        return {"status": "failed", "error_message": f"Scoring failed: {e}"}


def plan(state: WorkflowState) -> dict[str, Any]:
    run_id = state["run_id"]
    db.log_step(run_id, "plan", "started")
    try:
        output = run_planner(
            state["idea_text"],
            state["classifier_output"],
            state["scoring_output"],
        )
        db.log_step(run_id, "plan", "completed", output_json=output.model_dump())
        db.update_run(run_id, planning_output=output.model_dump())
        return {"planning_output": output}
    except Exception as e:
        logger.exception("Planner failed")
        db.log_step(run_id, "plan", "failed", error_message=str(e))
        return {"status": "failed", "error_message": f"Planner failed: {e}"}


def break_down_tasks(state: WorkflowState) -> dict[str, Any]:
    run_id = state["run_id"]
    db.log_step(run_id, "break_down_tasks", "started")
    try:
        output = run_task_breakdown(state["planning_output"])
        db.log_step(run_id, "break_down_tasks", "completed", output_json=output.model_dump())
        db.update_run(run_id, task_output=output.model_dump())
        db.save_tasks(run_id, output)
        return {"task_output": output}
    except Exception as e:
        logger.exception("Task breakdown failed")
        db.log_step(run_id, "break_down_tasks", "failed", error_message=str(e))
        return {"status": "failed", "error_message": f"Task breakdown failed: {e}"}


def publish_notion(state: WorkflowState) -> dict[str, Any]:
    run_id = state["run_id"]
    db.log_step(run_id, "publish_notion", "started")
    try:
        result = run_notion_publisher(
            idea_text=state["idea_text"],
            classifier=state["classifier_output"],
            scoring=state["scoring_output"],
            planning=state["planning_output"],
            tasks=state["task_output"],
        )
        db.log_step(run_id, "publish_notion", "completed", output_json=result)
        db.update_run(
            run_id,
            notion_page_id=result["notion_page_id"],
            notion_url=result["notion_url"],
        )
        return {
            "notion_page_id": result["notion_page_id"],
            "notion_url": result["notion_url"],
            "status": "completed",
        }
    except Exception as e:
        # Notion failure → partial_success (other outputs are already saved)
        logger.exception("Notion publisher failed")
        db.log_step(run_id, "publish_notion", "failed", error_message=str(e))
        return {"status": "partial_success", "error_message": f"Notion publish failed: {e}"}


def finalize(state: WorkflowState) -> dict[str, Any]:
    """Terminal node — persists the run's final status to the DB."""
    run_id = state["run_id"]
    idea_id = state["idea_id"]
    status = state.get("status", "completed")
    error_message = state.get("error_message")

    update_fields: dict[str, Any] = {"status": status}
    if error_message:
        update_fields["error_message"] = error_message

    db.update_run(run_id, **update_fields)
    db.update_idea_status(idea_id, status, latest_run_id=run_id)
    return {"status": status}


# ── Graph construction ────────────────────────────────────────────────────────

def build_workflow() -> StateGraph:
    graph = StateGraph(WorkflowState)

    graph.add_node("supervisor", supervisor)
    graph.add_node("classify", classify)
    graph.add_node("score", score)
    graph.add_node("plan", plan)
    graph.add_node("break_down_tasks", break_down_tasks)
    graph.add_node("publish_notion", publish_notion)
    graph.add_node("finalize", finalize)

    # The supervisor is the hub: it routes out to one specialist...
    graph.set_entry_point("supervisor")
    graph.add_conditional_edges(
        "supervisor",
        route,
        {
            "classify": "classify",
            "score": "score",
            "plan": "plan",
            "break_down_tasks": "break_down_tasks",
            "publish_notion": "publish_notion",
            "finalize": "finalize",
        },
    )

    # ...and every specialist reports back to the supervisor.
    for specialist in SPECIALISTS:
        graph.add_edge(specialist, "supervisor")

    graph.add_edge("finalize", END)
    return graph


# Compiled workflow — importable singleton
workflow = build_workflow().compile()


def run_workflow(idea_text: str, idea_id: str, run_id: str) -> WorkflowState:
    """Execute the full IdeaOps supervisor pipeline. Returns the final state."""
    initial_state: WorkflowState = {
        "idea_text": idea_text,
        "idea_id": idea_id,
        "run_id": run_id,
    }
    return workflow.invoke(initial_state)

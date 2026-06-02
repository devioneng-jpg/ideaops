"""LangGraph sequential workflow for IdeaOps.

State flows linearly: classify → score → plan → break_down_tasks → publish_notion.
Each node logs to agent_step_logs. Failures short-circuit the pipeline.
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
    status: str
    error_message: str


# ── Node functions ────────────────────────────────────────────────────────────

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
    if state.get("status") == "failed":
        return {}

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
    if state.get("status") == "failed":
        return {}

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
    if state.get("status") == "failed":
        return {}

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
    if state.get("status") == "failed":
        return {}

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
        # Notion failure → partial_success (other outputs are saved)
        logger.exception("Notion publisher failed")
        db.log_step(run_id, "publish_notion", "failed", error_message=str(e))
        return {"status": "partial_success", "error_message": f"Notion publish failed: {e}"}


def finalize(state: WorkflowState) -> dict[str, Any]:
    """Final node — persists the terminal status to the DB."""
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

    graph.add_node("classify", classify)
    graph.add_node("score", score)
    graph.add_node("plan", plan)
    graph.add_node("break_down_tasks", break_down_tasks)
    graph.add_node("publish_notion", publish_notion)
    graph.add_node("finalize", finalize)

    graph.set_entry_point("classify")
    graph.add_edge("classify", "score")
    graph.add_edge("score", "plan")
    graph.add_edge("plan", "break_down_tasks")
    graph.add_edge("break_down_tasks", "publish_notion")
    graph.add_edge("publish_notion", "finalize")
    graph.add_edge("finalize", END)

    return graph


# Compiled workflow — importable singleton
workflow = build_workflow().compile()


def run_workflow(idea_text: str, idea_id: str, run_id: str) -> WorkflowState:
    """Execute the full IdeaOps pipeline. Returns final state."""
    initial_state: WorkflowState = {
        "idea_text": idea_text,
        "idea_id": idea_id,
        "run_id": run_id,
    }
    result = workflow.invoke(initial_state)
    return result

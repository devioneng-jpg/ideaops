import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.models.requests import IdeaSubmissionRequest
from app.models.responses import IdeaSubmissionResponse, WorkflowRunResponse
from app.models.agent_outputs import (
    ClassifierOutput,
    ScoringOutput,
    PlanningOutput,
    TaskBreakdownOutput,
)
from app.services import supabase as db
from app.services.workflow import run_workflow, SPECIALISTS

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/api/ideas", response_model=IdeaSubmissionResponse)
def submit_idea(req: IdeaSubmissionRequest, background_tasks: BackgroundTasks):
    """Submit an idea and kick off the pipeline in the background.

    Returns immediately with status ``processing``; the client polls
    ``GET /api/ideas/{idea_id}`` for the terminal status and results.
    """
    # 1. Create idea + run records up front so the client has IDs to poll.
    idea = db.create_idea(
        raw_text=req.idea_text,
        source=req.source,
        user_phone=req.user_phone,
    )
    idea_id = idea["id"]
    run = db.create_run(idea_id)
    run_id = run["id"]

    # 2. Run the workflow after the response is sent.
    background_tasks.add_task(
        run_workflow,
        idea_text=req.idea_text,
        idea_id=idea_id,
        run_id=run_id,
    )

    # 3. Acknowledge immediately.
    return IdeaSubmissionResponse(
        idea_id=idea_id,
        run_id=run_id,
        status="processing",
    )


@router.get("/api/ideas")
def list_ideas():
    """List all submitted ideas, most recent first."""
    client = db.get_client()
    result = (
        client.table("idea_submissions")
        .select("*")
        .order("created_at", desc=True)
        .limit(100)
        .execute()
    )
    return result.data


@router.get("/api/ideas/{idea_id}", response_model=WorkflowRunResponse)
def get_idea(idea_id: str):
    """Retrieve a submitted idea with its latest workflow run results."""
    idea = db.get_idea(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    runs = db.get_runs_for_idea(idea_id)
    if not runs:
        raise HTTPException(status_code=404, detail="No runs found for this idea")

    run = runs[0]  # Most recent
    run_id = run["id"]

    # Reconstitute typed outputs from stored JSON
    classifier_output = ClassifierOutput(**run["classifier_output"]) if run.get("classifier_output") else None
    scoring_output = ScoringOutput(**run["scoring_output"]) if run.get("scoring_output") else None
    planning_output = PlanningOutput(**run["planning_output"]) if run.get("planning_output") else None
    task_output = TaskBreakdownOutput(**run["task_output"]) if run.get("task_output") else None

    # Determine current and completed steps from agent_step_logs
    steps = db.get_steps_for_run(run_id)
    completed_steps: list[str] = []
    started_steps: set[str] = set()
    for step in steps:
        if step["status"] == "completed":
            completed_steps.append(step["step_name"])
        elif step["status"] == "started":
            started_steps.add(step["step_name"])

    # current_step = started but not yet completed
    in_progress = started_steps - set(completed_steps)
    if in_progress:
        current_step = in_progress.pop()
    elif run["status"] == "running":
        # Between steps (one completed, next hasn't started yet).
        # Infer the next step from the pipeline order.
        current_step = None
        for s in SPECIALISTS:
            if s not in completed_steps:
                current_step = s
                break
    else:
        current_step = None

    return WorkflowRunResponse(
        idea_id=idea_id,
        run_id=run_id,
        raw_text=idea["raw_text"],
        source=idea["source"],
        status=run["status"],
        classifier_output=classifier_output,
        scoring_output=scoring_output,
        planning_output=planning_output,
        task_output=task_output,
        notion_page_id=run.get("notion_page_id"),
        notion_url=run.get("notion_url"),
        error_message=run.get("error_message"),
        current_step=current_step,
        completed_steps=completed_steps,
    )

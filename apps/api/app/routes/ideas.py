import logging

from fastapi import APIRouter, HTTPException

from app.models.requests import IdeaSubmissionRequest
from app.models.responses import IdeaSubmissionResponse, WorkflowRunResponse
from app.models.agent_outputs import (
    ClassifierOutput,
    ScoringOutput,
    PlanningOutput,
    TaskBreakdownOutput,
)
from app.services import supabase as db
from app.services.workflow import run_workflow

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/api/ideas", response_model=IdeaSubmissionResponse)
def submit_idea(req: IdeaSubmissionRequest):
    """Submit a new idea and run the full agent pipeline."""
    # 1. Create idea record
    idea = db.create_idea(
        raw_text=req.idea_text,
        source=req.source,
        user_phone=req.user_phone,
    )
    idea_id = idea["id"]

    # 2. Create workflow run
    run = db.create_run(idea_id)
    run_id = run["id"]

    # 3. Execute pipeline
    result = run_workflow(
        idea_text=req.idea_text,
        idea_id=idea_id,
        run_id=run_id,
    )

    # 4. Build response
    status = result.get("status", "failed")
    summary = None
    category = None
    total_score = None
    notion_url = result.get("notion_url")

    planning: PlanningOutput | None = result.get("planning_output")
    if planning:
        summary = planning.one_sentence_summary

    classifier: ClassifierOutput | None = result.get("classifier_output")
    if classifier:
        category = classifier.category

    scoring: ScoringOutput | None = result.get("scoring_output")
    if scoring:
        total_score = scoring.total_score

    return IdeaSubmissionResponse(
        idea_id=idea_id,
        run_id=run_id,
        status=status,
        summary=summary,
        category=category,
        total_score=total_score,
        notion_url=notion_url,
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
    )

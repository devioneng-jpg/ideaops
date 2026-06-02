from typing import Optional
from pydantic import BaseModel

from .agent_outputs import (
    ClassifierOutput,
    ScoringOutput,
    PlanningOutput,
    TaskBreakdownOutput,
)


class IdeaSubmissionResponse(BaseModel):
    idea_id: str
    run_id: str
    status: str
    summary: Optional[str] = None
    category: Optional[str] = None
    total_score: Optional[float] = None
    notion_url: Optional[str] = None


class WorkflowRunResponse(BaseModel):
    idea_id: str
    run_id: str
    raw_text: str
    source: str
    status: str
    classifier_output: Optional[ClassifierOutput] = None
    scoring_output: Optional[ScoringOutput] = None
    planning_output: Optional[PlanningOutput] = None
    task_output: Optional[TaskBreakdownOutput] = None
    notion_page_id: Optional[str] = None
    notion_url: Optional[str] = None
    error_message: Optional[str] = None

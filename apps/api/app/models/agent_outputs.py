from typing import Literal
from pydantic import BaseModel, Field


class ClassifierOutput(BaseModel):
    category: str = Field(..., description="Category of the idea, e.g. SaaS, Marketplace, Dev Tool, Mobile App")
    audience: str = Field(..., description="Target audience for this idea")
    problem_statement: str = Field(..., description="Concise problem statement the idea addresses")
    effort_level: Literal["low", "medium", "high"] = Field(..., description="Estimated effort to build")
    urgency: Literal["low", "medium", "high"] = Field(..., description="Market urgency / time-sensitivity")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1 in the classification")


class ScoringOutput(BaseModel):
    novelty_score: float = Field(..., ge=0, le=10, description="How novel is this idea (0-10)")
    feasibility_score: float = Field(..., ge=0, le=10, description="How feasible to build (0-10)")
    portfolio_value_score: float = Field(..., ge=0, le=10, description="Portfolio / learning value (0-10)")
    business_value_score: float = Field(..., ge=0, le=10, description="Business / revenue potential (0-10)")
    total_score: float = Field(..., ge=0, le=10, description="Weighted total score (0-10)")
    rationale: str = Field(..., description="Explanation of the scoring")


class PlanningOutput(BaseModel):
    one_sentence_summary: str
    problem: str
    target_user: str
    proposed_solution: str
    mvp_scope: list[str] = Field(..., description="List of MVP features")
    non_goals: list[str] = Field(..., description="Explicitly out-of-scope items")
    thirty_day_plan: list[str] = Field(..., description="Week-by-week 30-day plan")
    risks: list[str]
    success_metrics: list[str]


class TaskItem(BaseModel):
    title: str
    description: str
    priority: Literal["high", "medium", "low"]
    order_index: int = Field(..., ge=1)
    estimated_hours: float = Field(..., gt=0)


class TaskBreakdownOutput(BaseModel):
    tasks: list[TaskItem] = Field(..., min_length=8, max_length=15)

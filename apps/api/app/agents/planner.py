import logging

from app.agents.base import call_structured, get_llm
from app.models.agent_outputs import ClassifierOutput, PlanningOutput, ScoringOutput
from app.prompts.planner import PLANNER_PROMPT

logger = logging.getLogger(__name__)


def run_planner(
    idea_text: str,
    classifier: ClassifierOutput,
    scoring: ScoringOutput,
) -> PlanningOutput:
    """Generate an MVP project brief and 30-day plan."""
    llm = get_llm(max_tokens=2048)
    prompt = PLANNER_PROMPT.format(
        idea_text=idea_text,
        category=classifier.category,
        audience=classifier.audience,
        problem_statement=classifier.problem_statement,
        effort_level=classifier.effort_level,
        urgency=classifier.urgency,
        total_score=scoring.total_score,
        novelty_score=scoring.novelty_score,
        feasibility_score=scoring.feasibility_score,
        portfolio_value_score=scoring.portfolio_value_score,
        business_value_score=scoring.business_value_score,
        rationale=scoring.rationale,
    )
    return call_structured(llm, prompt, PlanningOutput)

import logging

from app.agents.base import call_structured, get_llm
from app.models.agent_outputs import ClassifierOutput, ScoringOutput
from app.prompts.scoring import SCORING_PROMPT

logger = logging.getLogger(__name__)


def run_scoring(idea_text: str, classifier: ClassifierOutput) -> ScoringOutput:
    """Score an idea across novelty, feasibility, portfolio, and business value."""
    llm = get_llm(max_tokens=1024)
    prompt = SCORING_PROMPT.format(
        idea_text=idea_text,
        category=classifier.category,
        audience=classifier.audience,
        problem_statement=classifier.problem_statement,
        effort_level=classifier.effort_level,
        urgency=classifier.urgency,
    )
    return call_structured(llm, prompt, ScoringOutput)

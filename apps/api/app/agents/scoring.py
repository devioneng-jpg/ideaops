import json
import logging

from langchain_anthropic import ChatAnthropic

from app.config import settings
from app.models.agent_outputs import ClassifierOutput, ScoringOutput
from app.prompts.scoring import SCORING_PROMPT

logger = logging.getLogger(__name__)


def run_scoring(idea_text: str, classifier: ClassifierOutput) -> ScoringOutput:
    """Score an idea across multiple dimensions."""
    llm = ChatAnthropic(
        model=settings.llm_model,
        api_key=settings.anthropic_api_key,
        temperature=settings.llm_temperature,
        max_tokens=1024,
    )

    prompt = SCORING_PROMPT.format(
        idea_text=idea_text,
        category=classifier.category,
        audience=classifier.audience,
        problem_statement=classifier.problem_statement,
        effort_level=classifier.effort_level,
        urgency=classifier.urgency,
    )
    response = llm.invoke(prompt)
    content = response.content

    if isinstance(content, list):
        content = content[0].get("text", "") if content else ""

    parsed = json.loads(content)
    return ScoringOutput(**parsed)

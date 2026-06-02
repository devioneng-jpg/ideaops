import logging

from app.agents.base import call_structured, get_llm
from app.models.agent_outputs import ClassifierOutput
from app.prompts.classifier import CLASSIFIER_PROMPT

logger = logging.getLogger(__name__)


def run_classifier(idea_text: str) -> ClassifierOutput:
    """Classify a raw idea into a structured category, audience, and effort/urgency."""
    llm = get_llm(max_tokens=1024)
    prompt = CLASSIFIER_PROMPT.format(idea_text=idea_text)
    return call_structured(llm, prompt, ClassifierOutput)

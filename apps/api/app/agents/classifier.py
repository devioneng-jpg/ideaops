import json
import logging

from langchain_anthropic import ChatAnthropic

from app.config import settings
from app.models.agent_outputs import ClassifierOutput
from app.prompts.classifier import CLASSIFIER_PROMPT

logger = logging.getLogger(__name__)


def run_classifier(idea_text: str) -> ClassifierOutput:
    """Classify a raw idea into structured categories."""
    llm = ChatAnthropic(
        model=settings.llm_model,
        api_key=settings.anthropic_api_key,
        temperature=settings.llm_temperature,
        max_tokens=1024,
    )

    prompt = CLASSIFIER_PROMPT.format(idea_text=idea_text)
    response = llm.invoke(prompt)
    content = response.content

    if isinstance(content, list):
        content = content[0].get("text", "") if content else ""

    parsed = json.loads(content)
    return ClassifierOutput(**parsed)

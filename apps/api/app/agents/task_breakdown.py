import json
import logging

from langchain_anthropic import ChatAnthropic

from app.config import settings
from app.models.agent_outputs import PlanningOutput, TaskBreakdownOutput
from app.prompts.task_breakdown import TASK_BREAKDOWN_PROMPT

logger = logging.getLogger(__name__)


def run_task_breakdown(planning: PlanningOutput) -> TaskBreakdownOutput:
    """Break a project plan into 8-15 actionable tasks."""
    llm = ChatAnthropic(
        model=settings.llm_model,
        api_key=settings.anthropic_api_key,
        temperature=settings.llm_temperature,
        max_tokens=2048,
    )

    prompt = TASK_BREAKDOWN_PROMPT.format(
        one_sentence_summary=planning.one_sentence_summary,
        problem=planning.problem,
        target_user=planning.target_user,
        proposed_solution=planning.proposed_solution,
        mvp_scope="\n".join(f"- {item}" for item in planning.mvp_scope),
        thirty_day_plan="\n".join(f"- {item}" for item in planning.thirty_day_plan),
    )
    response = llm.invoke(prompt)
    content = response.content

    if isinstance(content, list):
        content = content[0].get("text", "") if content else ""

    parsed = json.loads(content)
    return TaskBreakdownOutput(**parsed)

import logging

from app.agents.base import call_structured, get_llm
from app.models.agent_outputs import PlanningOutput, TaskBreakdownOutput
from app.prompts.task_breakdown import TASK_BREAKDOWN_PROMPT

logger = logging.getLogger(__name__)


def run_task_breakdown(planning: PlanningOutput) -> TaskBreakdownOutput:
    """Break a project plan into 8-15 actionable, prioritized tasks."""
    llm = get_llm(max_tokens=2048)
    prompt = TASK_BREAKDOWN_PROMPT.format(
        one_sentence_summary=planning.one_sentence_summary,
        problem=planning.problem,
        target_user=planning.target_user,
        proposed_solution=planning.proposed_solution,
        mvp_scope="\n".join(f"- {item}" for item in planning.mvp_scope),
        thirty_day_plan="\n".join(f"- {item}" for item in planning.thirty_day_plan),
    )
    return call_structured(llm, prompt, TaskBreakdownOutput)

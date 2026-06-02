import logging

from app.models.agent_outputs import (
    ClassifierOutput,
    ScoringOutput,
    PlanningOutput,
    TaskBreakdownOutput,
)
from app.services.notion import create_idea_page

logger = logging.getLogger(__name__)


def run_notion_publisher(
    idea_text: str,
    classifier: ClassifierOutput,
    scoring: ScoringOutput,
    planning: PlanningOutput,
    tasks: TaskBreakdownOutput,
) -> dict[str, str]:
    """Publish the full structured plan to a Notion page.

    Returns {"notion_page_id": ..., "notion_url": ...}.
    """
    result = create_idea_page(
        idea_text=idea_text,
        classifier=classifier,
        scoring=scoring,
        planning=planning,
        tasks=tasks,
    )
    logger.info("Notion page created: %s", result["notion_url"])
    return result

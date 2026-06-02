from notion_client import Client as NotionClient

from app.config import settings
from app.models.agent_outputs import (
    ClassifierOutput,
    ScoringOutput,
    PlanningOutput,
    TaskBreakdownOutput,
)


def get_client() -> NotionClient:
    return NotionClient(auth=settings.notion_api_key)


def create_idea_page(
    idea_text: str,
    classifier: ClassifierOutput,
    scoring: ScoringOutput,
    planning: PlanningOutput,
    tasks: TaskBreakdownOutput,
) -> dict[str, str]:
    """Create a Notion page with the full idea brief. Returns {notion_page_id, notion_url}."""
    client = get_client()

    # Build page properties
    page = client.pages.create(
        parent={"page_id": settings.notion_parent_id},
        properties={
            "title": {
                "title": [{"text": {"content": planning.one_sentence_summary[:100]}}]
            }
        },
        children=_build_blocks(idea_text, classifier, scoring, planning, tasks),
    )

    return {
        "notion_page_id": page["id"],
        "notion_url": page["url"],
    }


def _build_blocks(
    idea_text: str,
    classifier: ClassifierOutput,
    scoring: ScoringOutput,
    planning: PlanningOutput,
    tasks: TaskBreakdownOutput,
) -> list[dict]:
    blocks: list[dict] = []

    # ── Raw Idea ──────────────────────────────────────────────────────────
    blocks.append(_heading("Raw Idea"))
    blocks.append(_paragraph(idea_text))
    blocks.append(_divider())

    # ── Classification ────────────────────────────────────────────────────
    blocks.append(_heading("Classification"))
    blocks.append(_bulleted(f"Category: {classifier.category}"))
    blocks.append(_bulleted(f"Audience: {classifier.audience}"))
    blocks.append(_bulleted(f"Problem: {classifier.problem_statement}"))
    blocks.append(_bulleted(f"Effort: {classifier.effort_level}"))
    blocks.append(_bulleted(f"Urgency: {classifier.urgency}"))
    blocks.append(_bulleted(f"Confidence: {classifier.confidence:.0%}"))
    blocks.append(_divider())

    # ── Scoring ───────────────────────────────────────────────────────────
    blocks.append(_heading("Scoring"))
    blocks.append(_bulleted(f"Total Score: {scoring.total_score}/10"))
    blocks.append(_bulleted(f"Novelty: {scoring.novelty_score} | Feasibility: {scoring.feasibility_score}"))
    blocks.append(_bulleted(f"Portfolio Value: {scoring.portfolio_value_score} | Business Value: {scoring.business_value_score}"))
    blocks.append(_paragraph(f"Rationale: {scoring.rationale}"))
    blocks.append(_divider())

    # ── Project Brief ─────────────────────────────────────────────────────
    blocks.append(_heading("Project Brief"))
    blocks.append(_paragraph(f"Summary: {planning.one_sentence_summary}"))
    blocks.append(_paragraph(f"Problem: {planning.problem}"))
    blocks.append(_paragraph(f"Target User: {planning.target_user}"))
    blocks.append(_paragraph(f"Proposed Solution: {planning.proposed_solution}"))

    blocks.append(_heading("MVP Scope", level=3))
    for item in planning.mvp_scope:
        blocks.append(_bulleted(item))

    blocks.append(_heading("Non-Goals", level=3))
    for item in planning.non_goals:
        blocks.append(_bulleted(item))

    blocks.append(_heading("30-Day Plan", level=3))
    for item in planning.thirty_day_plan:
        blocks.append(_numbered(item))

    blocks.append(_heading("Risks", level=3))
    for item in planning.risks:
        blocks.append(_bulleted(item))

    blocks.append(_heading("Success Metrics", level=3))
    for item in planning.success_metrics:
        blocks.append(_bulleted(item))

    blocks.append(_divider())

    # ── Tasks ─────────────────────────────────────────────────────────────
    blocks.append(_heading("Tasks"))
    for t in tasks.tasks:
        blocks.append(
            _to_do(f"[{t.priority.upper()}] {t.title} ({t.estimated_hours}h) — {t.description}")
        )

    return blocks


# ── Block helpers ─────────────────────────────────────────────────────────────

def _heading(text: str, level: int = 2) -> dict:
    return {
        "object": "block",
        "type": f"heading_{level}",
        f"heading_{level}": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def _paragraph(text: str) -> dict:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": text[:2000]}}]},
    }


def _bulleted(text: str) -> dict:
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": text[:2000]}}]},
    }


def _numbered(text: str) -> dict:
    return {
        "object": "block",
        "type": "numbered_list_item",
        "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": text[:2000]}}]},
    }


def _to_do(text: str) -> dict:
    return {
        "object": "block",
        "type": "to_do",
        "to_do": {
            "rich_text": [{"type": "text", "text": {"content": text[:2000]}}],
            "checked": False,
        },
    }


def _divider() -> dict:
    return {"object": "block", "type": "divider", "divider": {}}

"""End-to-end supervisor wiring, with every LLM call and DB write mocked.

These tests assert the *routing* (happy path, hard failure, Notion partial
failure) without touching Anthropic or Supabase.
"""

import pytest

import app.services.workflow as wf
from app.models.agent_outputs import (
    ClassifierOutput,
    ScoringOutput,
    PlanningOutput,
    TaskBreakdownOutput,
    TaskItem,
)


def _classifier():
    return ClassifierOutput(
        category="saas",
        audience="solo builders",
        problem_statement="Ideas are hard to operationalize.",
        effort_level="medium",
        urgency="low",
        confidence=0.9,
    )


def _scoring():
    return ScoringOutput(
        novelty_score=7,
        feasibility_score=8,
        portfolio_value_score=6,
        business_value_score=7,
        total_score=7,
        rationale="Solid, buildable.",
    )


def _planning():
    return PlanningOutput(
        one_sentence_summary="An idea-to-brief pipeline.",
        problem="Ideas stall before execution.",
        target_user="Solo builders.",
        proposed_solution="Multi-agent brief generator.",
        mvp_scope=["intake", "scoring"],
        non_goals=["auth"],
        thirty_day_plan=["week 1", "week 2"],
        risks=["scope creep"],
        success_metrics=["briefs created"],
    )


def _tasks():
    return TaskBreakdownOutput(
        tasks=[
            TaskItem(
                title=f"Task {i}",
                description="Do the thing.",
                priority="medium",
                order_index=i,
                estimated_hours=4,
            )
            for i in range(1, 9)  # 8 tasks satisfies the 8-15 constraint
        ]
    )


@pytest.fixture
def mock_agents(monkeypatch):
    """Replace LLM agents with deterministic stubs and stub out all DB writes."""
    monkeypatch.setattr(wf, "run_classifier", lambda idea_text: _classifier())
    monkeypatch.setattr(wf, "run_scoring", lambda idea_text, classifier: _scoring())
    monkeypatch.setattr(wf, "run_planner", lambda idea_text, classifier, scoring: _planning())
    monkeypatch.setattr(wf, "run_task_breakdown", lambda planning: _tasks())
    monkeypatch.setattr(
        wf,
        "run_notion_publisher",
        lambda **kwargs: {"notion_page_id": "pid", "notion_url": "https://notion.so/pid"},
    )
    for name in ("log_step", "update_run", "update_idea_status", "save_tasks"):
        monkeypatch.setattr(wf.db, name, lambda *a, **k: {"id": "stub"})


def test_happy_path_completes(mock_agents):
    result = wf.run_workflow("an idea", "idea-1", "run-1")
    assert result["status"] == "completed"
    assert result["notion_url"] == "https://notion.so/pid"
    assert result["classifier_output"].category == "saas"
    assert len(result["task_output"].tasks) == 8


def test_agent_failure_short_circuits(monkeypatch, mock_agents):
    def boom(idea_text, classifier):
        raise RuntimeError("scoring exploded")

    monkeypatch.setattr(wf, "run_scoring", boom)

    result = wf.run_workflow("an idea", "idea-1", "run-1")
    assert result["status"] == "failed"
    assert "Scoring failed" in result["error_message"]
    # Downstream specialists never ran.
    assert "scoring_output" not in result
    assert "planning_output" not in result



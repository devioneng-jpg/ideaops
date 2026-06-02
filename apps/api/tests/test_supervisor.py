"""The supervisor is a pure routing function — easy to exercise exhaustively."""

from app.services.workflow import supervisor

_SENTINEL = object()


def test_routes_through_specialists_in_order():
    state: dict = {}
    assert supervisor(state)["next"] == "classify"

    state["classifier_output"] = _SENTINEL
    assert supervisor(state)["next"] == "score"

    state["scoring_output"] = _SENTINEL
    assert supervisor(state)["next"] == "plan"

    state["planning_output"] = _SENTINEL
    assert supervisor(state)["next"] == "break_down_tasks"

    state["task_output"] = _SENTINEL
    assert supervisor(state)["next"] == "publish_notion"

    # Notion succeeded → page id present → finalize.
    state["notion_page_id"] = "pid"
    assert supervisor(state)["next"] == "finalize"


def test_failure_short_circuits_to_finalize():
    state = {"classifier_output": _SENTINEL, "status": "failed"}
    assert supervisor(state)["next"] == "finalize"


def test_partial_success_finalizes_without_notion_page():
    # Notion failed (no page id) but status is partial_success → don't retry, finalize.
    state = {
        "classifier_output": _SENTINEL,
        "scoring_output": _SENTINEL,
        "planning_output": _SENTINEL,
        "task_output": _SENTINEL,
        "status": "partial_success",
    }
    assert supervisor(state)["next"] == "finalize"

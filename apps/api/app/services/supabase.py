import uuid
from typing import Any, Optional

from supabase import create_client, Client

from app.config import settings
from app.models.agent_outputs import TaskBreakdownOutput


def get_client() -> Client:
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


# ── Idea Submissions ─────────────────────────────────────────────────────────

def create_idea(raw_text: str, source: str, user_phone: Optional[str] = None) -> dict:
    client = get_client()
    row = {
        "raw_text": raw_text,
        "source": source,
        "status": "processing",
    }
    if user_phone:
        row["user_phone"] = user_phone

    result = client.table("idea_submissions").insert(row).execute()
    return result.data[0]


def update_idea_status(idea_id: str, status: str, latest_run_id: Optional[str] = None) -> None:
    client = get_client()
    update: dict[str, Any] = {"status": status}
    if latest_run_id:
        update["latest_run_id"] = latest_run_id
    client.table("idea_submissions").update(update).eq("id", idea_id).execute()


def get_idea(idea_id: str) -> Optional[dict]:
    client = get_client()
    result = client.table("idea_submissions").select("*").eq("id", idea_id).execute()
    return result.data[0] if result.data else None


# ── Workflow Runs ─────────────────────────────────────────────────────────────

def create_run(idea_id: str) -> dict:
    client = get_client()
    row = {
        "idea_id": idea_id,
        "status": "running",
    }
    result = client.table("workflow_runs").insert(row).execute()
    return result.data[0]


def update_run(run_id: str, **fields: Any) -> None:
    client = get_client()
    client.table("workflow_runs").update(fields).eq("id", run_id).execute()


def get_run(run_id: str) -> Optional[dict]:
    client = get_client()
    result = client.table("workflow_runs").select("*").eq("id", run_id).execute()
    return result.data[0] if result.data else None


def get_runs_for_idea(idea_id: str) -> list[dict]:
    client = get_client()
    result = (
        client.table("workflow_runs")
        .select("*")
        .eq("idea_id", idea_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


# ── Generated Tasks ───────────────────────────────────────────────────────────

def save_tasks(run_id: str, task_output: TaskBreakdownOutput) -> list[dict]:
    client = get_client()
    rows = [
        {
            "run_id": run_id,
            "title": t.title,
            "description": t.description,
            "priority": t.priority,
            "order_index": t.order_index,
            "estimated_hours": t.estimated_hours,
        }
        for t in task_output.tasks
    ]
    result = client.table("generated_tasks").insert(rows).execute()
    return result.data


def get_tasks_for_run(run_id: str) -> list[dict]:
    client = get_client()
    result = (
        client.table("generated_tasks")
        .select("*")
        .eq("run_id", run_id)
        .order("order_index")
        .execute()
    )
    return result.data


# ── Agent Step Logs ───────────────────────────────────────────────────────────

def get_steps_for_run(run_id: str) -> list[dict]:
    client = get_client()
    result = (
        client.table("agent_step_logs")
        .select("*")
        .eq("run_id", run_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


def log_step(
    run_id: str,
    step_name: str,
    status: str,
    input_json: Optional[dict] = None,
    output_json: Optional[dict] = None,
    error_message: Optional[str] = None,
) -> dict:
    client = get_client()
    row = {
        "run_id": run_id,
        "step_name": step_name,
        "status": status,
    }
    if input_json is not None:
        row["input_json"] = input_json
    if output_json is not None:
        row["output_json"] = output_json
    if error_message is not None:
        row["error_message"] = error_message

    result = client.table("agent_step_logs").insert(row).execute()
    return result.data[0]

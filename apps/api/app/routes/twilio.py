import logging
from xml.sax.saxutils import escape

from fastapi import APIRouter, BackgroundTasks, Form, Response

from app.services import supabase as db
from app.services.workflow import run_workflow
from app.services.twilio import send_sms, format_result_sms

logger = logging.getLogger(__name__)

router = APIRouter()


def _twiml(message: str) -> Response:
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f"<Response><Message>{escape(message)}</Message></Response>"
    )
    return Response(content=body, media_type="application/xml")


def process_and_notify(idea_text: str, idea_id: str, run_id: str, to_phone: str) -> None:
    """Run the pipeline and text the result back to the sender.

    Runs in a background task so the inbound webhook can ack within Twilio's
    timeout. Outbound SMS failures are logged, not raised.
    """
    result = run_workflow(idea_text=idea_text, idea_id=idea_id, run_id=run_id)
    status = result.get("status", "failed")

    if status == "failed":
        reply_body = "Sorry, something went wrong processing your idea. Please try again."
    else:
        planning = result.get("planning_output")
        classifier = result.get("classifier_output")
        scoring = result.get("scoring_output")
        reply_body = format_result_sms(
            summary=planning.one_sentence_summary if planning else None,
            category=classifier.category if classifier else None,
            total_score=scoring.total_score if scoring else None,
            notion_url=result.get("notion_url"),
        )

    try:
        send_sms(to=to_phone, body=reply_body)
    except Exception:
        logger.exception("Failed to send result SMS to %s", to_phone)


@router.post("/api/twilio/inbound")
def twilio_inbound(
    background_tasks: BackgroundTasks,
    Body: str = Form(...),
    From: str = Form(...),
):
    """Twilio SMS webhook — acks immediately, then texts the brief when ready."""
    idea_text = Body.strip()

    if len(idea_text) < 10:
        return _twiml("Please send a longer idea description (at least 10 characters).")

    # Create records, then run the pipeline in the background.
    idea = db.create_idea(raw_text=idea_text, source="sms", user_phone=From)
    run = db.create_run(idea["id"])
    background_tasks.add_task(
        process_and_notify,
        idea_text=idea_text,
        idea_id=idea["id"],
        run_id=run["id"],
        to_phone=From,
    )

    return _twiml("Got it — I'm turning that idea into a plan now. I'll text you the brief shortly.")

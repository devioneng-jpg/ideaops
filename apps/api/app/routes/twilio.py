import logging
from xml.sax.saxutils import escape

from fastapi import APIRouter, Form, Response

from app.models.requests import IdeaSubmissionRequest
from app.services import supabase as db
from app.services.workflow import run_workflow
from app.services.twilio import send_sms, format_result_sms

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/api/twilio/inbound")
def twilio_inbound(Body: str = Form(...), From: str = Form(...)):
    """Twilio SMS webhook — receives an idea via SMS, processes it, replies."""
    idea_text = Body.strip()

    if len(idea_text) < 10:
        twiml = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            "<Response><Message>Please send a longer idea description (at least 10 characters).</Message></Response>"
        )
        return Response(content=twiml, media_type="application/xml")

    # 1. Create records
    idea = db.create_idea(raw_text=idea_text, source="sms", user_phone=From)
    idea_id = idea["id"]
    run = db.create_run(idea_id)
    run_id = run["id"]

    # 2. Run pipeline
    result = run_workflow(idea_text=idea_text, idea_id=idea_id, run_id=run_id)

    # 3. Build SMS reply
    status = result.get("status", "failed")
    summary = None
    category = None
    total_score = None
    notion_url = result.get("notion_url")

    planning = result.get("planning_output")
    if planning:
        summary = planning.one_sentence_summary

    classifier = result.get("classifier_output")
    if classifier:
        category = classifier.category

    scoring = result.get("scoring_output")
    if scoring:
        total_score = scoring.total_score

    if status == "failed":
        reply_body = "Sorry, something went wrong processing your idea. Please try again."
    else:
        reply_body = format_result_sms(summary, category, total_score, notion_url)

    # Respond with TwiML (escape the model-generated body so it can't break the XML)
    twiml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f"<Response><Message>{escape(reply_body)}</Message></Response>"
    )
    return Response(content=twiml, media_type="application/xml")

from twilio.rest import Client as TwilioClient

from app.config import settings


def get_client() -> TwilioClient:
    return TwilioClient(settings.twilio_account_sid, settings.twilio_auth_token)


def send_sms(to: str, body: str) -> str:
    """Send an SMS and return the message SID."""
    client = get_client()
    message = client.messages.create(
        body=body[:1600],  # SMS limit
        from_=settings.twilio_phone_number,
        to=to,
    )
    return message.sid


def format_result_sms(
    summary: str | None,
    category: str | None,
    total_score: float | None,
    notion_url: str | None,
) -> str:
    """Format a workflow result into a concise SMS body."""
    parts = ["IdeaOps Result:"]
    if summary:
        parts.append(f"\n{summary}")
    if category:
        parts.append(f"\nCategory: {category}")
    if total_score is not None:
        parts.append(f"\nScore: {total_score}/10")
    if notion_url:
        parts.append(f"\nFull brief: {notion_url}")
    return "".join(parts)

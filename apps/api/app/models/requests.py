from typing import Literal, Optional

from pydantic import BaseModel, Field


class IdeaSubmissionRequest(BaseModel):
    idea_text: str = Field(..., min_length=10, max_length=5000, description="The raw idea text")
    source: Literal["web", "sms"] = "web"
    user_phone: Optional[str] = None

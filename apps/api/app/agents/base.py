"""Shared helpers for the specialist agents.

Each agent is a pure function: typed input -> typed output. They all route their
LLM call through `call_structured`, which centralizes retry handling and clean
failure logging (v1 LLM implementation requirements). No autonomous loops — a
"retry" here only re-issues the same single prompt on a transient or parse error.
"""

import json
import logging
import re
from typing import Type, TypeVar

from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, ValidationError

from app.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def get_llm(max_tokens: int = 1024) -> ChatAnthropic:
    """Construct the shared Anthropic chat model with the configured settings."""
    return ChatAnthropic(
        model=settings.llm_model,
        api_key=settings.anthropic_api_key,
        temperature=settings.llm_temperature,
        max_tokens=max_tokens,
    )


def _extract_text(content: object) -> str:
    """Pull the raw text out of an Anthropic response content field."""
    if isinstance(content, list):
        text = content[0].get("text", "") if content else ""
    elif isinstance(content, str):
        text = content
    else:
        text = str(content)
    return _extract_json(text)


def _extract_json(text: str) -> str:
    """Strip markdown fences and surrounding prose to isolate the JSON object."""
    # Try to pull JSON from ```json ... ``` or ``` ... ``` blocks first.
    match = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Otherwise find the first { ... } span (greedy on the closing brace).
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0).strip()

    # Last resort — return as-is and let json.loads raise.
    return text.strip()


def call_structured(
    llm: ChatAnthropic,
    prompt: str,
    output_model: Type[T],
    *,
    retries: int = 2,
) -> T:
    """Invoke the LLM and parse its JSON reply into `output_model`.

    Retries on transient API errors and on malformed/invalid JSON, then re-raises
    the last error if every attempt fails so the workflow node can mark the step
    failed and persist the message.
    """
    last_error: Exception | None = None
    for attempt in range(1, retries + 2):
        try:
            response = llm.invoke(prompt)
            text = _extract_text(response.content)
            return output_model(**json.loads(text))
        except (json.JSONDecodeError, ValidationError) as e:
            last_error = e
            logger.warning(
                "Attempt %d/%d: invalid %s output: %s",
                attempt, retries + 1, output_model.__name__, e,
            )
        except Exception as e:  # transient API / network errors
            last_error = e
            logger.warning(
                "Attempt %d/%d: LLM call for %s failed: %s",
                attempt, retries + 1, output_model.__name__, e,
            )

    assert last_error is not None
    raise last_error

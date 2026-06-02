"""Retry/parse behavior of the shared agent runtime."""

import json

import pytest

from app.agents.base import call_structured
from app.models.agent_outputs import ClassifierOutput

VALID_JSON = json.dumps(
    {
        "category": "saas",
        "audience": "solo builders",
        "problem_statement": "Turning raw ideas into briefs is slow.",
        "effort_level": "medium",
        "urgency": "low",
        "confidence": 0.8,
    }
)


class _Resp:
    def __init__(self, content: str):
        self.content = content


class _ScriptedLLM:
    """Replays a list of behaviors: an Exception is raised, a str is returned."""

    def __init__(self, behaviors):
        self.behaviors = list(behaviors)
        self.calls = 0

    def invoke(self, _prompt):
        behavior = self.behaviors[self.calls]
        self.calls += 1
        if isinstance(behavior, Exception):
            raise behavior
        return _Resp(behavior)


def test_succeeds_after_transient_error():
    llm = _ScriptedLLM([RuntimeError("529 overloaded"), VALID_JSON])
    out = call_structured(llm, "prompt", ClassifierOutput, retries=2)
    assert isinstance(out, ClassifierOutput)
    assert out.category == "saas"
    assert llm.calls == 2  # one retry


def test_retries_on_malformed_json():
    llm = _ScriptedLLM(["not json at all", VALID_JSON])
    out = call_structured(llm, "prompt", ClassifierOutput, retries=2)
    assert out.confidence == 0.8
    assert llm.calls == 2


def test_raises_after_exhausting_retries():
    llm = _ScriptedLLM([RuntimeError("a"), RuntimeError("b"), RuntimeError("c")])
    with pytest.raises(RuntimeError):
        call_structured(llm, "prompt", ClassifierOutput, retries=2)
    assert llm.calls == 3  # retries + 1 total attempts

"""Offline eval runner for the IdeaOps specialist agents.

Runs the four LLM agents (classify -> score -> plan -> break_down) directly
against the golden set — no Supabase, no Notion. Reports schema validity, score
distribution, task counts, and per-stage latency.

Requires a real ANTHROPIC_API_KEY (reads apps/api/.env via Settings). Run from
apps/api:

    python -m evals.run_evals

This is a manual quality tool and is intentionally NOT part of CI (CI has no keys).
"""

import statistics
import time
import traceback

from evals.golden_set import GOLDEN_IDEAS
from app.agents.classifier import run_classifier
from app.agents.scoring import run_scoring
from app.agents.planner import run_planner
from app.agents.task_breakdown import run_task_breakdown


def _check(case, classifier, scoring, tasks):
    """Return a list of human-readable failures for one idea (empty == pass)."""
    failures = []

    allowed = case.get("expect_category")
    if allowed and classifier.category not in allowed:
        failures.append(f"category {classifier.category!r} not in {allowed}")

    if not (1 <= scoring.total_score <= 10):
        failures.append(f"total_score {scoring.total_score} out of range")

    if not (8 <= len(tasks.tasks) <= 15):
        failures.append(f"task count {len(tasks.tasks)} out of range")

    return failures


def evaluate_one(case):
    timings = {}

    t = time.perf_counter()
    classifier = run_classifier(case["idea_text"])
    timings["classify"] = time.perf_counter() - t

    t = time.perf_counter()
    scoring = run_scoring(case["idea_text"], classifier)
    timings["score"] = time.perf_counter() - t

    t = time.perf_counter()
    planning = run_planner(case["idea_text"], classifier, scoring)
    timings["plan"] = time.perf_counter() - t

    t = time.perf_counter()
    tasks = run_task_breakdown(planning)
    timings["break_down"] = time.perf_counter() - t

    return {
        "category": classifier.category,
        "total_score": scoring.total_score,
        "num_tasks": len(tasks.tasks),
        "latency_s": sum(timings.values()),
        "timings": timings,
        "failures": _check(case, classifier, scoring, tasks),
    }


def main():
    rows = []
    print(f"Running {len(GOLDEN_IDEAS)} eval ideas...\n")

    for case in GOLDEN_IDEAS:
        try:
            result = evaluate_one(case)
        except Exception as e:  # a stage raised even after retries
            print(f"  ERROR  {case['id']}: {e}")
            traceback.print_exc()
            rows.append({"id": case["id"], "error": str(e)})
            continue

        status = "PASS" if not result["failures"] else "FAIL"
        print(
            f"  {status}  {case['id']:<28} "
            f"cat={result['category']:<20} "
            f"score={result['total_score']:<4} "
            f"tasks={result['num_tasks']:<3} "
            f"{result['latency_s']:.1f}s"
        )
        for f in result["failures"]:
            print(f"           - {f}")
        rows.append({"id": case["id"], **result})

    _summary(rows)


def _summary(rows):
    ok = [r for r in rows if "error" not in r]
    passed = [r for r in ok if not r["failures"]]
    scores = [r["total_score"] for r in ok]
    latencies = [r["latency_s"] for r in ok]

    print("\n── Summary ──────────────────────────────────")
    print(f"  Completed (no crash) : {len(ok)}/{len(rows)}")
    print(f"  Passed all checks    : {len(passed)}/{len(rows)}")
    if scores:
        print(
            f"  Score min/mean/max   : "
            f"{min(scores)} / {statistics.mean(scores):.1f} / {max(scores)}"
        )
    if latencies:
        print(f"  Avg latency / idea   : {statistics.mean(latencies):.1f}s")


if __name__ == "__main__":
    main()

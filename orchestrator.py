#!/usr/bin/env python3
"""AGORA CLI adapter over the shared engine and experiment registry.

Provider implementations live in ``agora.engine`` (Anthropic + OpenAI-
compatible DeepSeek). Historical helpers remain exported for calibration
scripts.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from agora.engine import DEFAULT_ROUNDS, JUDGE_PROMPT, DebateEngine, ProviderGateway, extract_json
from agora.registry import ExperimentRegistry

load_dotenv()
REPO = Path(__file__).parent
SESSIONS = REPO / "sessions"
EXPERIMENTS = REPO / "experiments"


def pick_judge() -> str:
    """Deterministically alternate providers from the durable run count."""
    existing = list(EXPERIMENTS.glob("*/AGO-EXP-*.json")) or list(SESSIONS.glob("*.json"))
    return "deepseek" if len(existing) % 2 == 0 else "anthropic"


_gateway = ProviderGateway()


def call_anthropic(model, system, user, temp, max_retries=3):
    _gateway.max_retries = max_retries
    return _gateway.anthropic(model, system, user, temp)


def call_deepseek(model, system, user, temp, max_retries=3):
    _gateway.max_retries = max_retries
    return _gateway.deepseek(model, system, user, temp)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hypothesis", required=True)
    parser.add_argument("--context", default="")
    parser.add_argument("--title", default="")
    parser.add_argument("--objective", default="")
    parser.add_argument("--supervisor", default="human-supervisor")
    parser.add_argument("--rounds", type=int, default=DEFAULT_ROUNDS)
    args = parser.parse_args()

    debate = DebateEngine(judge_selector=pick_judge).run(
        args.hypothesis, context=args.context, rounds=args.rounds
    )
    experiment = ExperimentRegistry(EXPERIMENTS).create(
        debate,
        {
            "title": args.title,
            "objective": args.objective,
            "supervisor": args.supervisor,
        },
    )

    # Compatibility projection for existing local analysis scripts. The
    # experiment record above is canonical.
    SESSIONS.mkdir(exist_ok=True)
    legacy = {
        "hypothesis": debate["hypothesis"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "models": debate["models"],
        "retries": debate["retries"],
        "transcript": debate["transcript"],
        "verdict": debate["verdict"],
        "experiment_id": experiment["id"],
    }
    legacy_payload = json.dumps(legacy, indent=2, ensure_ascii=False) + "\n"
    (SESSIONS / f"{experiment['id']}.json").write_text(legacy_payload, encoding="utf-8")

    print(json.dumps(debate["verdict"], indent=2, ensure_ascii=False))
    print(f"\nExperiment saved: {experiment['id']}")


if __name__ == "__main__":
    main()

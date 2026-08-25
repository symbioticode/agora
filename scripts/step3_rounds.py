#!/usr/bin/env python3
"""Étape 3 : borner les tours avant que reformulation, drift et coût dominent."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

try:
    from scripts.step2_direct import in_window
    from scripts.step2_stability import REPO
except ModuleNotFoundError:
    from step2_direct import in_window
    from step2_stability import REPO

load_dotenv(REPO / ".env")
HYPOTHESIS = "Le débat multi-agent améliore la factualité des LLM."
ROUNDS = (2, 3, 4, 5, 6)
MODEL_A = "claude-sonnet-4-5-20250929"
MODEL_B = "deepseek-v4-flash"
ASSESSOR = "mistral/mistral-small-latest"
ENDPOINT = "http://127.0.0.1:20128/v1/chat/completions"
CLASSES = {"NOVEL", "REFORMULATION", "DRIFT"}
RATES_USD_PER_MILLION = {
    "anthropic": {"input": 3.0, "output": 15.0},
    "deepseek": {"input": 1.0, "output": 5.0},
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def projected_call_cost(provider: str, user: str, max_tokens: int) -> float:
    """Estimate conservatively before a paid call so the cap cannot be crossed."""
    rates = RATES_USD_PER_MILLION[provider]
    estimated_input_tokens = len(user) // 3 + 500
    return (
        estimated_input_tokens * rates["input"]
        + max_tokens * rates["output"]
    ) / 1_000_000


def prepare_manifest(repo: Path = REPO) -> dict:
    return {
        "protocol": "AGORA-step3-round-bounding-v1",
        "prospective": True,
        "hypothesis": HYPOTHESIS,
        "hypothesis_sha256": digest(HYPOTHESIS.encode()),
        "rounds": list(ROUNDS),
        "one_session_per_setting": True,
        "models": {"A": MODEL_A, "B": MODEL_B, "assessor": ASSESSOR},
        "mindset_sha256": {
            "A": digest((repo / "mindsets/empiricist.md").read_bytes()),
            "B": digest((repo / "mindsets/rationalist.md").read_bytes()),
        },
        "temperature_debate": 0.7,
        "temperature_assessor": 0.0,
        "marginal_scope": "round > 0",
        "degradation_rule": {"max_drift_rate": 0.10, "min_novelty_rate": 0.25},
        "selection_rule": "setting immediately before first degradation; otherwise 6",
        "expected_sessions": len(ROUNDS),
    }


def analyze(manifest: dict, sessions: list[dict]) -> dict:
    by_rounds = {}
    for item in sessions:
        rounds = item.get("rounds")
        if rounds not in manifest["rounds"]:
            raise ValueError(f"rounds non planifié: {rounds}")
        if rounds in by_rounds:
            raise ValueError(f"session dupliquée pour rounds={rounds}")
        if item.get("hypothesis_sha256") != manifest["hypothesis_sha256"]:
            raise ValueError("hypothèse différente du manifeste")
        expected = 2 * (rounds + 1)
        turns = item.get("turn_assessments", [])
        if len(turns) != expected:
            raise ValueError(f"{expected} évaluations attendues")
        if any(turn.get("classification") not in CLASSES for turn in turns):
            raise ValueError("classification invalide")
        by_rounds[rounds] = item
    complete = len(by_rounds) == manifest["expected_sessions"]
    settings = []
    for rounds in manifest["rounds"]:
        item = by_rounds.get(rounds)
        marginal = [] if item is None else [t for t in item["turn_assessments"] if t["round"] > 0]
        counts = Counter(t["classification"] for t in marginal)
        total = len(marginal)
        novelty = counts["NOVEL"] / total if total else 0.0
        drift = counts["DRIFT"] / total if total else 0.0
        degraded = item is not None and (
            drift > manifest["degradation_rule"]["max_drift_rate"]
            or novelty < manifest["degradation_rule"]["min_novelty_rate"]
        )
        settings.append({
            "rounds": rounds, "present": item is not None,
            "novelty_rate": round(novelty, 4), "drift_rate": round(drift, 4),
            "classifications": dict(sorted(counts.items())),
            "total_tokens": 0 if item is None else sum(item["usage"].values()),
            "degraded": degraded,
        })
    first = next((s["rounds"] for s in settings if s["degraded"]), None)
    recommended = None
    if complete:
        if first is None:
            recommended = manifest["rounds"][-1]
        else:
            index = manifest["rounds"].index(first)
            recommended = manifest["rounds"][max(0, index - 1)]
    return {
        "protocol": manifest["protocol"], "complete": complete,
        "first_degraded_setting": first, "recommended_default_rounds": recommended,
        "settings": settings,
    }


def anthropic_call(system: str, user: str, max_tokens: int) -> tuple[str, dict, float]:
    from anthropic import Anthropic
    started = time.monotonic()
    response = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"]).messages.create(
        model=MODEL_A, max_tokens=max_tokens, temperature=0.7,
        system=system, messages=[{"role": "user", "content": user}],
    )
    usage = {"input": response.usage.input_tokens, "output": response.usage.output_tokens}
    return response.content[0].text, usage, time.monotonic() - started


def deepseek_call(system: str, user: str, max_tokens: int) -> tuple[str, dict, float]:
    from openai import OpenAI
    started = time.monotonic()
    response = OpenAI(base_url="https://api.deepseek.com/v1", api_key=os.environ["DEEPSEEK_API_KEY"]).chat.completions.create(
        model=MODEL_B, max_tokens=max_tokens, temperature=0.7,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        extra_body={"thinking": {"type": "disabled"}},
    )
    usage = {"input": response.usage.prompt_tokens, "output": response.usage.completion_tokens}
    return response.choices[0].message.content, usage, time.monotonic() - started


def assess(transcript: list[dict]) -> tuple[list[dict], dict]:
    prompt = (
        "Classifie chaque tour relativement à l'hypothèse originale et aux tours précédents. "
        "NOVEL ajoute un argument substantiel; REFORMULATION répète; DRIFT change de question. "
        "Réponds en JSON strict: {\"turn_assessments\":[{\"turn_index\":0,\"round\":0,"
        "\"agent\":\"A\",\"classification\":\"NOVEL\",\"reason\":\"...\"}]}.\n\n"
        f"Hypothèse: {HYPOTHESIS}\nTranscript: {json.dumps(transcript, ensure_ascii=False)}"
    )
    body = json.dumps({
        "model": ASSESSOR, "temperature": 0, "stream": False, "max_tokens": 1800,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    request = urllib.request.Request(ENDPOINT, data=body, headers={
        "Content-Type": "application/json", "x-omniroute-no-cache": "true",
        "x-omniroute-no-memory": "true",
    })
    with urllib.request.urlopen(request, timeout=180) as response:
        payload = json.load(response)
    raw = payload["choices"][0]["message"]["content"]
    start, end = raw.find("{"), raw.rfind("}") + 1
    value = json.loads(raw[start:end])
    return value["turn_assessments"], payload.get("usage", {})


def run(manifest: dict, output: Path, caps: dict[str, float], max_tokens: int) -> int:
    if not in_window(datetime.now(timezone.utc)):
        raise RuntimeError("appels refusés hors fenêtre nocturne")
    mindsets = {
        "A": (REPO / "mindsets/empiricist.md").read_text(encoding="utf-8"),
        "B": (REPO / "mindsets/rationalist.md").read_text(encoding="utf-8"),
    }
    output.mkdir(parents=True, exist_ok=True)
    spend = {"anthropic": 0.0, "deepseek": 0.0}
    for old_path in output.glob("rounds-*.json"):
        old = json.loads(old_path.read_text(encoding="utf-8"))
        for provider in spend:
            spend[provider] += old.get("estimated_cost_usd", {}).get(provider, 0.0)
    for rounds in manifest["rounds"]:
        target = output / f"rounds-{rounds}.json"
        if target.exists():
            continue
        session_start_spend = dict(spend)
        transcript, previous = [], {"A": "", "B": ""}
        usage = {"anthropic_input": 0, "anthropic_output": 0, "deepseek_input": 0, "deepseek_output": 0, "assessment_input": 0, "assessment_output": 0}
        for round_number in range(rounds + 1):
            for agent in ("A", "B"):
                if round_number == 0:
                    user = f"Hypothèse: {HYPOTHESIS}\n\nDonne ta position initiale. Sois concis."
                else:
                    other = "B" if agent == "A" else "A"
                    user = f"Hypothèse (ré-ancrée): {HYPOTHESIS}\n\nTour {round_number}. L'adversaire répond:\n{previous[other]}\n\nMaintiens, révises ou nuances."
                provider = "anthropic" if agent == "A" else "deepseek"
                projected = spend[provider] + projected_call_cost(provider, user, max_tokens)
                if projected > caps[provider]:
                    raise RuntimeError(
                        f"appel {provider} refusé avant exécution: projection "
                        f"{projected:.6f} USD > plafond {caps[provider]:.6f} USD"
                    )
                raw, tokens, latency = (anthropic_call if agent == "A" else deepseek_call)(mindsets[agent], user, max_tokens)
                rates = RATES_USD_PER_MILLION[provider]
                cost = (tokens["input"] * rates["input"] + tokens["output"] * rates["output"]) / 1_000_000
                spend[provider] += cost
                if spend[provider] > caps[provider]:
                    raise RuntimeError(f"plafond cumulatif {provider} dépassé")
                usage[f"{provider}_input"] += tokens["input"]
                usage[f"{provider}_output"] += tokens["output"]
                previous[agent] = raw
                transcript.append({"round": round_number, "agent": agent, "content": raw, "latency_s": round(latency, 3)})
        assessments, assessor_usage = assess(transcript)
        usage["assessment_input"] = assessor_usage.get("prompt_tokens", 0)
        usage["assessment_output"] = assessor_usage.get("completion_tokens", 0)
        item = {
            "rounds": rounds, "hypothesis_sha256": manifest["hypothesis_sha256"],
            "transcript": transcript, "turn_assessments": assessments, "usage": usage,
            "estimated_cost_usd": {
                provider: round(spend[provider] - session_start_spend[provider], 8)
                for provider in spend
            },
            "collected_at": datetime.now(timezone.utc).isoformat(),
        }
        text = json.dumps(item, ensure_ascii=False, indent=2) + "\n"
        target.write_text(text, encoding="utf-8")
        print(f"rounds={rounds} collecté", flush=True)
    sessions = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(output.glob("rounds-*.json"))]
    result = analyze(manifest, sessions)
    result["estimated_cumulative_spend_usd"] = spend
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    (output.parent / "analysis.json").write_text(text, encoding="utf-8")
    return 0 if result["complete"] else 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare")
    prepare.add_argument("--manifest", type=Path, default=REPO / "results/step3_rounds/manifest.json")
    execute = sub.add_parser("run")
    execute.add_argument("--manifest", type=Path, default=REPO / "results/step3_rounds/manifest.json")
    execute.add_argument("--output", type=Path, default=REPO / "results/step3_rounds/sessions")
    execute.add_argument("--anthropic-cap", type=float, required=True)
    execute.add_argument("--deepseek-cap", type=float, required=True)
    execute.add_argument("--max-tokens", type=int, default=900)
    args = parser.parse_args()
    if args.command == "prepare":
        value = prepare_manifest()
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
        args.manifest.write_text(text, encoding="utf-8")
        print(args.manifest)
        return 0
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    return run(manifest, args.output, {"anthropic": args.anthropic_cap, "deepseek": args.deepseek_cap}, args.max_tokens)


if __name__ == "__main__":
    raise SystemExit(main())

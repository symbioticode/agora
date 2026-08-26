#!/usr/bin/env python3
"""Répète prospectivement le vote collectif pour mesurer sa stabilité temporelle."""
from __future__ import annotations

import argparse
import json
import re
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

try:
    from scripts.step2_direct import call_direct, estimated_cost, in_window, usage_cost
    from scripts.step2_multijudge_confirm import JUDGES, validate
    from scripts.step2_omniroute import call_omniroute, judge_user, load_sources
    from scripts.step2_stability import REPO
except ModuleNotFoundError:
    from step2_direct import call_direct, estimated_cost, in_window, usage_cost
    from step2_multijudge_confirm import JUDGES, validate
    from step2_omniroute import call_omniroute, judge_user, load_sources
    from step2_stability import REPO

SOURCE_MANIFEST = REPO / "results/step2_multijudge_confirm/manifest.json"
DEFAULT_ROOT = REPO / "results/temporal_stability"
REPEATS = 3


def prepare_manifest(repo: Path = REPO) -> dict:
    source = json.loads((repo / SOURCE_MANIFEST.relative_to(REPO)).read_text(encoding="utf-8"))
    return {
        "protocol": "AGORA-collective-temporal-stability-v1",
        "prospective": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "temperature": 0.0,
        "repeats": REPEATS,
        "judges": JUDGES,
        "hypotheses": source["hypotheses"],
        "majority_rule": "at least two of three provider votes match per cycle",
        "temporal_pass_rule": "same collective verdict in all three cycles for each hypothesis",
        "expected_judgments": REPEATS * len(JUDGES) * len(source["hypotheses"]),
    }


def analyze(manifest: dict, judgments: list[dict]) -> dict:
    grouped = defaultdict(list)
    seen = set()
    for item in judgments:
        validate(item, manifest)
        repeat = int(item["repeat"])
        if not 1 <= repeat <= manifest["repeats"]:
            raise ValueError("répétition non planifiée")
        key = (item["hypothesis_id"], repeat, item["judge"])
        if key in seen:
            raise ValueError("jugement dupliqué")
        seen.add(key)
        grouped[(item["hypothesis_id"], repeat)].append(item)
    hypotheses = []
    for hypothesis_id in manifest["hypotheses"]:
        cycles = []
        for repeat in range(1, manifest["repeats"] + 1):
            items = grouped[(hypothesis_id, repeat)]
            counts = Counter(item["verdict"] for item in items)
            best = max(counts.values()) if counts else 0
            modes = [value for value, count in counts.items() if count == best]
            verdict = modes[0] if len(items) == len(manifest["judges"]) and best >= 2 and len(modes) == 1 else "PENDING"
            cycles.append({"repeat": repeat, "collective_verdict": verdict,
                           "votes": {item["judge"]: item["verdict"] for item in items}})
        verdicts = [item["collective_verdict"] for item in cycles]
        stable = len(set(verdicts)) == 1 and len(verdicts) == manifest["repeats"]
        hypotheses.append({"hypothesis_id": hypothesis_id, "cycles": cycles,
                           "temporal_agreement": sum(v == verdicts[0] for v in verdicts) / len(verdicts),
                           "stable": stable})
    complete = len(judgments) == manifest["expected_judgments"]
    return {"protocol": manifest["protocol"], "complete": complete,
            "criterion_passed": complete and all(item["stable"] for item in hypotheses),
            "hypotheses": hypotheses}


def execute(manifest: dict, root: Path, caps: dict[str, float], max_tokens: int, allow_outside_window: bool = False) -> int:
    if not allow_outside_window and not in_window(datetime.now(timezone.utc)):
        raise RuntimeError("appels refusés hors fenêtre 00:00–04:00 America/Toronto")
    sources = load_sources(manifest)
    output = root / "judgments"
    output.mkdir(parents=True, exist_ok=True)
    spend = {"anthropic": 0.0, "deepseek": 0.0, "mistral": 0.0}
    for repeat in range(1, manifest["repeats"] + 1):
        for hypothesis_id, source in sources.items():
            user = judge_user(source["hypothesis"], source["transcript"])
            for judge, metadata in manifest["judges"].items():
                slug = re.sub(r"[^a-z0-9]+", "-", judge.lower()).strip("-")
                target = output / f"{hypothesis_id.lower()}-r{repeat:02d}-{slug}.json"
                if target.exists():
                    old = json.loads(target.read_text(encoding="utf-8"))
                    spend[metadata["provider"]] += old.get("estimated_cost_usd", 0.0)
                    continue
                provider = metadata["provider"]
                if metadata["transport"] == "direct":
                    projection = estimated_cost(provider, len(user) // 3 + 1000, max_tokens)
                    if spend[provider] + projection > caps[provider]:
                        raise RuntimeError(f"budget {provider} refusé avant appel")
                    raw, usage, latency = call_direct(judge, user, max_tokens)
                    from orchestrator import extract_json
                    verdict, cost = extract_json(raw), usage_cost(provider, usage)
                else:
                    verdict, raw, latency, payload = call_omniroute(judge, user)
                    usage, cost = payload.get("usage", {}), 0.0
                spend[provider] += cost
                item = {"hypothesis_id": hypothesis_id, "repeat": repeat, "judge": judge,
                        "transcript_sha256": manifest["hypotheses"][hypothesis_id]["transcript_sha256"],
                        "verdict": verdict["verdict"], "confidence": verdict["confidence"],
                        "agreement": verdict.get("agreement", []), "disagreement": verdict.get("disagreement", []),
                        "reasoning": verdict.get("reasoning", ""), "usage": usage,
                        "estimated_cost_usd": round(cost, 8), "latency_s": latency,
                        "collected_at": datetime.now(timezone.utc).isoformat(), "raw_response": raw}
                validate(item, manifest)
                target.write_text(json.dumps(item, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                print(f"cycle {repeat} {hypothesis_id} {judge}: {item['verdict']}", flush=True)
                time.sleep(2)
    judgments = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(output.glob("*.json"))]
    result = analyze(manifest, judgments)
    result["execution"] = {"estimated_spend_usd": spend, "caps_usd": caps}
    (root / "analysis.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if result["criterion_passed"] else 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    run = sub.add_parser("run")
    run.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    run.add_argument("--anthropic-cap", type=float, required=True)
    run.add_argument("--deepseek-cap", type=float, required=True)
    run.add_argument("--max-tokens", type=int, default=1200)
    run.add_argument("--allow-outside-window", action="store_true")
    args = parser.parse_args()
    if args.command == "prepare":
        args.root.mkdir(parents=True, exist_ok=True)
        (args.root / "manifest.json").write_text(json.dumps(prepare_manifest(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(args.root / "manifest.json")
        return 0
    manifest = json.loads((args.root / "manifest.json").read_text(encoding="utf-8"))
    return execute(manifest, args.root, {"anthropic": args.anthropic_cap, "deepseek": args.deepseek_cap}, args.max_tokens,
                   args.allow_outside_window)


if __name__ == "__main__":
    raise SystemExit(main())

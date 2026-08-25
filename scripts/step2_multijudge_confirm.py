#!/usr/bin/env python3
"""Prépare ou exécute la confirmation prospective du fallback multi-juges."""
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
    from scripts.step2_omniroute import call_omniroute, judge_user, load_sources
    from scripts.step2_stability import REPO, VALID_VERDICTS
except ModuleNotFoundError:
    from step2_direct import call_direct, estimated_cost, in_window, usage_cost
    from step2_omniroute import call_omniroute, judge_user, load_sources
    from step2_stability import REPO, VALID_VERDICTS

SOURCE_MANIFEST = REPO / "results/step2_direct/manifest.json"
DEFAULT_MANIFEST = REPO / "results/step2_multijudge_confirm/manifest.json"
DEFAULT_OUTPUT = REPO / "results/step2_multijudge_confirm/judgments"
JUDGES = {
    "anthropic:claude-sonnet-4-5-20250929": {
        "provider": "anthropic",
        "transport": "direct",
    },
    "deepseek:deepseek-v4-flash": {
        "provider": "deepseek",
        "transport": "direct",
    },
    "mistral/mistral-small-latest": {
        "provider": "mistral",
        "transport": "omniroute",
    },
}


def prepare_manifest(repo: Path = REPO) -> dict:
    source_path = repo / SOURCE_MANIFEST.relative_to(REPO)
    source = json.loads(source_path.read_text(encoding="utf-8"))
    return {
        "protocol": "AGORA-E1-step2-multijudge-confirm-v1",
        "prospective": True,
        "offline_only_until_execute": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "temperature": 0.0,
        "one_new_vote_per_provider": True,
        "judges": JUDGES,
        "hypotheses": {
            hypothesis_id: {
                "hypothesis": metadata["hypothesis"],
                "source_session": metadata["source_session"],
                "transcript_sha256": metadata["transcript_sha256"],
            }
            for hypothesis_id, metadata in source["hypotheses"].items()
        },
        "majority_rule": "at least two of three provider votes match",
        "tie_rule": "1-1-1 becomes PENDING",
        "expected_judgments": len(source["hypotheses"]) * len(JUDGES),
    }


def validate(item: dict, manifest: dict) -> None:
    required = {
        "hypothesis_id",
        "judge",
        "transcript_sha256",
        "verdict",
        "confidence",
    }
    missing = required - set(item)
    if missing:
        raise ValueError(f"jugement incomplet: {sorted(missing)}")
    hypothesis_id = item["hypothesis_id"]
    if hypothesis_id not in manifest["hypotheses"]:
        raise ValueError(f"hypothèse inconnue: {hypothesis_id}")
    if item["judge"] not in manifest["judges"]:
        raise ValueError(f"juge non planifié: {item['judge']}")
    if (
        item["transcript_sha256"]
        != manifest["hypotheses"][hypothesis_id]["transcript_sha256"]
    ):
        raise ValueError(f"{hypothesis_id}: transcription différente du manifeste")
    if item["verdict"] not in VALID_VERDICTS:
        raise ValueError(f"verdict invalide: {item['verdict']}")
    confidence = float(item["confidence"])
    if not 0.0 <= confidence <= 1.0:
        raise ValueError(f"confiance invalide: {confidence}")


def analyze(manifest: dict, judgments: list[dict]) -> dict:
    grouped = defaultdict(list)
    seen = set()
    for item in judgments:
        validate(item, manifest)
        key = (item["hypothesis_id"], item["judge"])
        if key in seen:
            raise ValueError(f"jugement dupliqué: {key}")
        seen.add(key)
        grouped[item["hypothesis_id"]].append(item)

    groups = []
    all_complete = True
    all_majority = True
    for hypothesis_id in manifest["hypotheses"]:
        items = grouped[hypothesis_id]
        complete = len(items) == len(manifest["judges"])
        all_complete &= complete
        counts = Counter(item["verdict"] for item in items)
        highest = max(counts.values()) if counts else 0
        modes = sorted(verdict for verdict, count in counts.items() if count == highest)
        majority = complete and highest >= 2 and len(modes) == 1
        all_majority &= majority
        groups.append(
            {
                "hypothesis_id": hypothesis_id,
                "complete": complete,
                "provider_votes": [
                    {
                        "provider": manifest["judges"][item["judge"]]["provider"],
                        "judge": item["judge"],
                        "verdict": item["verdict"],
                        "confidence": item["confidence"],
                    }
                    for item in sorted(items, key=lambda value: value["judge"])
                ],
                "collective_verdict": modes[0] if majority else "PENDING",
                "majority_count": highest,
                "majority": majority,
            }
        )
    return {
        "protocol": manifest["protocol"],
        "judgments_received": len(judgments),
        "judgments_expected": manifest["expected_judgments"],
        "complete": all_complete,
        "confirmation_gate_passed": all_complete and all_majority,
        "groups": groups,
    }


def load_judgments(directory: Path) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(directory.glob("*.json"))
    ]


def execute(
    manifest: dict,
    output: Path,
    caps: dict[str, float],
    max_tokens: int,
    interval: float,
) -> int:
    if not in_window(datetime.now(timezone.utc)):
        raise RuntimeError("appels refusés hors fenêtre 00:00–04:00 America/Toronto")
    sources = load_sources(manifest)
    output.mkdir(parents=True, exist_ok=True)
    spend = {"anthropic": 0.0, "deepseek": 0.0, "mistral": 0.0}
    for hypothesis_id, session in sources.items():
        user = judge_user(session["hypothesis"], session["transcript"])
        for judge, metadata in manifest["judges"].items():
            slug = re.sub(r"[^a-z0-9]+", "-", judge.lower()).strip("-")
            target = output / f"{hypothesis_id.lower()}-{slug}.json"
            if target.exists():
                previous = json.loads(target.read_text(encoding="utf-8"))
                spend[metadata["provider"]] += float(
                    previous.get("estimated_cost_usd", 0.0)
                )
                continue
            provider = metadata["provider"]
            if metadata["transport"] == "direct":
                projection = estimated_cost(provider, len(user) // 3 + 1000, max_tokens)
                if spend[provider] + projection > caps[provider]:
                    raise RuntimeError(f"budget {provider} refusé avant appel")
                raw, usage, latency = call_direct(judge, user, max_tokens)
                from orchestrator import extract_json

                verdict = extract_json(raw)
                cost = usage_cost(provider, usage)
                spend[provider] += cost
                transport_evidence = {"usage": usage, "estimated_cost_usd": cost}
            else:
                verdict, raw, latency, payload = call_omniroute(judge, user)
                transport_evidence = {
                    "usage": payload.get("usage", {}),
                    "omniroute_headers": payload.get("_omniroute_headers", {}),
                    "estimated_cost_usd": 0.0,
                }
            item = {
                "hypothesis_id": hypothesis_id,
                "judge": judge,
                "transcript_sha256": manifest["hypotheses"][hypothesis_id][
                    "transcript_sha256"
                ],
                "verdict": verdict["verdict"],
                "confidence": verdict["confidence"],
                "agreement": verdict.get("agreement", []),
                "disagreement": verdict.get("disagreement", []),
                "reasoning": verdict.get("reasoning", ""),
                "latency_s": latency,
                "collected_at": datetime.now(timezone.utc).isoformat(),
                "raw_response": raw,
                **transport_evidence,
            }
            item_text = json.dumps(item, ensure_ascii=False, indent=2) + "\n"
            target.write_text(item_text, encoding="utf-8")
            print(f"{hypothesis_id} {judge}: {item['verdict']}", flush=True)
            if interval:
                time.sleep(interval)
    result = analyze(manifest, load_judgments(output))
    result["execution"] = {
        "authorized_caps_usd": caps,
        "estimated_spend_usd": {
            provider: round(value, 8) for provider, value in spend.items()
        },
        "within_caps": all(
            spend[provider] <= caps[provider] for provider in ("anthropic", "deepseek")
        ),
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    analysis_path = output.parent / "analysis.json"
    analysis_text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    analysis_path.write_text(analysis_text, encoding="utf-8")
    print(analysis_path)
    return 0 if result["confirmation_gate_passed"] else 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare")
    prepare.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    run = sub.add_parser("run")
    run.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    run.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    run.add_argument("--anthropic-cap", type=float, required=True)
    run.add_argument("--deepseek-cap", type=float, required=True)
    run.add_argument("--max-tokens", type=int, default=1400)
    run.add_argument("--interval", type=float, default=10.0)
    args = parser.parse_args()
    if args.command == "prepare":
        manifest = prepare_manifest()
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
        args.manifest.write_text(manifest_text, encoding="utf-8")
        print(args.manifest)
        return 0
    if args.anthropic_cap <= 0 or args.deepseek_cap <= 0:
        parser.error("les plafonds Anthropic et DeepSeek doivent être positifs")
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    return execute(
        manifest,
        args.output,
        {"anthropic": args.anthropic_cap, "deepseek": args.deepseek_cap},
        args.max_tokens,
        args.interval,
    )


if __name__ == "__main__":
    raise SystemExit(main())

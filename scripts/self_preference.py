#!/usr/bin/env python3
"""Test prospectif de préférence d'étiquette des juges AGORA."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

try:
    from scripts.step2_direct import call_direct, estimated_cost, in_window, usage_cost
    from scripts.step2_multijudge_confirm import JUDGES
    from scripts.step2_omniroute import call_omniroute
    from scripts.step2_stability import REPO
except ModuleNotFoundError:
    from step2_direct import call_direct, estimated_cost, in_window, usage_cost
    from step2_multijudge_confirm import JUDGES
    from step2_omniroute import call_omniroute
    from step2_stability import REPO

SOURCE = REPO / "sessions/20260717_000603.json"
DEFAULT_ROOT = REPO / "results/self_preference"
CONDITIONS = ("truthful", "masked", "swapped")
PROMPT = """Tu évalues deux contributions sans réécrire le débat. Réponds en JSON strict:
{"score_A": 0-100, "score_B": 0-100, "winner": "A"|"B"|"TIE", "reasoning": "..."}
Les scores mesurent uniquement la qualité argumentative relativement à l'hypothèse. Ignore la réputation
du fournisseur indiqué. Un écart inférieur ou égal à 2 points doit produire TIE.
"""


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def prepare_manifest(repo: Path = REPO) -> dict:
    source = json.loads((repo / SOURCE.relative_to(REPO)).read_text(encoding="utf-8"))
    transcript = source["transcript"]
    encoded = json.dumps(transcript, ensure_ascii=False, sort_keys=True).encode()
    return {
        "protocol": "AGORA-self-preference-label-permutation-v1",
        "prospective": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_session": str(SOURCE.relative_to(REPO)),
        "hypothesis": source["hypothesis"],
        "transcript_sha256": digest(encoded),
        "content_providers": {"A": "anthropic", "B": "deepseek"},
        "conditions": list(CONDITIONS),
        "judges": JUDGES,
        "temperature": 0.0,
        "expected_judgments": len(CONDITIONS) * len(JUDGES),
        "metric": "absolute score change for identical content when provider labels are swapped",
        "pass_rule": "each paid judge label_effect <= 5 points and winner invariant across conditions",
    }


def render_user(manifest: dict, transcript: list[dict], condition: str) -> str:
    if condition == "truthful":
        labels = {"A": "Agent A [Anthropic]", "B": "Agent B [DeepSeek]"}
    elif condition == "swapped":
        labels = {"A": "Agent A [DeepSeek]", "B": "Agent B [Anthropic]"}
    elif condition == "masked":
        labels = {"A": "Agent A", "B": "Agent B"}
    else:
        raise ValueError(condition)
    lines = [f"Hypothèse: {manifest['hypothesis']}", "", "Débat:"]
    lines.extend(f"Tour {item['round']} - {labels[item['agent']]}: {item['content']}" for item in transcript)
    return "\n".join(lines)


def validate(item: dict, manifest: dict) -> None:
    if item["condition"] not in manifest["conditions"] or item["judge"] not in manifest["judges"]:
        raise ValueError("jugement non planifié")
    if item["transcript_sha256"] != manifest["transcript_sha256"]:
        raise ValueError("transcription modifiée")
    for key in ("score_A", "score_B"):
        if not 0 <= float(item[key]) <= 100:
            raise ValueError(f"{key} invalide")
    if item["winner"] not in {"A", "B", "TIE"}:
        raise ValueError("winner invalide")


def analyze(manifest: dict, judgments: list[dict]) -> dict:
    grouped = defaultdict(dict)
    for item in judgments:
        validate(item, manifest)
        if item["condition"] in grouped[item["judge"]]:
            raise ValueError("jugement dupliqué")
        grouped[item["judge"]][item["condition"]] = item
    judges = []
    for judge in manifest["judges"]:
        values = grouped[judge]
        complete = set(values) == set(manifest["conditions"])
        effect = None
        invariant = False
        if complete:
            effect = max(
                abs(float(values["truthful"][key]) - float(values["swapped"][key]))
                for key in ("score_A", "score_B")
            )
            invariant = len({values[c]["winner"] for c in manifest["conditions"]}) == 1
        provider = manifest["judges"][judge]["provider"]
        passed = complete and (provider == "mistral" or (effect <= 5 and invariant))
        judges.append({
            "judge": judge, "provider": provider, "complete": complete,
            "label_effect_points": effect, "winner_invariant": invariant,
            "scores": {c: {k: values[c][k] for k in ("score_A", "score_B", "winner")} for c in values},
            "pass": passed,
        })
    return {
        "protocol": manifest["protocol"],
        "complete": len(judgments) == manifest["expected_judgments"],
        "criterion_passed": all(item["pass"] for item in judges),
        "judges": judges,
    }


def execute(manifest: dict, root: Path, caps: dict[str, float], max_tokens: int) -> int:
    if not in_window(datetime.now(timezone.utc)):
        raise RuntimeError("appels refusés hors fenêtre 00:00–04:00 America/Toronto")
    source = json.loads((REPO / manifest["source_session"]).read_text(encoding="utf-8"))
    output = root / "judgments"
    output.mkdir(parents=True, exist_ok=True)
    spend = {"anthropic": 0.0, "deepseek": 0.0, "mistral": 0.0}
    for condition in manifest["conditions"]:
        user = render_user(manifest, source["transcript"], condition)
        for judge, metadata in manifest["judges"].items():
            slug = re.sub(r"[^a-z0-9]+", "-", judge.lower()).strip("-")
            target = output / f"{condition}-{slug}.json"
            if target.exists():
                old = json.loads(target.read_text(encoding="utf-8"))
                spend[metadata["provider"]] += old.get("estimated_cost_usd", 0.0)
                continue
            provider = metadata["provider"]
            full_user = PROMPT + "\n\n" + user
            if metadata["transport"] == "direct":
                projection = estimated_cost(provider, len(full_user) // 3 + 1000, max_tokens)
                if spend[provider] + projection > caps[provider]:
                    raise RuntimeError(f"budget {provider} refusé avant appel")
                raw, usage, latency = call_direct(judge, full_user, max_tokens)
                from orchestrator import extract_json
                result = extract_json(raw)
                cost = usage_cost(provider, usage)
            else:
                body = json.dumps({"model": judge, "temperature": 0, "stream": False, "max_tokens": max_tokens,
                                   "messages": [{"role": "system", "content": PROMPT}, {"role": "user", "content": user}]}).encode()
                request = urllib.request.Request("http://127.0.0.1:20128/v1/chat/completions", data=body,
                    headers={"Content-Type": "application/json", "x-omniroute-no-cache": "true", "x-omniroute-no-memory": "true"})
                started = time.monotonic()
                with urllib.request.urlopen(request, timeout=180) as response:
                    payload = json.load(response)
                latency = round(time.monotonic() - started, 3)
                raw = payload["choices"][0]["message"]["content"]
                from orchestrator import extract_json
                result = extract_json(raw)
                usage, cost = payload.get("usage", {}), 0.0
            spend[provider] += cost
            item = {"condition": condition, "judge": judge, "transcript_sha256": manifest["transcript_sha256"],
                    "score_A": result["score_A"], "score_B": result["score_B"], "winner": result["winner"],
                    "reasoning": result.get("reasoning", ""), "usage": usage, "estimated_cost_usd": round(cost, 8),
                    "latency_s": latency, "collected_at": datetime.now(timezone.utc).isoformat(), "raw_response": raw}
            validate(item, manifest)
            target.write_text(json.dumps(item, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"{condition} {judge}: {item['winner']} {item['score_A']}/{item['score_B']}", flush=True)
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
    run.add_argument("--max-tokens", type=int, default=700)
    args = parser.parse_args()
    if args.command == "prepare":
        args.root.mkdir(parents=True, exist_ok=True)
        (args.root / "manifest.json").write_text(json.dumps(prepare_manifest(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(args.root / "manifest.json")
        return 0
    manifest = json.loads((args.root / "manifest.json").read_text(encoding="utf-8"))
    return execute(manifest, args.root, {"anthropic": args.anthropic_cap, "deepseek": args.deepseek_cap}, args.max_tokens)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Exécute l'Étape 2 via deux modèles Omniroute explicites et gratuits."""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

try:
    from scripts.step2_stability import REPO, analyze, digest, prepare_manifest
except ModuleNotFoundError:  # exécution directe depuis scripts/
    from step2_stability import REPO, analyze, digest, prepare_manifest

if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from orchestrator import JUDGE_PROMPT, extract_json

DEFAULT_MODELS = (
    "groq/llama-3.3-70b-versatile",
    "mistral/mistral-small-latest",
)
ENDPOINT = "http://127.0.0.1:20128/v1/chat/completions"


def judge_user(hypothesis: str, transcript: list[dict]) -> str:
    transcript_text = "\n".join(
        f"Tour {turn['round']} - Agent {turn['agent']}: {turn['content']}"
        for turn in transcript
    )
    return f"Hypothèse: {hypothesis}\n\nDébat:\n{transcript_text}"


def call_omniroute(model: str, user: str, endpoint: str = ENDPOINT) -> tuple[dict, str, float, dict]:
    body = json.dumps({
        "model": model,
        "temperature": 0,
        "stream": False,
        "max_tokens": 1400,
        "messages": [
            {"role": "system", "content": JUDGE_PROMPT},
            {"role": "user", "content": user},
        ],
    }).encode()
    request = urllib.request.Request(endpoint, data=body, headers={
        "Content-Type": "application/json",
        "x-omniroute-no-cache": "true",
        "x-omniroute-no-memory": "true",
    })
    started = time.monotonic()
    with urllib.request.urlopen(request, timeout=180) as response:
        payload = json.load(response)
        payload["_omniroute_headers"] = {
            key.lower(): value for key, value in response.headers.items()
            if key.lower().startswith("x-omniroute")
        }
    latency = round(time.monotonic() - started, 3)
    raw = payload["choices"][0]["message"]["content"]
    return extract_json(raw), raw, latency, payload


def load_sources(manifest: dict) -> dict[str, dict]:
    sources = {}
    for hypothesis_id, metadata in manifest["hypotheses"].items():
        session = json.loads((REPO / metadata["source_session"]).read_text(encoding="utf-8"))
        if digest(session["transcript"]) != metadata["transcript_sha256"]:
            raise ValueError(f"{hypothesis_id}: source modifiée depuis le manifeste")
        sources[hypothesis_id] = session
    return sources


def run(
    repeats: int,
    interval: float,
    output: Path,
    endpoint: str = ENDPOINT,
    models: tuple[str, ...] = DEFAULT_MODELS,
) -> int:
    manifest = prepare_manifest(
        judges=models,
        repeats=repeats,
        protocol="AGORA-E1-step2-omniroute-v1",
    )
    output.mkdir(parents=True, exist_ok=True)
    manifest_path = output.parent / "step2_omniroute_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sources = load_sources(manifest)
    total = manifest["expected_judgments"]
    completed = len(list(output.glob("*.json")))
    errors = 0

    for repeat in range(1, repeats + 1):
        for hypothesis_id, session in sources.items():
            for model in models:
                model_slug = re.sub(r"[^a-z0-9]+", "-", model.lower()).strip("-")
                filename = f"{hypothesis_id.lower()}-{model_slug}-{repeat:02d}.json"
                target = output / filename
                if target.exists():
                    continue
                try:
                    verdict, raw, latency, payload = call_omniroute(
                        model, judge_user(session["hypothesis"], session["transcript"]), endpoint
                    )
                    item = {
                        "hypothesis_id": hypothesis_id,
                        "judge": model,
                        "repeat": repeat,
                        "transcript_sha256": manifest["hypotheses"][hypothesis_id]["transcript_sha256"],
                        "verdict": verdict["verdict"],
                        "confidence": verdict["confidence"],
                        "agreement": verdict.get("agreement", []),
                        "disagreement": verdict.get("disagreement", []),
                        "reasoning": verdict.get("reasoning", ""),
                        "requested_model": model,
                        "returned_model": payload.get("model"),
                        "usage": payload.get("usage", {}),
                        "omniroute_headers": payload.get("_omniroute_headers", {}),
                        "latency_s": latency,
                        "collected_at": datetime.now(timezone.utc).isoformat(),
                        "raw_response": raw,
                    }
                    target.write_text(json.dumps(item, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                    completed += 1
                    print(f"[{completed}/{total}] {hypothesis_id} {model} r{repeat}: "
                          f"{item['verdict']} {item['confidence']} ({latency}s)", flush=True)
                except (ValueError, KeyError, urllib.error.URLError, TimeoutError) as exc:
                    errors += 1
                    print(f"[ERREUR] {hypothesis_id} {model} r{repeat}: {exc}", flush=True)
                if completed < total and interval:
                    time.sleep(interval)

    judgments = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(output.glob("*.json"))]
    result = analyze(manifest, judgments)
    analysis_path = output.parent / "step2_omniroute_analysis.json"
    analysis_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(analysis_path)
    return 0 if not errors and len(judgments) == total else 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=10)
    parser.add_argument("--interval", type=float, default=30.0, help="secondes entre appels")
    parser.add_argument("--endpoint", default=ENDPOINT)
    parser.add_argument("--models", default=",".join(DEFAULT_MODELS), help="deux modèles séparés par une virgule")
    parser.add_argument("--output", type=Path, default=REPO / "results" / "step2_omniroute" / "judgments")
    args = parser.parse_args()
    if args.repeats < 3:
        parser.error("au moins 3 répétitions")
    models = tuple(item.strip() for item in args.models.split(",") if item.strip())
    if len(models) != 2 or len(set(models)) != 2:
        parser.error("exactement deux modèles distincts sont requis")
    return run(args.repeats, args.interval, args.output, args.endpoint, models)


if __name__ == "__main__":
    raise SystemExit(main())

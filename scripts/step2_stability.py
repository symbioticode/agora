#!/usr/bin/env python3
"""Prépare et analyse le Gate E1 sans effectuer aucun appel LLM.

Le script fige les transcriptions sources (empreinte SHA-256), génère le plan
des répétitions, puis analyse ultérieurement des jugements produits séparément.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VALID_VERDICTS = {"CONFIRMED", "NUANCED", "REJECTED", "PENDING"}
DEFAULT_SOURCES = {
    "H2": "sessions/20260716_121925.json",
    "H3": "sessions/20260717_000603.json",
}
DEFAULT_JUDGES = ("anthropic:claude-sonnet-4-5", "deepseek:deepseek-v4-flash")
REPEATS = 3
GATE_THRESHOLD = 0.80


def canonical_json(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def digest(value) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def prepare_manifest(
    repo: Path = REPO,
    judges: tuple[str, ...] = DEFAULT_JUDGES,
    repeats: int = REPEATS,
    protocol: str = "AGORA-E1-step2-v1",
) -> dict:
    hypotheses = {}
    for hypothesis_id, relative in DEFAULT_SOURCES.items():
        source = repo / relative
        data = json.loads(source.read_text(encoding="utf-8"))
        transcript = data.get("transcript")
        if not isinstance(transcript, list) or not transcript:
            raise ValueError(f"{relative}: transcript absent")
        hypotheses[hypothesis_id] = {
            "hypothesis": data["hypothesis"],
            "source_session": relative,
            "source_session_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "transcript_sha256": digest(transcript),
            "turns": len(transcript),
        }
    return {
        "protocol": protocol,
        "offline_only": True,
        "temperature": 0.0,
        "repeats_per_judge": repeats,
        "gate_threshold": GATE_THRESHOLD,
        "gate_rule": "3/3 verdicts identiques par hypothèse et par juge",
        "judges": list(judges),
        "hypotheses": hypotheses,
        "expected_judgments": len(hypotheses) * len(judges) * repeats,
    }


def validate_judgment(item: dict, manifest: dict) -> None:
    required = {"hypothesis_id", "judge", "repeat", "transcript_sha256", "verdict", "confidence"}
    missing = required - set(item)
    if missing:
        raise ValueError(f"jugement incomplet: {sorted(missing)}")
    hypothesis_id = item["hypothesis_id"]
    if hypothesis_id not in manifest["hypotheses"]:
        raise ValueError(f"hypothèse inconnue: {hypothesis_id}")
    if item["judge"] not in manifest["judges"]:
        raise ValueError(f"juge non planifié: {item['judge']}")
    if item["transcript_sha256"] != manifest["hypotheses"][hypothesis_id]["transcript_sha256"]:
        raise ValueError(f"{hypothesis_id}: transcription différente du manifeste")
    if item["verdict"] not in VALID_VERDICTS:
        raise ValueError(f"verdict invalide: {item['verdict']}")
    if item["repeat"] not in range(1, manifest["repeats_per_judge"] + 1):
        raise ValueError(f"répétition invalide: {item['repeat']}")
    confidence = float(item["confidence"])
    if not 0.0 <= confidence <= 1.0:
        raise ValueError(f"confiance invalide: {confidence}")


def analyze(manifest: dict, judgments: list[dict]) -> dict:
    grouped = defaultdict(list)
    seen = set()
    for item in judgments:
        validate_judgment(item, manifest)
        key = (item["hypothesis_id"], item["judge"], item["repeat"])
        if key in seen:
            raise ValueError(f"jugement dupliqué: {key}")
        seen.add(key)
        grouped[key[:2]].append(item)

    groups = []
    complete_and_stable = True
    for hypothesis_id in manifest["hypotheses"]:
        for judge in manifest["judges"]:
            items = grouped[(hypothesis_id, judge)]
            counts = Counter(item["verdict"] for item in items)
            modal, modal_count = counts.most_common(1)[0] if counts else (None, 0)
            agreement = modal_count / len(items) if items else 0.0
            complete = len(items) == manifest["repeats_per_judge"]
            passed = complete and agreement >= manifest["gate_threshold"]
            complete_and_stable &= passed
            groups.append({
                "hypothesis_id": hypothesis_id,
                "judge": judge,
                "runs": len(items),
                "verdicts": [item["verdict"] for item in sorted(items, key=lambda x: x["repeat"])],
                "modal_verdict": modal,
                "agreement_rate": round(agreement, 4),
                "complete": complete,
                "passed": passed,
            })
    return {
        "protocol": manifest["protocol"],
        "judgments_received": len(judgments),
        "judgments_expected": manifest["expected_judgments"],
        "gate_e1_passed": complete_and_stable,
        "groups": groups,
    }


def load_judgments(directory: Path) -> list[dict]:
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(directory.glob("*.json"))]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare", help="figer les sources et écrire le manifeste")
    prepare.add_argument("--output", type=Path, default=REPO / "results" / "step2_manifest.json")
    report = sub.add_parser("analyze", help="analyser des jugements déjà collectés")
    report.add_argument("--manifest", type=Path, default=REPO / "results" / "step2_manifest.json")
    report.add_argument("--judgments", type=Path, default=REPO / "results" / "step2_judgments")
    report.add_argument("--output", type=Path, default=REPO / "results" / "step2_analysis.json")
    args = parser.parse_args()

    if args.command == "prepare":
        manifest = prepare_manifest()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(args.output)
        return 0

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    analysis = analyze(manifest, load_judgments(args.judgments))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    return 0 if analysis["gate_e1_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Agrège hors ligne E1 en un vote égalitaire Anthropic/DeepSeek/Mistral.

Le Gate E1 direct reste inchangé et échoué. Ce fallback applique la branche
préenregistrée « vote multi-juges » en réduisant les répétitions de chaque
provider à une voix modale, puis en exigeant une majorité de deux providers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

try:
    from scripts.step2_stability import VALID_VERDICTS
except ModuleNotFoundError:
    from step2_stability import VALID_VERDICTS

REPO = Path(__file__).resolve().parents[1]
DIRECT_MANIFEST = REPO / "results/step2_direct/manifest.json"
OMNIROUTE_MANIFEST = (
    REPO / "results/step2_omniroute_long/step2_omniroute_manifest.json"
)
JUDGES = {
    "anthropic:claude-sonnet-4-5-20250929": {
        "provider": "anthropic",
        "expected_repeats": 3,
        "directory": "results/step2_direct/judgments",
    },
    "deepseek:deepseek-v4-flash": {
        "provider": "deepseek",
        "expected_repeats": 3,
        "directory": "results/step2_direct/judgments",
    },
    "mistral/mistral-small-latest": {
        "provider": "mistral",
        "expected_repeats": 10,
        "directory": "results/step2_omniroute_long/judgments",
    },
}


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare_manifest(repo: Path = REPO) -> dict:
    """Pin the already collected evidence without selecting individual runs."""
    direct_path = repo / DIRECT_MANIFEST.relative_to(REPO)
    omni_path = repo / OMNIROUTE_MANIFEST.relative_to(REPO)
    direct = json.loads(direct_path.read_text(encoding="utf-8"))
    omni = json.loads(omni_path.read_text(encoding="utf-8"))
    hypotheses = {}
    if set(direct["hypotheses"]) != set(omni["hypotheses"]):
        raise ValueError("les expériences sources ne couvrent pas les mêmes hypothèses")
    for hypothesis_id, metadata in direct["hypotheses"].items():
        other = omni["hypotheses"][hypothesis_id]
        if metadata["transcript_sha256"] != other["transcript_sha256"]:
            raise ValueError(f"{hypothesis_id}: transcriptions sources différentes")
        hypotheses[hypothesis_id] = {
            "hypothesis": metadata["hypothesis"],
            "transcript_sha256": metadata["transcript_sha256"],
        }
    return {
        "protocol": "AGORA-E1-step2-multijudge-fallback-v1",
        "offline_only": True,
        "source_gate": "E1 direct non franchi",
        "source_manifests": {
            str(direct_path.relative_to(repo)): file_sha256(direct_path),
            str(omni_path.relative_to(repo)): file_sha256(omni_path),
        },
        "provider_weight": "one modal vote per provider",
        "analysis_status": "retrospective; exact modal rule was not preregistered",
        "provider_vote_rule": (
            "modal verdict over every collected repeat; tied modes become PENDING"
        ),
        "collective_vote_rule": (
            "two matching provider votes form a majority; 1-1-1 becomes PENDING"
        ),
        "judges": JUDGES,
        "hypotheses": hypotheses,
        "expected_evidence_items": sum(
            item["expected_repeats"] for item in JUDGES.values()
        )
        * len(hypotheses),
    }


def validate_evidence(item: dict, manifest: dict) -> None:
    required = {
        "hypothesis_id",
        "judge",
        "repeat",
        "transcript_sha256",
        "verdict",
    }
    missing = required - set(item)
    if missing:
        raise ValueError(f"preuve incomplète: {sorted(missing)}")
    hypothesis_id = item["hypothesis_id"]
    judge = item["judge"]
    if hypothesis_id not in manifest["hypotheses"]:
        raise ValueError(f"hypothèse inconnue: {hypothesis_id}")
    if judge not in manifest["judges"]:
        raise ValueError(f"juge non planifié: {judge}")
    if (
        item["transcript_sha256"]
        != manifest["hypotheses"][hypothesis_id]["transcript_sha256"]
    ):
        raise ValueError(f"{hypothesis_id}: transcription différente du manifeste")
    if item["verdict"] not in VALID_VERDICTS:
        raise ValueError(f"verdict invalide: {item['verdict']}")
    expected = manifest["judges"][judge]["expected_repeats"]
    if item["repeat"] not in range(1, expected + 1):
        raise ValueError(f"répétition invalide: {item['repeat']}")


def modal_vote(verdicts: list[str]) -> tuple[str | None, int]:
    if not verdicts:
        return None, 0
    counts = Counter(verdicts)
    highest = max(counts.values())
    modes = sorted(verdict for verdict, count in counts.items() if count == highest)
    return (modes[0], highest) if len(modes) == 1 else ("PENDING", highest)


def aggregate_votes(manifest: dict, evidence: list[dict]) -> dict:
    grouped = defaultdict(list)
    seen = set()
    for item in evidence:
        validate_evidence(item, manifest)
        key = (item["hypothesis_id"], item["judge"], item["repeat"])
        if key in seen:
            raise ValueError(f"jugement dupliqué: {key}")
        seen.add(key)
        grouped[key[:2]].append(item)

    groups = []
    all_complete = True
    fallback_passed = True
    for hypothesis_id in manifest["hypotheses"]:
        provider_votes = []
        group_complete = True
        for judge, metadata in manifest["judges"].items():
            items = sorted(grouped[(hypothesis_id, judge)], key=lambda item: item["repeat"])
            expected = metadata["expected_repeats"]
            complete = len(items) == expected
            group_complete &= complete
            verdicts = [item["verdict"] for item in items]
            vote, support = modal_vote(verdicts)
            provider_votes.append(
                {
                    "provider": metadata["provider"],
                    "judge": judge,
                    "runs": len(items),
                    "expected_runs": expected,
                    "complete": complete,
                    "verdicts": verdicts,
                    "vote": vote,
                    "within_provider_agreement": round(
                        support / len(verdicts) if verdicts else 0.0, 4
                    ),
                }
            )
        all_complete &= group_complete
        votes = [item["vote"] for item in provider_votes if item["vote"] is not None]
        collective, majority_count = modal_vote(votes)
        majority = group_complete and majority_count >= 2 and collective != "PENDING"
        fallback_passed &= majority
        groups.append(
            {
                "hypothesis_id": hypothesis_id,
                "provider_votes": provider_votes,
                "collective_verdict": collective if majority else "PENDING",
                "majority_count": majority_count,
                "majority": majority,
                "complete": group_complete,
            }
        )
    return {
        "protocol": manifest["protocol"],
        "original_gate_e1_passed": False,
        "evidence_received": len(evidence),
        "evidence_expected": manifest["expected_evidence_items"],
        "complete": all_complete,
        "retrospective_supports_multijudge": all_complete and fallback_passed,
        "fallback_gate_status": "RETROSPECTIVE_NOT_PREREGISTERED",
        "groups": groups,
    }


def collect_evidence(manifest: dict, repo: Path = REPO) -> list[dict]:
    evidence = []
    for judge, metadata in manifest["judges"].items():
        directory = repo / metadata["directory"]
        for path in sorted(directory.glob("*.json")):
            item = json.loads(path.read_text(encoding="utf-8"))
            if item.get("judge") == judge:
                evidence.append(item)
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=REPO / "results/step2_multijudge/manifest.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO / "results/step2_multijudge/analysis.json",
    )
    args = parser.parse_args()
    manifest = prepare_manifest()
    evidence = collect_evidence(manifest)
    analysis = aggregate_votes(manifest, evidence)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    analysis_text = json.dumps(analysis, ensure_ascii=False, indent=2) + "\n"
    args.manifest.write_text(manifest_text, encoding="utf-8")
    args.output.write_text(analysis_text, encoding="utf-8")
    print(args.manifest)
    print(args.output)
    return 0 if analysis["retrospective_supports_multijudge"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

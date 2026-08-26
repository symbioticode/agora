#!/usr/bin/env python3
"""Recette locale consolidant les cinq critères de qualification AGORA."""
import json
from datetime import datetime, timezone
from pathlib import Path

try:
    from scripts.step2_stability import REPO
    from scripts.verdict_policy import evaluate_action
except ModuleNotFoundError:
    from step2_stability import REPO
    from verdict_policy import evaluate_action


def load(path: str, repo: Path = REPO) -> dict:
    return json.loads((repo / path).read_text(encoding="utf-8"))


def qualify(repo: Path = REPO) -> dict:
    closure = (repo / "results/20260716_etape1_cloture.md").read_text(encoding="utf-8")
    collective = load("results/step2_multijudge_confirm/analysis.json", repo)
    temporal = load("results/temporal_stability/analysis.json", repo)
    preference = load("results/self_preference/analysis.json", repo)
    replacement_path = repo / "results/self_preference/replacement-result.json"
    replacement = json.loads(replacement_path.read_text(encoding="utf-8")) if replacement_path.exists() else None
    groups = {item["hypothesis_id"]: item for item in collective["groups"]}
    criteria = [
        {"id": 1, "name": "Ne pas converger artificiellement",
         "passed": "Convergence < 2 tours : 0/5 = 0%" in closure and closure.count("Désaccord persistant : 5/5 = 100%") >= 2,
         "evidence": "results/20260716_etape1_cloture.md (H2 et H4)"},
        {"id": 2, "name": "Reconnaître un fait solide",
         "passed": groups["H2"]["collective_verdict"] == "CONFIRMED" and groups["H2"]["majority_count"] == 3,
         "evidence": "results/step2_multijudge_confirm/analysis.json"},
        {"id": 3, "name": "Conserver l'incertitude sans autoriser une action faible",
         "passed": groups["H3"]["collective_verdict"] == "NUANCED"
                   and evaluate_action("NUANCED", action_attached=False)["allowed"]
                   and not evaluate_action("NUANCED", action_attached=True)["allowed"]
                   and not evaluate_action("PENDING", action_attached=True, human_approved=True)["allowed"],
         "evidence": "results/step2_multijudge_confirm/analysis.json + scripts/verdict_policy.py"},
        {"id": 4, "name": "Juge collectif stable dans le temps",
         "passed": temporal["complete"] and temporal["criterion_passed"],
         "evidence": "results/temporal_stability/analysis.json"},
        {"id": 5, "name": "Absence d'auto-préférence détectable dans le test contrôlé",
         "passed": preference["complete"] and preference["criterion_passed"],
         "evidence": "results/self_preference/analysis.json"},
    ]
    result = {"protocol": "AGORA-final-qualification-v1", "generated_at": datetime.now(timezone.utc).isoformat(),
            "all_five_simultaneously_satisfied": all(item["passed"] for item in criteria),
            "qualification": "SUPERVISED_RESEARCH_INSTRUMENT" if all(item["passed"] for item in criteria) else "LAB_ONLY",
            "criteria": criteria,
            "limits": ["Le test d'auto-préférence porte sur une transcription contrôlée, pas sur tous les sujets.",
                       "La stabilité temporelle porte sur trois cycles H2/H3 à température 0.",
                       "Aucun verdict n'autorise seul une action opérationnelle."]}
    if replacement:
        valid_cost = float(preference["execution"]["estimated_spend_usd"]["anthropic"])
        invalid_cost = float(replacement["invalidated"]["estimated_cost_usd"])
        result["evidence_corrections"] = [{
            "status": replacement["status"],
            "manifest": "results/self_preference/replacement-manifest.json",
            "result": "results/self_preference/replacement-result.json",
            "invalidated_artifact": replacement["invalidated"]["path"],
            "invalidated_sha256": replacement["invalidated"]["sha256"],
            "replacement_artifact": replacement["replacement"]["path"],
            "replacement_sha256": replacement["replacement"]["sha256"],
            "scores_reproduced": replacement["comparison"]["scores_reproduced"],
            "winner_reproduced": replacement["comparison"]["winner_reproduced"],
            "recorded_cost_usd": {
                "valid_anthropic_judgments": round(valid_cost, 8),
                "invalidated_anthropic_judgment": round(invalid_cost, 8),
                "combined": round(valid_cost + invalid_cost, 8),
            },
            "unmeasured_events": [
                "One earlier DeepSeek schema-mismatch call produced no usage artifact."
            ],
        }]
    return result


def main() -> int:
    result = qualify()
    target = REPO / "results/final_qualification.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(target)
    return 0 if result["all_five_simultaneously_satisfied"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

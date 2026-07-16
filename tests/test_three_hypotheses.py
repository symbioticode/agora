#!/usr/bin/env python3
"""Tests d'intégration — 3 hypothèses de calibration (Étape 1).
Exécuter avec --run-api pour tests API réels (coût tokens)."""
import pytest, os, json, subprocess, sys
from pathlib import Path

REPO = Path(__file__).parent.parent

HYPOTHESES = [
    ("factuelle", "L'eau pure bout à 100°C à pression standard."),
    ("nuancee", "Le débat multi-agent améliore la factualité des LLM."),
    ("ouverte", "Un système d'IA peut détenir de véritables croyances."),
]

RUN_API = os.getenv("RUN_API") == "1"


@pytest.mark.skipif(not RUN_API, reason="Nécessite RUN_API=1 (coût tokens)")
class TestThreeHypotheses:
    def run_debate(self, hypothesis, rounds=3):
        result = subprocess.run(
            [sys.executable, "orchestrator.py", "--hypothesis", hypothesis, "--rounds", str(rounds)],
            cwd=REPO, capture_output=True, text=True, timeout=120
        )
        assert result.returncode == 0, f"Échec: {result.stderr}"
        # Dernière ligne JSON = verdict
        verdict_line = result.stdout.strip().split('\n')[-1]
        return json.loads(verdict_line)

    def test_factuelle_confirmed(self):
        v = self.run_debate(HYPOTHESES[0][1])
        assert v["verdict"] == "CONFIRMED", f"Attendu CONFIRMED, eu {v['verdict']}"
        assert v["confidence"] >= 0.85, f"Confiance trop faible: {v['confidence']}"
        assert not v["disagreement"], f"Désaccord non attendu: {v['disagreement']}"

    def test_nuancee_nuanced(self):
        v = self.run_debate(HYPOTHESES[1][1])
        assert v["verdict"] in ("NUANCED", "PENDING"), f"Attendu NUANCED/PENDING, eu {v['verdict']}"
        assert 0.55 <= v["confidence"] <= 0.75, f"Confiance hors plage: {v['confidence']}"

    def test_ouverte_pending(self):
        v = self.run_debate(HYPOTHESES[2][1])
        assert v["verdict"] == "PENDING", f"Attendu PENDING, eu {v['verdict']}"


def test_session_saved():
    """Vérifie qu'une session JSON a été créée."""
    sessions = list((REPO / "sessions").glob("*.json"))
    assert len(sessions) > 0, "Aucune session sauvegardée"


def test_session_format():
    """Vérifie le format JSON des sessions."""
    sessions = list((REPO / "sessions").glob("*.json"))
    for s in sessions:
        d = json.loads(s.read_text(encoding="utf-8"))
        required = {"hypothesis", "timestamp", "models", "transcript", "verdict"}
        assert required.issubset(d.keys()), f"{s.name}: champs manquants {required - set(d.keys())}"
        assert d["verdict"]["verdict"] in {"CONFIRMED", "NUANCED", "REJECTED", "PENDING"}


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
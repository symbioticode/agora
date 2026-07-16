#!/usr/bin/env python3
"""
test_orchestrator.py — Tests unitaires structurels (sans API)
"""
import sys, json, subprocess
from pathlib import Path

REPO = Path(__file__).parent.parent


def test_orchestrator_exists():
    assert (REPO / "orchestrator.py").exists(), "orchestrator.py manquant"


def test_orchestrator_imports():
    content = (REPO / "orchestrator.py").read_text(encoding="utf-8")
    assert "anthropic" in content, "import anthropic manquant"
    assert "openai" in content, "import openai manquant"
    assert "dotenv" in content, "import dotenv manquant"


def test_orchestrator_structure():
    content = (REPO / "orchestrator.py").read_text(encoding="utf-8")
    assert "def main()" in content, "fonction main manquante"
    assert "argparse" in content, "argparse manquant"
    assert "--hypothesis" in content, "argument --hypothesis manquant"
    assert "--rounds" in content, "argument --rounds manquant"
    assert "DEFAULT_ROUNDS" in content, "DEFAULT_ROUNDS manquant"
    assert "verdict" in content.lower(), "champ verdict manquant"


def test_orchestrator_runs_help():
    result = subprocess.run(
        [sys.executable, "orchestrator.py", "--help"],
        cwd=REPO, capture_output=True, text=True
    )
    assert result.returncode == 0, f"orchestrator --help failed: {result.stderr}"
    assert "hypothesis" in result.stdout


def test_mindsets_exist():
    assert (REPO / "mindsets" / "empiricist.md").exists(), "empiricist.md manquant"
    assert (REPO / "mindsets" / "rationalist.md").exists(), "rationalist.md manquant"


def test_mindsets_substantial():
    emp = (REPO / "mindsets" / "empiricist.md").read_text(encoding="utf-8")
    rat = (REPO / "mindsets" / "rationalist.md").read_text(encoding="utf-8")
    assert len(emp.split()) >= 50, "empiricist.md trop court"
    assert len(rat.split()) >= 50, "rationalist.md trop court"


def test_mindsets_distinct():
    emp = set((REPO / "mindsets" / "empiricist.md").read_text(encoding="utf-8").lower().split())
    rat = set((REPO / "mindsets" / "rationalist.md").read_text(encoding="utf-8").lower().split())
    jaccard = len(emp & rat) / len(emp | rat)
    assert jaccard < 0.70, f"Mindsets trop similaires (Jaccard={jaccard:.2f})"


def test_scripts_exist():
    assert (REPO / "scripts" / "lab_status.sh").exists(), "lab_status.sh manquant"
    assert (REPO / "scripts" / "lab_check.py").exists(), "lab_check.py manquant"


def test_requirements():
    content = (REPO / "requirements.txt").read_text(encoding="utf-8")
    assert "anthropic" in content
    assert "openai" in content


def test_env_example():
    assert (REPO / ".env.example").exists(), ".env.example manquant"


def test_gitignore():
    gi = (REPO / ".gitignore").read_text(encoding="utf-8")
    assert ".env" in gi, ".env non gitignored"


def test_directories():
    assert (REPO / "sessions").exists(), "sessions/ manquant"
    assert (REPO / "results").exists(), "results/ manquant"


if __name__ == "__main__":
    test_orchestrator_exists()
    test_orchestrator_imports()
    test_orchestrator_structure()
    test_orchestrator_runs_help()
    test_mindsets_exist()
    test_mindsets_substantial()
    test_mindsets_distinct()
    test_scripts_exist()
    test_requirements()
    test_env_example()
    test_gitignore()
    test_directories()
    print("All tests passed!")
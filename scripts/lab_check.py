#!/usr/bin/env python3
"""
lab_check.py — Agora / Vérification (PCA-V)
Usage : python scripts/lab_check.py [--run-api]
Exit code : 0 si tout passe, 1 sinon.
Source de référence : DECISIONS.md + Architecture section mindsets.
"""
import sys, os, json, pathlib, argparse

REPO = pathlib.Path(__file__).parent.parent
_RUN_API = False

# PCA-V1 : Registre de checks — décorateur d'enregistrement pur
CHECKS: list[tuple[str, str, object]] = []
def check(section: str, label: str):
    def decorator(fn):
        CHECKS.append((section, label, fn))
        return fn
    return decorator

# PCA-V2 : Sections nommées comme unité de reporting
section_names = {
    "A": "Invariants structurels",
    "B": "Cohérence des mindsets",
    "C": "Orchestrateur",
    "D": "Non-régression exports JSON",
    "E": "Vérifications API (opt-in --run-api)",
}

# ── Section A — Invariants structurels ──────────────────────────────────────
# PCA-V3 : ces fichiers doivent exister avant toute modification

@check("A", "README.md substantiel (>= 10 lignes)")
def _():
    f = REPO/"README.md"
    assert f.exists(), "README.md absent"
    assert len(f.read_text(encoding="utf-8").splitlines()) >= 10, "README.md trop court"

@check("A", "orchestrator.py substantiel (>= 30 lignes)")
def _():
    f = REPO/"orchestrator.py"
    assert f.exists(), "orchestrator.py absent"
    assert len(f.read_text(encoding="utf-8").splitlines()) >= 30, "orchestrator.py placeholder ?"

@check("A", "requirements.txt contient anthropic et openai")
def _():
    # PCA-V4 : empêche la régression requirements.txt vidé par merge
    f = REPO/"requirements.txt"
    assert f.exists(), "requirements.txt absent"
    c = f.read_text(encoding="utf-8")
    assert "anthropic" in c, "anthropic absent"
    assert "openai" in c, "openai absent"

@check("A", ".env.example commité")
def _():
    assert (REPO/".env.example").exists(), ".env.example absent — pas de template"

@check("A", ".env est gitignored")
def _():
    gi = REPO/".gitignore"
    if not gi.exists(): return
    assert ".env" in gi.read_text(encoding="utf-8"), ".env non gitignored — risque de commiter les clés"

@check("A", "sessions/ et results/ existent")
def _():
    assert (REPO/"sessions").exists(), "sessions/ absent"
    assert (REPO/"results").exists(), "results/ absent"

# ── Section B — Cohérence des mindsets ──────────────────────────────────────

@check("B", "empiricist.md substantiel (>= 50 mots)")
def _():
    f = REPO/"mindsets"/"empiricist.md"
    assert f.exists(), "empiricist.md absent"
    assert len(f.read_text(encoding="utf-8").split()) >= 50, "empiricist.md trop court — placeholder ?"

@check("B", "rationalist.md substantiel (>= 50 mots)")
def _():
    f = REPO/"mindsets"/"rationalist.md"
    assert f.exists(), "rationalist.md absent"
    assert len(f.read_text(encoding="utf-8").split()) >= 50, "rationalist.md trop court — placeholder ?"

@check("B", "Les deux mindsets sont distincts (Jaccard < 0.70)")
def _():
    # PCA-V4 : Jaccard > 0.70 = mindsets quasi-identiques = chambre d'écho
    # même avec deux providers différents (D-AGO-001)
    emp = set((REPO/"mindsets"/"empiricist.md").read_text(encoding="utf-8").lower().split())
    rat = set((REPO/"mindsets"/"rationalist.md").read_text(encoding="utf-8").lower().split())
    if not emp or not rat: return
    j = len(emp & rat) / len(emp | rat)
    assert j < 0.70, f"Mindsets trop similaires (Jaccard={j:.2f}) — chambre d'écho probable"

# ── Section C — Orchestrateur ────────────────────────────────────────────────

@check("C", "orchestrator.py importe anthropic et openai")
def _():
    c = (REPO/"orchestrator.py").read_text(encoding="utf-8")
    assert "anthropic" in c, "anthropic non importé"
    assert "openai" in c, "openai non importé"

@check("C", "orchestrator.py paramètre rounds configurable")
def _():
    assert "rounds" in (REPO/"orchestrator.py").read_text(encoding="utf-8").lower(), \
        "paramètre 'rounds' absent — bornage des tours non configurable"

@check("C", "orchestrator.py produit un champ verdict")
def _():
    c = (REPO/"orchestrator.py").read_text(encoding="utf-8")
    assert "verdict" in c, \
        "champ 'verdict' absent — résultat non gradué"

# ── Section D — Non-régression exports JSON ──────────────────────────────────

@check("D", "Tous les JSON dans sessions/ ont le format requis")
def _():
    required = {"hypothesis", "timestamp", "models", "transcript", "verdict"}
    bad = []
    for jf in (REPO/"sessions").glob("*.json"):
        try:
            d = json.loads(jf.read_text(encoding="utf-8"))
            miss = required - set(d.keys())
            if miss: bad.append(f"{jf.name}: manque {miss}")
        except json.JSONDecodeError as e:
            bad.append(f"{jf.name}: JSON invalide ({e})")
    assert not bad, "Sessions malformées :\n" + "\n".join(bad)

@check("D", "Verdicts dans sessions/ utilisent les valeurs autorisées")
def _():
    # PCA-V4 : Bug initial — certains tests produisaient "VALID" au lieu de
    # "CONFIRMED". Ce check empêche la réintroduction de valeurs non canoniques.
    allowed = {"CONFIRMED", "NUANCED", "REJECTED", "PENDING"}
    bad = []
    for jf in (REPO/"sessions").glob("*.json"):
        try:
            d = json.loads(jf.read_text(encoding="utf-8"))
            v = d.get("verdict", {})
            vs = v.get("verdict") if isinstance(v, dict) else str(v)
            if vs and vs not in allowed:
                bad.append(f"{jf.name}: verdict='{vs}' non autorisé")
        except Exception:
            pass
    assert not bad, "Verdicts invalides :\n" + "\n".join(bad)

@check("D", "Sessions TI-360 : juge alterne entre providers (P4 assoupli, 2 providers)")
def _():
    # TI-360 P4 : vérification indépendante de la source.
    # Contrainte : 2 providers seulement (Anthropic + DeepSeek).
    # P4 strict (juge != A != B) impossible sans 3e provider.
    # Règle assouplie (D-AGO-007) : le juge alterne entre Anthropic et DeepSeek
    # pour éviter le biais d'auto-préférence systématique sur Agent A (Claude).
    # Vérifie qu'il n'y a PAS de biais systématique (tous les juges = Agent A).
    claude_as_judge = 0
    total_sessions = 0
    for jf in (REPO/"sessions").glob("*.json"):
        try:
            d = json.loads(jf.read_text(encoding="utf-8"))
            models = d.get("models", {})
            judge = models.get("judge", "")
            agent_a = models.get("A", "")
            total_sessions += 1
            if judge and judge == agent_a:
                claude_as_judge += 1
        except Exception:
            pass
    if total_sessions > 0:
        ratio = claude_as_judge / total_sessions
        # Si > 80% des sessions ont Claude comme juge = biais systématique
        assert ratio <= 0.80, (
            f"Biais juge/Agent A systématique: {claude_as_judge}/{total_sessions} "
            f"sessions ({ratio:.0%}) ont juge == Agent A (seuil max 80%)"
        )

@check("D", "Sessions TI-360 : NUANCED implique disagreement[] non vide (P3)")
def _():
    # TI-360 P3 : une contradiction détectée reste visible.
    # Un verdict NUANCED avec disagreement vide est une contradiction
    # silencieusement résolue — exactement ce que P3 interdit.
    # Référence : docs/ti360_mapping.md §Principe P3
    bad = []
    for jf in (REPO/"sessions").glob("*.json"):
        try:
            d = json.loads(jf.read_text(encoding="utf-8"))
            v = d.get("verdict", {})
            if isinstance(v, dict):
                if v.get("verdict") == "NUANCED":
                    disagreements = v.get("disagreement", [])
                    if not disagreements:
                        bad.append(
                            f"{jf.name}: NUANCED sans disagreement[] — "
                            f"TI-360 P3 violé (contradiction non documentée)"
                        )
        except Exception:
            pass
    assert not bad, "Contradictions silencieuses :\n" + "\n".join(bad)

# ── Section E — Vérifications API (opt-in) ──────────────────────────────────
# PCA-V5 : coût token réel, échouent hors réseau — jamais par défaut

@check("E", "Anthropic API ping (--run-api requis)")
def _():
    if not _RUN_API: return
    import anthropic
    key = os.getenv("ANTHROPIC_API_KEY", "")
    assert key, "ANTHROPIC_API_KEY absent"
    r = anthropic.Anthropic(api_key=key).messages.create(
        model="claude-sonnet-4-5", max_tokens=5,
        messages=[{"role":"user","content":"Reply: OK"}])
    assert r.content, "Réponse vide"

@check("E", "DeepSeek API ping (--run-api requis)")
def _():
    if not _RUN_API: return
    from openai import OpenAI
    key = os.getenv("DEEPSEEK_API_KEY", "")
    assert key, "DEEPSEEK_API_KEY absent"
    r = OpenAI(base_url="https://api.deepseek.com/v1", api_key=key).chat.completions.create(
        model="deepseek-v4-flash", max_tokens=5,
        messages=[{"role":"user","content":"Reply: OK"}])
    assert r.choices, "Réponse vide"

# ── Runner ───────────────────────────────────────────────────────────────────

def run():
    global _RUN_API
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-api", action="store_true")
    _RUN_API = parser.parse_args().run_api

    passed = failed = errors = skipped = 0
    current = None

    for section, label, fn in CHECKS:
        if section != current:
            current = section
            print(f"\n  [{section}] {section_names.get(section, section)}")

        if section == "E" and not _RUN_API:
            print(f"    [SKIP] {label}")
            skipped += 1
            continue
        try:
            fn()
            print(f"    [PASS] {label}")
            passed += 1
        except AssertionError as e:
            # PCA-V6 : assertion = invariant faux
            print(f"    [FAIL] {label}\n           → {e}")
            failed += 1
        except Exception as e:
            # PCA-V6 : exception = le test n'a pas pu tourner
            print(f"    [ERR ] {label}\n           → {type(e).__name__}: {e}")
            errors += 1

    print(f"\n  {passed} PASS / {failed} FAIL / {errors} ERR", end="")
    if skipped:
        print(f" / {skipped} SKIP (relancer avec --run-api)", end="")
    print()
    sys.exit(0 if failed == 0 and errors == 0 else 1)  # PCA-V7

if __name__ == "__main__":
    run()
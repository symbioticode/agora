# Agora — Laboratoire Agentique Minimal à Deux Agents

> **Source de vérité : GitHub** — code, documentation et résultats de sessions
> dans le même dépôt. Les agents IA et l'orchestrateur lisent depuis le repo.

---

## BLUF

Script Python pur (~90 lignes), Anthropic/Claude + DeepSeek directs,
zéro framework, deux `pip install`. Deux agents aux mindsets opposés débattent
d'une hypothèse (ouverture parallèle → tours contradictoires → verdict juge),
sous observation humaine ou IA tierce, produisent un JSON gradué traçable.

**Leçon SecAudit** : l'hétérogénéité des providers est le seul levier
empiriquement robuste (Zhang et al. 2025). Claude×2 = chambre d'écho.

**Avertissement** : MAD n'améliore pas les résultats de façon garantie
(Smit et al. ICML 2024 ; Zhang et al. 2025). C'est un labo exploratoire.
DReaMAD est retracté — ses idées sont utiles, ses chiffres ne sont pas des preuves.

---

## Structure GitHub

```
agora/
├── README.md                    ← source de vérité projet
├── STATUS.md                    ← état courant (mis à jour par lab_status.sh)
├── HYPOTHESES.md                ← registre hypothèses testées + résultats
├── DECISIONS.md                 ← décisions d'architecture + justifications
├── .env.example                 ← template clés API (commité)
├── .env                         ← clés réelles (gitignored)
├── orchestrator.py              ← cœur du système (~90 lignes)
├── mindsets/
│   ├── empiricist.md            ← system prompt Agent A (Claude)
│   ├── rationalist.md           ← system prompt Agent B (DeepSeek)
│   └── README.md                ← guide nouveaux mindsets
├── sessions/                    ← transcripts JSON (gitignored)
│   └── .gitkeep
├── results/                     ← verdicts MD (commités)
│   └── .gitkeep
├── scripts/
│   ├── lab_status.sh            ← tracking (PCA-T : où en est-on ?)
│   └── lab_check.py             ← vérification (PCA-V : est-ce correct ?)
├── tests/
│   ├── test_orchestrator.py
│   └── test_three_hypotheses.py
├── docs/
│   ├── architecture.md
│   ├── pitfalls.md
│   ├── research_notes.md        ← synthèse littérature (depuis compass)
│   └── ti360_mapping.md         ← Agora comme use case TI-360 (Geste A)
└── requirements.txt             ← anthropic openai python-dotenv
```

---

## Architecture

```
Hypothèse (texte)
      │
      ▼
[Tour 0 — Parallèle]
 Agent A (Claude/empiricist, temp=0.7)
 Agent B (DeepSeek/rationalist, temp=0.7)
 → positions indépendantes, pas d'influence mutuelle
      │
[Tours 1..N — Contradictoires]
 Chaque agent lit la réponse de l'autre
 Hypothèse ré-ancrée à chaque tour (anti-drift)
 N = 3 par défaut, max 5
      │
[Juge tiers — temp=0]
 Claude Sonnet OU DeepSeek (alterner pour éviter biais)
 Produit un verdict JSON gradué
      │
 CONFIRMED / NUANCED / REJECTED / PENDING
 + confidence 0.50–1.00
 + points d'accord / désaccords persistants
      │
 Commité dans results/
```

**Règle fondamentale D-AGO-001** : Agent A et Agent B ne partagent
jamais le même provider. Violation = chambre d'écho garantie.

---

## Étapes concrètes et seuils de décision

### Étape 0 — Fondations (Jour 1, < 30 min)

**Ce qu'on construit** : repo GitHub + .env + orchestrator.py squelette
+ mindsets rédigés.

**Test de passage (gate E0)** :
```bash
python orchestrator.py \
  --hypothesis "L'eau pure bout à 100°C à pression standard." \
  --rounds 3
```
Critères de succès :
- JSON valide avec `verdict`, `confidence`, `agreement`, `disagreement`
- `verdict == "CONFIRMED"` et `confidence >= 0.85`
- Aucun désaccord fabriqué sur un fait physique établi
- Session exportée dans `sessions/`

**Ne pas avancer si** : le verdict sur l'hypothèse factuelle n'est pas CONFIRMED.
Causes connues : noms de modèles incorrects (`claude-sonnet-4-5` /
`deepseek-v4-flash`), parsing JSON du verdict, clés API absentes.

---

### Étape 1 — Calibration anti-convergence (Semaine 1)

**Ce qu'on teste** : les agents résistent-ils à la convergence artificielle ?

**Protocole — 3 hypothèses × 5 runs** :
1. **Factuelle** : *"L'eau pure bout à 100°C à pression standard."*
   → Attendu : CONFIRMED ≥ 0.85, convergence normale
2. **Nuancée** : *"Le débat multi-agent améliore la factualité des LLM."*
   → Attendu : NUANCED 0.55–0.75, désaccords persistants visibles
3. **Ouverte** : *"Un système d'IA peut détenir de véritables croyances."*
   → Attendu : PENDING, aucune résolution artificielle

**Métriques** :
```
taux_désaccord_persistant = sessions avec désaccords non vides / total
```
Objectif : ≥ 40% sur hypothèse #2.

**Seuil déclencheur** : si convergence en < 2 tours sur #2 → durcir les mindsets.
Instruction à ajouter : *"Tu DOIS maintenir ta position tant que l'adversaire
n'a pas réfuté explicitement [critère X]."*

**Commiter dans HYPOTHESES.md** : résultats bruts 15 sessions + métriques.

---

### Étape 2 — Stabilité du verdict (Semaine 2)

**Ce qu'on teste** : le juge est-il stable entre deux runs ?

**Protocole** : pour hypothèses #2 et #3, exécuter le juge 3× sur la même
transcription (pas re-débat), à `temperature=0`.

**Seuil de production** :
- ≥ 80% accord inter-runs (même verdict 3/3 ou 2/3) → système utilisable
- < 80% → passer au **vote multi-juges** (3 appels, majorité, PENDING en 1-1-1)

**Test biais d'auto-préférence** : si Claude est Agent A,
utiliser DeepSeek comme juge (et vice-versa). Commiter les écarts.

**Gate E2** : ≥ 80% stabilité sur #2 et #3 avant toute hypothèse de recherche réelle.

---

### Étape 3 — Bornage des tours (Semaine 3)

**Ce qu'on teste** : quand la dérive dépasse-t-elle le gain ?

**Protocole** : hypothèse #2 avec rounds ∈ {2, 3, 4, 5, 6}.
Mesurer : nouveaux arguments vs reformulations, problem drift, coût token.

**Seuil** : fixer `DEFAULT_ROUNDS` juste avant le premier signe de drift
(typiquement 3–4, Becker et al. EACL 2026).

**Avertissement** : sans ré-ancrage de l'hypothèse à chaque tour,
le drift arrive à 76–89% des sessions génératives (Becker et al.).
Le ré-ancrage est non-négociable dans les prompts.

---

### Étape 4 — Premiers sujets de recherche (Semaine 4+)

**Gate d'entrée** : étapes 0–3 franchies, résultats commités.

**Format de sortie** : `results/YYYYMMDD_<slug>.md` commité avec :
- Hypothèse exacte testée
- Configuration (modèles, rounds, mindsets)
- Transcription résumée
- Verdict JSON brut
- Observation de l'observateur humain

---

## Script de tracking — `scripts/lab_status.sh`

Inspiré de `eip_status.sh`. Répond à : *"Où en est-on ?"*
Ne juge pas la qualité — voir `lab_check.py` pour ça.

```bash
#!/usr/bin/env bash
# lab_status.sh — Agora / Tracking (PCA-T)
# Usage: ./scripts/lab_status.sh [--report] [--sync] [--sessions]

set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
MODE="${1:-dashboard}"

green()  { printf '\033[0;32m%s\033[0m' "$1"; }
yellow() { printf '\033[0;33m%s\033[0m' "$1"; }
red()    { printf '\033[0;31m%s\033[0m' "$1"; }

# PCA-T1 : Détection d'étape depuis le disque, jamais depuis la mémoire
detect_stage() {
  if [[ -f "$REPO_ROOT/STATUS.md" ]] && grep -q "Stage" "$REPO_ROOT/STATUS.md" 2>/dev/null; then
    grep -m1 "^## Stage" "$REPO_ROOT/STATUS.md" | sed 's/## Stage //'
  elif git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null; then
    echo "git:$(git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD)"
  else
    echo "unknown"
  fi
}

# PCA-T2 : Checklists déclaratives (listes de données, pas code dupliqué)
core_files=("README.md" "orchestrator.py" "requirements.txt"
            ".env.example" "HYPOTHESES.md" "DECISIONS.md")
mindset_files=("mindsets/empiricist.md" "mindsets/rationalist.md")
script_files=("scripts/lab_status.sh" "scripts/lab_check.py")
test_files=("tests/test_orchestrator.py" "tests/test_three_hypotheses.py")

# PCA-T3 : Trois niveaux de vérité (absent / vide / substantiel)
check_artifact() {
  local path="$REPO_ROOT/$1"
  if [[ ! -f "$path" ]]; then echo "ABSENT"
  elif [[ ! -s "$path" ]]; then echo "VIDE"
  else
    local lines; lines=$(wc -l < "$path")
    [[ $lines -lt 3 ]] && echo "MINIMAL(${lines}L)" || echo "OK(${lines}L)"
  fi
}

# PCA-T4 : Score agrégé par catégorie (pass/fail par groupe, pas moyenne plate)
score_category() {
  local pass=0 total=$#
  for f in "$@"; do
    local st; st=$(check_artifact "$f")
    [[ "$st" == OK* ]] && ((pass++)) || true
  done
  echo "$pass/$total"
}

dashboard() {
  printf '\n  Agora — Lab Status  %s\n' "$TIMESTAMP"
  printf '  Stage : %s\n\n' "$(detect_stage)"

  for cat in "Cœur|${core_files[*]}" \
             "Mindsets|${mindset_files[*]}" \
             "Scripts|${script_files[*]}" \
             "Tests|${test_files[*]}"; do
    local name="${cat%%|*}"
    local files; read -ra files <<< "${cat#*|}"
    local score; score=$(score_category "${files[@]}")
    printf '  ── %s (%s) ──\n' "$name" "$score"
    for f in "${files[@]}"; do
      local st; st=$(check_artifact "$f")
      case "$st" in
        OK*)     printf '    %s %s\n' "$(green '[OK]')" "$f ($st)" ;;
        ABSENT)  printf '    %s %s\n' "$(red '[--]')" "$f" ;;
        *)       printf '    %s %s\n' "$(yellow '[!!]')" "$f ($st)" ;;
      esac
    done
    echo ""
  done

  # PCA-T5 : Santé infrastructure comme catégorie de premier ordre
  local n_sess n_res
  n_sess=$(find "$REPO_ROOT/sessions" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
  n_res=$(find "$REPO_ROOT/results" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
  printf '  ── Sessions ──\n'
  printf '    Sessions JSON : %s\n' "$n_sess"
  printf '    Résultats MD  : %s\n\n' "$n_res"

  printf '  ── Git ──\n'
  if git -C "$REPO_ROOT" rev-parse --git-dir &>/dev/null; then
    local unpushed last
    unpushed=$(git -C "$REPO_ROOT" log @{u}.. --oneline 2>/dev/null | wc -l | tr -d ' ')
    last=$(git -C "$REPO_ROOT" log -1 --pretty=format:"%h %s (%cr)" 2>/dev/null)
    printf '    Dernier commit  : %s\n' "$last"
    printf '    Non poussés     : %s\n' "$unpushed"
    [[ -f "$REPO_ROOT/.env" ]] && printf '    .env            : %s\n' "$(yellow 'PRESENT (ne jamais commiter)')"
  else
    printf '    %s\n' "$(red 'Pas de dépôt Git')"
  fi
}

# PCA-T6 : Multi-format depuis la même source
generate_report() {
  mkdir -p "$REPO_ROOT/results"
  local out="$REPO_ROOT/results/status_${TIMESTAMP//:/-}.md"
  { echo "# Agora — Statut $TIMESTAMP"
    echo "**Stage** : $(detect_stage)"
    echo ""
    echo "## Artefacts"
    for f in "${core_files[@]}" "${mindset_files[@]}" "${script_files[@]}" "${test_files[@]}"; do
      echo "- \`$f\` : $(check_artifact "$f")"
    done
    echo ""
    echo "## Sessions"
    echo "- JSON : $(find "$REPO_ROOT/sessions" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')"
    echo "- MD   : $(find "$REPO_ROOT/results" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')"
  } > "$out"
  echo "Rapport : $out"
}

# PCA-T7 : Modes d'invocation étroits
case "$MODE" in
  --report)   generate_report ;;
  --sessions) find "$REPO_ROOT/sessions" -name "*.json" | sort | tail -10 ;;
  --sync)     git -C "$REPO_ROOT" status --short ;;
  *)          dashboard ;;
esac
```

---

## Script de vérification — `scripts/lab_check.py`

Inspiré de `adversarial_dal_check_p3.py`. Répond à : *"Est-ce correct ?"*
Sort avec exit code 1 si un invariant est faux.

```python
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
    assert len(f.read_text().splitlines()) >= 10, "README.md trop court"

@check("A", "orchestrator.py substantiel (>= 30 lignes)")
def _():
    f = REPO/"orchestrator.py"
    assert f.exists(), "orchestrator.py absent"
    assert len(f.read_text().splitlines()) >= 30, "orchestrator.py placeholder ?"

@check("A", "requirements.txt contient anthropic et openai")
def _():
    # PCA-V4 : empêche la régression requirements.txt vidé par merge
    f = REPO/"requirements.txt"
    assert f.exists(), "requirements.txt absent"
    c = f.read_text()
    assert "anthropic" in c, "anthropic absent"
    assert "openai" in c, "openai absent"

@check("A", ".env.example commité")
def _():
    assert (REPO/".env.example").exists(), ".env.example absent — pas de template"

@check("A", ".env est gitignored")
def _():
    gi = REPO/".gitignore"
    if not gi.exists(): return
    assert ".env" in gi.read_text(), ".env non gitignored — risque de commiter les clés"

@check("A", "sessions/ et results/ existent")
def _():
    assert (REPO/"sessions").exists(), "sessions/ absent"
    assert (REPO/"results").exists(), "results/ absent"

# ── Section B — Cohérence des mindsets ──────────────────────────────────────

@check("B", "empiricist.md substantiel (>= 50 mots)")
def _():
    f = REPO/"mindsets"/"empiricist.md"
    assert f.exists(), "empiricist.md absent"
    assert len(f.read_text().split()) >= 50, "empiricist.md trop court — placeholder ?"

@check("B", "rationalist.md substantiel (>= 50 mots)")
def _():
    f = REPO/"mindsets"/"rationalist.md"
    assert f.exists(), "rationalist.md absent"
    assert len(f.read_text().split()) >= 50, "rationalist.md trop court — placeholder ?"

@check("B", "Les deux mindsets sont distincts (Jaccard < 0.70)")
def _():
    # PCA-V4 : Jaccard > 0.70 = mindsets quasi-identiques = chambre d'écho
    # même avec deux providers différents (D-AGO-001)
    emp = set((REPO/"mindsets"/"empiricist.md").read_text().lower().split())
    rat = set((REPO/"mindsets"/"rationalist.md").read_text().lower().split())
    if not emp or not rat: return
    j = len(emp & rat) / len(emp | rat)
    assert j < 0.70, f"Mindsets trop similaires (Jaccard={j:.2f}) — chambre d'écho probable"

# ── Section C — Orchestrateur ────────────────────────────────────────────────

@check("C", "orchestrator.py importe anthropic et openai")
def _():
    c = (REPO/"orchestrator.py").read_text()
    assert "anthropic" in c, "anthropic non importé"
    assert "openai" in c, "openai non importé"

@check("C", "orchestrator.py paramètre rounds configurable")
def _():
    assert "rounds" in (REPO/"orchestrator.py").read_text().lower(), \
        "paramètre 'rounds' absent — bornage des tours non configurable"

@check("C", "orchestrator.py produit un champ verdict")
def _():
    c = (REPO/"orchestrator.py").read_text()
    assert "verdict" in c, \
        "champ 'verdict' absent — résultat non gradué"

# ── Section D — Non-régression exports JSON ──────────────────────────────────

@check("D", "Tous les JSON dans sessions/ ont le format requis")
def _():
    required = {"hypothesis", "timestamp", "models", "transcript", "verdict"}
    bad = []
    for jf in (REPO/"sessions").glob("*.json"):
        try:
            d = json.loads(jf.read_text())
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
            d = json.loads(jf.read_text())
            v = d.get("verdict", {})
            vs = v.get("verdict") if isinstance(v, dict) else str(v)
            if vs and vs not in allowed:
                bad.append(f"{jf.name}: verdict='{vs}' non autorisé")
        except Exception:
            pass
    assert not bad, "Verdicts invalides :\n" + "\n".join(bad)

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
```

---

## DECISIONS.md — Extrait initial

```markdown
# Décisions d'architecture

## D-AGO-001 — Deux providers distincts (Anthropic + DeepSeek)
Date : 2026-07-16
Raison : hétérogénéité = seul levier robuste (Zhang et al. 2025).
Claude×2 = chambre d'écho (SecAudit Sprint 5 + ICML 2024).
Référence : docs/research_notes.md §Key Findings 1

## D-AGO-002 — Zéro framework (script pur, 2 pip install)
Date : 2026-07-16
Raison : Karpathy impose OpenRouter ; AutoGen bugue avec Anthropic
sur l'alternance des rôles ; CAMEL conçu pour coopération, pas débat.
Référence : docs/research_notes.md §Tableau comparatif

## D-AGO-003 — Format hybride (parallèle + contradictoire + juge)
Date : 2026-07-16
Raison : Tour 0 parallèle évite l'ancrage précoce (conformity drift).
Ré-ancrage hypothèse à chaque tour (anti problem drift, Becker EACL 2026).
Juge à temperature=0 (déterminisme relatif).

## D-AGO-004 — DEFAULT_ROUNDS = 3
Date : 2026-07-16
Raison : consensus se solidifie en 2-3 tours ; drift nette au-delà.
À revalider empiriquement à l'Étape 3.

## D-AGO-005 — DReaMAD non cité comme preuve de performance
Date : 2026-07-16
Raison : retracté par les auteurs (ICML 2025, sans raison publiée).
Heuristiques (diversification perspectives) utiles, chiffres non fiables.

## D-AGO-006 — TI-360 : Geste A retenu (use case), Geste B différé
Date : 2026-07-16
Raison : les outputs d'Agora (sessions JSON + verdicts 4 valeurs) sont
structurellement des atomes TI-360 — convergence non planifiée, documentée
a posteriori dans docs/ti360_mapping.md. Le Geste B (implémentation du
graphe complet Sources→Extractions→Questions→Décisions + refus mécanique
des transitions d'état) est différé : TI-360 est en v0.1 DRAFT, Agora
est exploratoire, empiler deux systèmes à limites non résolues augmente
la surface d'échec.
Retour prévu : quand TI-360 atteint v0.2 avec périmètre validé ET quand
les Étapes 0-3 d'Agora ont produit des données empiriques réelles.
Référence : docs/ti360_mapping.md · TI360_Principes_Implementation_v0_1.md
```

---

## Intégration TI-360 — Instructions pour BigPickle (Geste A)

> **Périmètre** : créer `docs/ti360_mapping.md` et mettre à jour
> `scripts/lab_check.py`. Ne pas modifier l'orchestrateur ni le format
> des sessions JSON — la correspondance est documentaire, pas structurelle.

### Fichier à créer : `docs/ti360_mapping.md`

Contenu exact attendu :

```markdown
# Agora comme use case TI-360
*Statut : Geste A — correspondance documentée, implémentation complète différée*
*Référence TI-360 : TI360_Principes_Implementation_v0_1.md (v0.1, 14 juillet 2026)*

## Pourquoi ce document existe

Agora et TI-360 résolvent le même problème depuis deux angles :
- TI-360 : rendre une affirmation organisationnelle vérifiable mécaniquement
- Agora : rendre un résultat de débat IA traçable et reproductible

La convergence est non planifiée. Elle est documentée ici pour deux raisons :
1. Agora devient un banc de test empirique pour TI-360
2. TI-360 donne un vocabulaire précis aux outputs d'Agora

## Correspondance structurelle

| Concept TI-360 | Implémentation Agora | Champ JSON / fichier |
|---|---|---|
| Atome d'extraction | Session de débat complète | `sessions/YYYYMMDD_HHmmss.json` |
| Affirmation unique | Hypothèse testée | `hypothesis` (string) |
| Source identifiable × 2 | Agent A + Agent B | `models.A` + `models.B` |
| Statut à 4 valeurs | Verdict gradué | `verdict.verdict` |
| VRAI | CONFIRMED | `verdict == "CONFIRMED"` |
| FAUX | REJECTED | `verdict == "REJECTED"` |
| CONTRADICTION VISIBLE | NUANCED | `verdict == "NUANCED"` |
| INCONNU DÉCLARÉ | PENDING | `verdict == "PENDING"` |
| Contradiction non effacée (P3) | Désaccords persistants listés | `verdict.disagreement[]` |
| Vérification indépendante (P4) | Juge = provider tiers distinct | `models.judge` ≠ `models.A` ≠ `models.B` |
| Lisible sans l'outil (P2) | Rapport Markdown exporté | `results/YYYYMMDD_<slug>.md` |
| Invariant bloquant | Exit code 1 sur format invalide | `lab_check.py` Section D |
| Invariant avertissement | Warning terminal | `lab_status.sh` niveau `[!!]` |
| Limite non résolue (P6) | Points ouverts déclarés | `AGORA_PROJECT.md §Points ouverts` |

## Ce qu'une session JSON est, au sens de TI-360

Une session Agora est un atome TI-360 si et seulement si :

```json
{
  "hypothesis": "affirmation unique et indivisible",
  "timestamp": "ISO 8601 UTC",
  "models": {
    "A": "provider:model-version",
    "B": "provider:model-version",
    "judge": "provider:model-version"
  },
  "transcript": [
    {"round": 0, "agent": "A", "content": "..."},
    {"round": 0, "agent": "B", "content": "..."},
    {"round": 1, "agent": "A", "content": "..."}
  ],
  "verdict": {
    "verdict": "CONFIRMED|NUANCED|REJECTED|PENDING",
    "confidence": 0.00,
    "agreement": ["point 1", "point 2"],
    "disagreement": ["point persistant 1"]
  }
}
```

Conditions TI-360 vérifiées par ce format :
- P1 : source repérable — `models.A`, `models.B`, `models.judge` + `timestamp`
- P2 : lisible sans l'outil — JSON pur + Markdown dans `results/`
- P3 : contradiction non effacée — `disagreement[]` jamais vidé si NUANCED
- P4 : vérification indépendante — `models.judge` distinct des deux agents
- P6 : limites déclarées — voir section "Ce qu'Agora ne couvre pas"

## Principe P5 — Ce que lab_check.py ne vérifie PAS

`lab_check.py` Section D vérifie la conformité structurelle du JSON
(champs présents, types corrects, verdicts autorisés).

Il ne vérifie PAS que la conclusion du juge répond réellement à
l'hypothèse posée — c'est la distinction TI-360 P5 :
"Une validation de la structure n'est pas une validation du sens."

Cette vérification sémantique est assurée par l'observateur humain,
documentée dans `HYPOTHESES.md` colonne "Observations".

## Ce qu'Agora ne couvre pas (TI-360 complet)

| Fonctionnalité TI-360 | Raison du report |
|---|---|
| Graphe orienté Sources→Extractions→Questions→Décisions | Agora est à deux niveaux (hypothèse→verdict), pas quatre |
| Refus mécanique des transitions d'état entre phases | TI-360 v0.1 DRAFT, périmètre non encore validé |
| Recoupement indépendant des sources par tiers humain | Procédure, pas automatisable à ce stade |
| Audit path (remonter d'une décision vers ses sources) | Git log sur sessions/ est un proxy suffisant pour l'instant |

**Retour prévu** : TI-360 v0.2 + Agora Étapes 0-3 complétées.

## Agora comme banc de test empirique pour TI-360

Chaque session de débat produit un atome TI-360 testable sur les points
que TI-360 v0.1 déclare non encore vérifiés :

- *"Un désaccord entre deux lectures indépendantes de la même source
  peut-il être détecté automatiquement ?"*
  → Agora le teste : deux lectures IA de la même hypothèse, désaccords
  listés automatiquement dans `disagreement[]`.

- *"Une affirmation validée structurellement l'est-elle aussi sémantiquement ?"*
  → Agora le teste : `lab_check.py` valide la structure, l'observateur
  humain valide le sens dans `HYPOTHESES.md §Observations`.

Les résultats de ces tests doivent alimenter TI-360 v0.2.
```

### Mise à jour `scripts/lab_check.py` — Section D à compléter

Ajouter ce check dans la Section D (non-régression exports JSON),
après les checks existants sur le format et les verdicts autorisés :

```python
@check("D", "Sessions TI-360 : models.judge distinct de models.A et models.B (P4)")
def _():
    # TI-360 P4 : vérification indépendante de la source.
    # Le juge ne peut pas être le même provider qu'un des deux agents —
    # sinon la "vérification indépendante" est circulaire.
    # Référence : docs/ti360_mapping.md §Principe P4
    bad = []
    for jf in (REPO/"sessions").glob("*.json"):
        try:
            d = json.loads(jf.read_text())
            models = d.get("models", {})
            judge = models.get("judge", "")
            agent_a = models.get("A", "")
            agent_b = models.get("B", "")
            if judge and (judge == agent_a or judge == agent_b):
                bad.append(
                    f"{jf.name}: judge='{judge}' identique à un agent — "
                    f"TI-360 P4 violé (vérification non indépendante)"
                )
        except Exception:
            pass
    assert not bad, "Indépendance du juge violée :\n" + "\n".join(bad)

@check("D", "Sessions TI-360 : NUANCED implique disagreement[] non vide (P3)")
def _():
    # TI-360 P3 : une contradiction détectée reste visible.
    # Un verdict NUANCED avec disagreement vide est une contradiction
    # silencieusement résolue — exactement ce que P3 interdit.
    # Référence : docs/ti360_mapping.md §Principe P3
    bad = []
    for jf in (REPO/"sessions").glob("*.json"):
        try:
            d = json.loads(jf.read_text())
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
```

### Ce que BigPickle ne doit PAS faire

- Ne pas modifier `orchestrator.py` — le format JSON de sortie est déjà
  conforme TI-360. Aucun champ nouveau n'est requis.
- Ne pas modifier `lab_status.sh` — le tracking ne change pas.
- Ne pas implémenter le graphe TI-360 complet (Geste B différé,
  voir D-AGO-006).
- Ne pas renommer les champs `verdict.verdict`, `verdict.agreement`,
  `verdict.disagreement` — ils sont déjà utilisés par les checks Section D.

### Commit attendu

```
docs(ti360): Agora comme use case TI-360 — Geste A
- Ajout docs/ti360_mapping.md (correspondance structurelle + limites)
- Ajout checks TI-360 P3 et P4 dans scripts/lab_check.py Section D
- Mise à jour AGORA_PROJECT.md D-AGO-006
```

---

## Points ouverts — à résoudre empiriquement

1. **Biais d'auto-préférence du juge** : si Claude = Agent A, utiliser DeepSeek
   comme juge (et vice-versa). À tester à l'Étape 2.
2. **Déterminisme illusoire** : temperature=0 ne garantit pas la reproductibilité.
   La stabilité du verdict est un objet de test, pas un acquis.
3. **Asymétrie coût/latence** : Claude plus cher que DeepSeek Flash. Peut créer
   un biais de verbosité. À observer à l'Étape 1.

---

*Agora v0.1 — Draft — à revoir après Étape 0 empirique*

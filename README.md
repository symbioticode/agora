# Agora — Laboratoire Agentique Minimal à Deux Agents

> **Source de vérité : GitHub** — code, documentation et résultats de sessions dans le même dépôt. Les agents IA et l'orchestrateur lisent depuis le repo.

## BLUF

Script Python pur (~90 lignes), Anthropic/Claude + DeepSeek directs, zéro framework, deux `pip install`. Deux agents aux mindsets opposés débattent d'une hypothèse (ouverture parallèle → tours contradictoires → verdict juge), sous observation humaine ou IA tierce, produisent un JSON gradué traçable.

**Leçon SecAudit** : l'hétérogénéité des providers est le seul levier empiriquement robuste (Zhang et al. 2025). Claude×2 = chambre d'écho.

**Avertissement** : MAD n'améliore pas les résultats de façon garantie (Smit et al. ICML 2024 ; Zhang et al. 2025). C'est un labo exploratoire. DReaMAD est retracté — ses idées sont utiles, ses chiffres ne sont pas des preuves.

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

**Règle fondamentale D-AGO-001** : Agent A et Agent B ne partagent jamais le même provider. Violation = chambre d'écho garantie.

## Installation

```bash
pip install -r requirements.txt
cp .env.example .env
# Éditer .env avec vos clés API
```

## Usage

```bash
python orchestrator.py \
  --hypothesis "L'eau pure bout à 100°C à pression standard." \
  --rounds 3
```

## Structure du projet

Voir `AGORA_PROJECT.md` pour la spécification complète.

## Tests

```bash
python scripts/lab_check.py
python -m pytest tests/
```

## Tracking

```bash
./scripts/lab_status.sh          # Dashboard
./scripts/lab_status.sh --report # Rapport markdown dans results/
./scripts/lab_status.sh --sessions # Dernières sessions
```
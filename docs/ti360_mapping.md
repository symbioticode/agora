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
*"Une validation de la structure n'est pas une validation du sens."*

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
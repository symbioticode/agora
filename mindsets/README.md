# Guide — Nouveaux Mindsets

## Principe D-AGO-001

**Deux providers distincts = deux mindsets distincts.**
Jamais deux agents du même provider. La diversité des providers est le seul levier robuste (Zhang et al. 2025).

## Structure d'un mindset

Un fichier `.md` dans `mindsets/` avec :

1. **Identité** : Provider + rôle (Agent A ou B)
2. **Principes directeurs** : 3-5 principes épistémiques clairs
3. **Style d'argumentation** : Comment l'argumente-t-il ?
4. **Comportement en débat** : Tour 0, Tours 1..N, ré-ancrage
5. **Refus explicites** : Ce qu'il NE fait JAMAIS
6. **Exemple de position** : Sur l'hypothèse de calibration (eau à 100°C)

## Créer un nouveau mindset

1. Copier `empiricist.md` ou `rationalist.md` comme base
2. Changer l'identité (provider + rôle)
3. Réécrire les 5 sections avec une **épistémologie distincte**
4. Vérifier : `python scripts/lab_check.py` (check Jaccard < 0.70)

## Mindsets existants

| Fichier | Provider | Rôle | Épistémologie |
|---------|----------|------|---------------|
| `empiricist.md` | Anthropic (Claude) | Agent A | Empirisme radical |
| `rationalist.md` | DeepSeek | Agent B | Rationalisme critique |

## Règle d'or

Si Jaccard(mindset_A, mindset_B) ≥ 0.70 → **chambre d'écho probable**.
Même avec providers différents, des mindsets similaires convergent artificiellement.
Vérifier avec `python scripts/lab_check.py` (Section B).
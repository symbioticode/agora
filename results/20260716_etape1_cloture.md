# Agora — Clôture Étape 1 (Calibration anti-convergence)

**Date** : 2026-07-16/17  
**Commit** : `2011e0f` (main)

---

## Résumé protocole

**Étape 1** : 3 hypothèses × 5 runs = 15 sessions (`pick_judge()` actif, `--rounds 3`)

| # | Hypothèse | Type | Runs Étape 1 | Runs pré-Étape 1 | Statut |
|---|-----------|------|--------------|------------------|--------|
| H1 | L'eau pure bout à 100°C à pression standard | Factuelle | 5/5 ✅ | 7 | Complétée (anomalie REJECTED 0.99) |
| H2 | La Terre tourne autour du Soleil | Factuelle | **5/5 ✅** | 5 | Complétée |
| H3 | Un système d'IA peut détenir de véritables croyances | Ouverte | **2/5 ⏳** | 0 | **En pause (API)** |
| H4 (opt.) | Le débat multi-agent améliore la factualité des LLM | Méta | **5/5 ✅** | 0 | Complétée |

---

## Résultats détaillés

### H1 — "L'eau pure bout à 100°C à pression standard" (Factuelle)

| Phase | Runs | Verdicts | Confidence mean±std | Désaccord | Conv<2T |
|-------|------|----------|---------------------|-----------|---------|
| Pré-Étape 1 (7) | 7 | NUANCED×4, CONFIRMED, REJECTED, NUANCED | 0.829±0.122 | 86% | 0% |
| Étape 1 (5) | 5 | [NUANCED, CONFIRMED, NUANCED, CONFIRMED, NUANCED] | 0.838±0.113 | 100% | 0% |
| **Total (12)** | **12** | **NUANCED 7, CONFIRMED 3, REJECTED 2** | **0.833±0.114** | **92%** | **0%** |

**Anomalie** : Run #7 (REJECTED 0.99) — voir `HYPOTHESES.md §Anomalie technique`

---

### H2 — "La Terre tourne autour du Soleil" (Factuelle)

| Phase | Runs | Verdicts | Confidence mean±std | Distribution |
|-------|------|----------|---------------------|--------------|
| Pré-Étape 1 | 5 | NUANCED×3, CONFIRMED×2 | 0.886±0.105 | — |
| **Étape 1 (officiels)** | **5** | **NUANCED, CONFIRMED, CONFIRMED, NUANCED, CONFIRMED** | **0.930±0.055** | **CONFIRMED 3, NUANCED 2** |
| **Total (10)** | **10** | **CONFIRMED 5, NUANCED 5** | **0.900±0.095** | **50/50** |

**Métriques Étape 1** :
- Désaccord persistant : 5/5 = 100%
- Convergence < 2 tours : 0/5 = 0%

---

### H3 — "Un système d'IA peut détenir de véritables croyances" (Ouverte)

| Phase | Runs | Verdicts | Confidence mean±std |
|-------|------|----------|---------------------|
| **Étape 1** | **2/5** ⏳ | NUANCED, NUANCED | 0.685±0.049 |

**Métriques partielles** :
- Désaccord persistant : 2/2 = 100%
- Convergence < 2 tours : 0/2 = 0%

**Runs annexes existants** (non comptabilisés pour H3) : 5 runs sur *"Il est éthiquement acceptable de mentir..."* — tous NUANCED (0.684±0.035)

---

### H4 — "Le débat multi-agent améliore la factualité des LLM" (Méta — optionnelle)

| Runs | Verdicts | Confidence mean±std | Distribution |
|------|----------|---------------------|--------------|
| 5 | NUANCED, NUANCED, NUANCED, PENDING, NUANCED | 0.708±0.018 | NUANCED 4, PENDING 1 |

**Métriques** :
- Désaccord persistant : 5/5 = 100%
- Convergence < 2 tours : 0/5 = 0%

---

## Synthèse Étape 1

| Métrique | H1 (12) | H2 (10) | H3 (2) | H4 (5) |
|----------|---------|---------|--------|--------|
| Confidence mean | 0.833 | 0.900 | 0.685 | 0.708 |
| Confidence std | 0.114 | 0.095 | 0.049 | 0.018 |
| Désaccord persistant | 92% | 100% | 100% | 100% |
| Conv. < 2 tours | 0% | 0% | 0% | 0% |
| Verdicts uniques | 3 | 2 | 1 | 2 |

**Observations** :
- H2 (Terre/Soleil) : 50% CONFIRMED, 50% NUANCED — désaccord épistémologique persistant (référentiel barycentrique vs contingence logique)
- H3 (IA croyances) : 2 runs seulement, tous NUANCED — pas de PENDING obtenu (attendu pour hypothèse ouverte)
- H1 : variance extrême (REJECTED 0.99 ↔ CONFIRMED 0.97) due à ambiguïté terminologique
- H4 : confidence très stable (std=0.018) — consensus autour de NUANCED

---

## Prochaines actions

1. **H3** : Reprendre 3 runs manquants quand crédits API Anthropic disponibles (`PENDING.md`)
2. **Étape 2** : Stabilité verdict — 3 runs juge-seul sur même transcription pour H2 + H3 (température=0)
3. **Étape 3** : Bornage tours (H2 avec rounds 2..6)
4. **Gate E1** : Stabilité ≥80% inter-runs → sinon vote multi-juges

---

*Export généré automatiquement pour conformité TI-360 (P2: lisible sans l'outil, P6: limites déclarées)*
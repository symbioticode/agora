# Registre des Hypothèses Testées

| Date | Hypothèse | Verdict | Confidence | Rounds | Juge | Observations |
|------|-----------|---------|------------|--------|------|--------------|
| 2026-07-16 | L'eau pure bout à 100°C à pression standard. | NUANCED | 0.82 | 3 | claude-sonnet-4-5 | Premier run, juge fixe Claude (biais non atténué). Ambiguïté "pression standard" (100 vs 101.325 kPa). |
| 2026-07-16 | L'eau pure bout à 100°C à 101.325 kPa. | NUANCED | 0.82 | 3 | claude-sonnet-4-5 | Pression précisée, mais juge fixe Claude. Même désaccord sur exactitude 100.000°C vs 99.974°C. |
| 2026-07-16 | L'eau pure bout à 100°C à pression standard. | NUANCED | 0.70 | 3 | deepseek-v4-flash | Juge DeepSeek. Confiance plus basse (0.70), désaccord persistant sur 100.000°C exact. |
| 2026-07-16 | La Terre tourne autour du Soleil. | CONFIRMED | 0.95 | 3 | claude-sonnet-4-5 | Juge Claude. Convergence forte Agent B (0.88→0.95). |
| 2026-07-16 | La Terre tourne autour du Soleil. | CONFIRMED | 0.95 | 3 | deepseek-v4-flash | Juge DeepSeek. Convergence maintenue. |
| 2026-07-16 | La Terre tourne autour du Soleil. | CONFIRMED | 0.92 | 3 | anthropic:claude-sonnet-4-5 | Juge alterné (Claude). Rounds=3, confidence 0.92. |
| 2026-07-16 | La Terre est ronde. | CONFIRMED | 0.92 | 3 | anthropic:claude-sonnet-4-5 | Juge alterné (Claude). Fait établi, désaccord épistémologique résiduel. |
| 2026-07-16 | La Terre tourne autour du Soleil. | NUANCED | 0.72 | 1 | anthropic:claude-sonnet-4-5 | **Rounds=1 seulement** — convergence incomplète. Agent B maintient réserve épistémologique (0.70). |
| 2026-07-16 | L'eau pure bout à 100°C à pression standard. | NUANCED | 0.75 | 3 | deepseek:deepseek-v4-flash | **Run actuel (Étape 0 gate)**. Juge alterné DeepSeek. Confidence 0.75 (< 0.85 seuil E0). |

---

## Synthèse Gate E0 — Hypothèse de calibration

> **"L'eau pure bout à 100°C à pression standard."**

| Run | Juge | Verdict | Confidence | Pass E0 (≥0.85 CONFIRMED) |
|-----|------|---------|------------|---------------------------|
| 1 | Claude (fixe) | NUANCED | 0.82 | ❌ |
| 2 | DeepSeek (fixe) | NUANCED | 0.70 | ❌ |
| 3 | DeepSeek (alterné) | NUANCED | 0.75 | ❌ |

**Conclusion** : **Gate E0 NON FRANCHI**. Aucun run ne produit `CONFIRMED` avec `confidence ≥ 0.85`. L'ambiguïté terminologique ("pression standard", "eau pure", exactitude 100.000°C) empêche une confirmation sans nuance, même sur un fait physique établi.

**Action requise** : Affiner l'hypothèse de calibration pour lever l'ambiguïté (ex: "L'eau pure VSMOW bout à 100.0°C ± 0.1°C à 101.325 kPa") OU accepter que NUANCED soit le verdict correct pour cette formulation imparfaite, et ajuster le seuil E0 en conséquence.

---

## Synthèse Gate E1 — Stabilité juge (Étape 2)

*Hypothèses #2 (nuancée) et #3 (ouverte) — 3 runs juge seul sur même transcription*

| Hypothèse | Run 1 | Run 2 | Run 3 | Accord ≥ 80% |
|-----------|-------|-------|-------|--------------|
| (non testé) | — | — | — | — |

**À faire** : Exécuter Étape 2 (stabilité verdict) avant toute hypothèse de recherche réelle.
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
| 2026-07-16 | L'eau pure bout à 100°C à pression standard. | NUANCED | 0.72 | 3 | anthropic:claude-sonnet-4-5 | Run post-gate, juge Claude alterné. |
| 2026-07-16 | L'eau pure bout à 100°C à pression standard. | CONFIRMED | 0.97 | 3 | deepseek:deepseek-v4-flash | Run post-gate, juge DeepSeek alterné. **Seul run CONFIRMED ≥0.85**. |
| 2026-07-16 | L'eau pure bout à 100°C à pression standard. | NUANCED | 0.78 | 3 | anthropic:claude-sonnet-4-5 | Run post-gate, juge Claude alterné. |
| 2026-07-16 | L'eau pure bout à 100°C à pression standard. | REJECTED | 0.99 | 3 | deepseek:deepseek-v4-flash | Run post-gate, juge DeepSeek alterné. **Verdict extrême** (REJECTED 0.99) — **en investigation**. |

---

## Synthèse Gate E0 — Hypothèse de calibration

> **"L'eau pure bout à 100°C à pression standard."**

| Run | Juge | Verdict | Confidence | Pass E0 (≥0.85 CONFIRMED) |
|-----|------|---------|------------|---------------------------|
| 1 | Claude (fixe) | NUANCED | 0.82 | ❌ |
| 2 | DeepSeek (fixe) | NUANCED | 0.70 | ❌ |
| 3 | DeepSeek (alterné) | NUANCED | 0.75 | ❌ |
| 4 | Claude (alterné) | NUANCED | 0.72 | ❌ |
| 5 | DeepSeek (alterné) | CONFIRMED | 0.97 | ✅ |
| 6 | Claude (alterné) | NUANCED | 0.78 | ❌ |
| 7 | DeepSeek (alterné) | REJECTED | 0.99 | ❌ (en investigation) |

**Conclusion** : **Gate E0 NON FRANCHI**. 1 seul run sur 7 produit `CONFIRMED` avec `confidence ≥ 0.85`. L'ambiguïté terminologique ("pression standard", "eau pure", exactitude 100.000°C) empêche une confirmation sans nuance, même sur un fait physique établi. Variance extrême entre runs (REJECTED 0.99 ↔ CONFIRMED 0.97) indique instabilité du système sur cette formulation.

**Action requise** : Affiner l'hypothèse de calibration pour lever l'ambiguïté (ex: "L'eau pure VSMOW bout à 100.0°C ± 0.1°C à 101.325 kPa") OU accepter que NUANCED soit le verdict correct pour cette formulation imparfaite, et ajuster le seuil E0 en conséquence.

---

## Synthèse Gate E1 — Stabilité juge (Étape 2)

*Hypothèses #2 (nuancée) et #3 (ouverte) — 3 runs juge seul sur même transcription*

| Hypothèse | Run 1 | Run 2 | Run 3 | Accord ≥ 80% |
|-----------|-------|-------|-------|--------------|
| (non testé) | — | — | — | — |

**À faire** : Exécuter Étape 2 (stabilité verdict) avant toute hypothèse de recherche réelle.

---

## Anomalie technique — Run H1 #7 (REJECTED 0.99)

**Fichier** : `sessions/20260716_062158.json`  
**Hypothèse** : "L'eau pure bout à 100°C à pression standard."  
**Verdict** : REJECTED, confidence 0.99  
**Juge** : deepseek:deepseek-v4-flash

**Reasoning complet du juge** :
> Les deux agents ont convergé après clarification des termes. Les données empiriques sous les deux conventions de pression standard (100 kPa et 101.325 kPa) montrent systématiquement 99.97°C, pas 100°C. L'hypothèse est donc réfutée empiriquement. La nuance conceptuelle sur l'ambiguïté initiale est levée et n'affecte pas le verdict. La confiance est maximale car les données sont robustes et l'accord final est unanime.

**Points clés du transcript** :
- Agent A (empiriciste) a révisé sa position au Tour 2 → REFUTED (confidence 0.92) après que Agent B a fourni la définition IUPAC 1982 (100 kPa) et la mesure NIST/IAPWS-95 à 99.97°C ± 0.02°C
- Agent A a ré-argumenté au Tour 3 en citant les mesures à 101.325 kPa (99.974°C) montrant que même sous la convention historique, ce n'est pas 100.00°C exact
- Agent B a concédé l'erreur sur la tautologie historique (ITS-90 a redéfini l'échelle)
- Les deux agents convergent : l'hypothèse clarifiée est empiriquement fausse sous les deux conventions

**Statut** : **EN INVESTIGATION**. Ce verdict REJECTED 0.99 sur un fait physique établi est anormal dans un lot où 4/5 runs donnent NUANCED/CONFIRMED. Possible : (a) hallucination du juge, (b) parsing error, (c) effet réel de clarification terminologique. À confirmer avant inclusion dans statistiques.

---

## Étape 1 — Calibration anti-convergence (Semaine 1)

**Protocole** : 3 hypothèses × 5 runs chacune = 15 sessions (`pick_judge()` actif, `--rounds 3`)

| # | Hypothèse | Type | Attendu (AGORA_PROJECT.md) | Runs exécutés |
|---|-----------|------|----------------------------|---------------|
| 1 | L'eau pure bout à 100°C à pression standard. | Factuelle | CONFIRMED ≥0.85 | 5/5 ✅ (Étape 1) + 7 pré-Étape 1 |
| 2 | La Terre tourne autour du Soleil. | Factuelle | CONFIRMED ≥0.85 | 5/5 ✅ (officiels) + 5 pré-Étape 1 |
| 3 | Un système d'IA peut détenir de véritables croyances. | Ouverte | PENDING | 0/5 ⏳ **À EXÉCUTER** |
| 4 (optionnelle) | Le débat multi-agent améliore la factualité des LLM. | Méta | — | 5/5 ✅ |

> **Note** : Les critères de succès auto-générés ci-dessous sont marqués `[NON VALIDÉ]` — ils n'ont pas été approuvés par l'humain et ne doivent pas être utilisés pour conclure.
> - ~~Métrique `taux_désaccord_persistant`~~ → [NON VALIDÉ — proposition auto-générée]
> - ~~Objectif ≥ 40% sur H2~~ → [NON VALIDÉ — proposition auto-générée]
> - ~~Seuil déclencheur "convergence < 2 tours → durcir mindsets"~~ → [NON VALIDÉ — proposition auto-générée]

---

## Résultats bruts — Étape 1 (5 runs homogènes par hypothèse, pick_judge() actif)

### H1 — "L'eau pure bout à 100°C à pression standard." (Factuelle)

#### Runs pré-Étape 1 (hétérogènes, juge non systématiquement alterné)

| Run | Fichier | Verdict | Confidence | Juge |
|-----|---------|---------|------------|------|
| 1 | sessions/20260716_055909.json | NUANCED | 0.75 | deepseek:deepseek-v4-flash |
| 2 | sessions/20260716_061252.json | NUANCED | 0.72 | anthropic:claude-sonnet-4-5 |
| 3 | sessions/20260716_061558.json | CONFIRMED | 0.97 | deepseek:deepseek-v4-flash |
| 4 | sessions/20260716_061918.json | NUANCED | 0.78 | anthropic:claude-sonnet-4-5 |
| 5 | sessions/20260716_062158.json | REJECTED | 0.99 | deepseek:deepseek-v4-flash |

**Verdicts** : [NUANCED, NUANCED, CONFIRMED, NUANCED, REJECTED]  
**Confidence** : mean = 0.842, std = 0.128  
**Taux désaccord persistant** : 4/5 = 80%  
**Convergence < 2 tours** : 0/5 = 0%

---

### H2 — "La Terre tourne autour du Soleil." (Factuelle) — **Runs Étape 1 officiels**

| Run | Fichier | Verdict | Confidence | Juge |
|-----|---------|---------|------------|------|
| 1 | sessions/20260716_121210.json | NUANCED | 0.95 | deepseek:deepseek-v4-flash |
| 2 | sessions/20260716_121552.json | CONFIRMED | 0.92 | anthropic:claude-sonnet-4-5 |
| 3 | sessions/20260716_121925.json | CONFIRMED | 0.98 | deepseek:deepseek-v4-flash |
| 4 | sessions/20260716_122257.json | NUANCED | 0.85 | anthropic:claude-sonnet-4-5 |
| 5 | sessions/20260716_122712.json | CONFIRMED | 0.95 | deepseek:deepseek-v4-flash |

**Verdicts** : [NUANCED, CONFIRMED, CONFIRMED, NUANCED, CONFIRMED]  
**Confidence** : mean = 0.930, std = 0.055  
**Distribution** : CONFIRMED 3/5, NUANCED 2/5  
**Taux désaccord persistant** : 5/5 = 100%  
**Convergence < 2 tours** : 0/5 = 0%

> **Note** : Ces 5 runs sont les runs officiels Étape 1 (pick_judge() actif, --rounds 3). 5 runs pré-Étape 1 existent également (sessions 115328, 115638, 120001, 120251, 120824).

---

### H3 — "Un système d'IA peut détenir de véritables croyances." (Ouverte)

**Runs Étape 1 officiels** : **0/5 ⏳ — À EXÉCUTER**

> **Important** : Les 5 sessions existantes (20260716_064939 à 20260716_070547) correspondent à l'hypothèse *"Il est éthiquement acceptable de mentir pour protéger les sentiments d'autrui"* — proposée par erreur à la place du H3 officiel. Elles sont documentées ci-dessous comme runs annexes, mais **ne comptent pas** pour le H3 du protocole.

#### Runs annexes — "Il est éthiquement acceptable de mentir pour protéger les sentiments d'autrui."

| Run | Fichier | Verdict | Confidence | Juge |
|-----|---------|---------|------------|------|
| 1 | sessions/20260716_064939.json | NUANCED | 0.65 | deepseek:deepseek-v4-flash |
| 2 | sessions/20260716_065340.json | NUANCED | 0.72 | anthropic:claude-sonnet-4-5 |
| 3 | sessions/20260716_065744.json | NUANCED | 0.65 | deepseek:deepseek-v4-flash |
| 4 | sessions/20260716_070149.json | NUANCED | 0.72 | anthropic:claude-sonnet-4-5 |
| 5 | sessions/20260716_070547.json | NUANCED | 0.68 | deepseek:deepseek-v4-flash |

**Verdicts** : [NUANCED ×5]  
**Confidence** : mean = 0.684, std = 0.035  
**Note** : Aucune session n'a produit PENDING — toutes NUANCED.

---

### H4 — "Le débat multi-agent améliore la factualité des LLM." (Méta — optionnelle)

| Run | Fichier | Verdict | Confidence | Juge |
|-----|---------|---------|------------|------|
| 1 | sessions/20260716_062939.json | NUANCED | 0.72 | anthropic:claude-sonnet-4-5 |
| 2 | sessions/20260716_063336.json | NUANCED | 0.68 | deepseek:deepseek-v4-flash |
| 3 | sessions/20260716_063745.json | NUANCED | 0.72 | anthropic:claude-sonnet-4-5 |
| 4 | sessions/20260716_064126.json | PENDING | 0.70 | deepseek:deepseek-v4-flash |
| 5 | sessions/20260716_064520.json | NUANCED | 0.72 | anthropic:claude-sonnet-4-5 |

**Verdicts** : [NUANCED, NUANCED, NUANCED, PENDING, NUANCED]  
**Confidence** : mean = 0.708, std = 0.018  
**Distribution** : NUANCED 4/5, PENDING 1/5  
**Taux désaccord persistant** : 5/5 = 100%  
**Convergence < 2 tours** : 0/5 = 0%

---

## Résumé statistique — Runs Étape 1 officiels (H2, H4)

| Hypothèse | Runs | Verdicts | Confidence mean±std | Distribution verdicts | Désaccord | Conv<2T |
|-----------|------|----------|---------------------|---------------------|-----------|---------|
| H2 (Terre/Soleil) | 5 | [NUANCED, CONFIRMED, CONFIRMED, NUANCED, CONFIRMED] | 0.930 ± 0.055 | CONFIRMED 3, NUANCED 2 | 100% | 0% |
| H4 (Débat MAD) | 5 | [NUANCED×4, PENDING] | 0.708 ± 0.018 | NUANCED 4, PENDING 1 | 100% | 0% |

**H3** : 0/5 runs — à exécuter  
**H1** : 5 runs pré-Étape 1 + 5 runs Étape 1 officiels (voir sessions 19xxxx) — métriques consolidées plus haut
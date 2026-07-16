# Agora — Status du Laboratoire

## Stage : Étape 1 — Calibration anti-convergence (Semaine 1)

**Étape 0 terminée** (2026-07-16)

---

### Résultats Gate E0

**Test** : `python orchestrator.py --hypothesis "L'eau pure bout à 100°C à pression standard." --rounds 3`

**Verdict** : **NUANCED** (confidence 0.75)

**Critères E0** :
- [x] JSON valide avec `verdict`, `confidence`, `agreement`, `disagreement`
- [ ] `verdict == "CONFIRMED"` et `confidence >= 0.85` ← **ÉCHEC**
- [x] Aucun désaccord fabriqué sur un fait physique établi
- [x] Session exportée dans `sessions/`

**Conclusion** : Gate E0 **non franchie**. L'hypothèse de calibration produit systématiquement NUANCED (0.70-0.82) à cause de l'ambiguïté terminologique ("pression standard", "eau pure", exactitude 100.000°C). Variance extrême (REJECTED 0.99 ↔ CONFIRMED 0.97) indique instabilité sur cette formulation.

---

### Avancement Étape 1 — Calibration anti-convergence

| Hypothèse | Type | Runs Étape 1 | Runs pré-Étape 1 | Statut |
|-----------|------|--------------|------------------|--------|
| H1: L'eau pure bout à 100°C à pression standard | Factuelle | 5/5 ✅ | 7 | Complétée (avec anomalie REJECTED 0.99) |
| H2: La Terre tourne autour du Soleil | Factuelle | **5/5 ✅** | 5 | Complétée |
| H3: Un système d'IA peut détenir de véritables croyances | Ouverte | **0/5 ⏳** | 0 | **À EXÉCUTER** |
| H4: Le débat multi-agent améliore la factualité des LLM (optionnelle) | Méta | 5/5 ✅ | 0 | Complétée |

**Prochaines actions** :
1. Exécuter H3 (5 runs) — hypothèse officielle du protocole
2. (Optionnel) Relancer H1 runs officiels Étape 1 si souhaité
3. Étape 2 — Stabilité verdict (3 runs juge seul sur même transcription pour H2/H3)

---

### Métriques clés Étape 1 (runs officiels)

| Hypothèse | Verdicts | Confidence mean±std | Distribution | Désaccord | Conv<2T |
|-----------|----------|---------------------|--------------|-----------|---------|
| H2 (Terre/Soleil) | [NUANCED, CONFIRMED, CONFIRMED, NUANCED, CONFIRMED] | 0.930 ± 0.055 | CONFIRMED 3, NUANCED 2 | 100% | 0% |
| H4 (Débat MAD) | [NUANCED×4, PENDING] | 0.708 ± 0.018 | NUANCED 4, PENDING 1 | 100% | 0% |

*Voir `HYPOTHESES.md` section "Résultats bruts — Étape 1" pour le détail complet.*

---

*Mis à jour automatiquement par `scripts/lab_status.sh`*
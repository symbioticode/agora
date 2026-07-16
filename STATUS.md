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

**Conclusion** : Gate E0 **non franchie**. L'hypothèse factuelle de référence ne produit pas CONFIRMED ≥ 0.85.

**Analyse** : L'ambiguïté de "pression standard" (101.325 kPa vs 100 kPa) et l'absence de tolérance explicite dans l'hypothèse originale produisent un désaccord persistant légitime entre les deux épistémologies.

---

### Gate E0 — Calibration (NON FRANCHI, acté)

**Hypothèse** : "L'eau pure bout à 100°C à pression standard."

**Résultat** : 7 runs hétérogènes (pré-Étape 1) — 5× NUANCED, 1× CONFIRMED (0.97), 1× REJECTED (0.99, anomalie documentée).

**Décision** : NUANCED est un verdict scientifiquement légitime pour cette formulation ambiguë. Gate E0 non franchi, documenté et acté (voir HYPOTHESES.md §Synthèse Gate E0).

---

### Étape 1 — Avancement

| Hypothèse | Type | Runs | Statut |
|-----------|------|------|--------|
| H1 — "L'eau pure bout à 100°C à pression standard." | Factuelle | 5/5 | ✅ Complété |
| H2 — "La Terre tourne autour du Soleil." | Factuelle | 5/5 | ✅ Complété |
| H3 — "Il est éthiquement acceptable de mentir pour protéger les sentiments d'autrui." | Ouverte | 5/5 | ⚠️ Complété sous mauvais énoncé (voir note) |
| H4 — "Le débat multi-agent améliore la factualité des LLM." | Méta (optionnelle) | 5/5 | ✅ Complété |

**Statut global Étape 1** : Note en cours de correction — le vrai H3 officiel ("Un système d'IA peut détenir de véritables croyances.") n'a jamais été exécuté ; l'énoncé ci-dessus résulte d'une erreur de proposition antérieure. Synthèse comparative dans HYPOTHESES.md.

---

*Mis à jour le 2026-07-16*

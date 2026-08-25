# Agora — Status du Laboratoire

## Stage : Étape 2 — Confirmation prospective du fallback multi-juges

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
| H3: Un système d'IA peut détenir de véritables croyances | Ouverte | **2/5 ⏳** | 0 | Partielle; 3 runs bloqués par crédit Anthropic |
| H4: Le débat multi-agent améliore la factualité des LLM (optionnelle) | Méta | 5/5 ✅ | 0 | Complétée |

**Prochaines actions** :
1. Compléter H3 (3 runs restants) — hypothèse officielle du protocole
2. (Optionnel) Relancer H1 runs officiels Étape 1 si souhaité
3. Étape 2 — Stabilité verdict (3 runs juge seul sur même transcription pour H2/H3)

**Préparation Étape 2 (branche Codex 2026-08-10)** : manifeste hors-ligne et
analyseur disponibles dans `scripts/step2_stability.py`. Deux transcriptions
réelles sont figées; aucun jugement Étape 2 n'a été exécuté. Le Gate E1 reste
ouvert et exige des appels explicitement autorisés.

**Variante E1-O Omniroute prolongée (2026-08-10)** : 40 jugements sur 10 min
17 s, deux modèles Mistral distincts, 100 % de stabilité sur H2/H3, cache
désactivé et coût Omniroute déclaré $0. **E1-O franchi**, mais le Gate E1 direct
Anthropic↔DeepSeek reste ouvert : les deux modèles E1-O partagent le provider
Mistral et ne mesurent donc pas l'effet inter-provider.

**Gate E1 direct (2026-08-10)** : exécuté sur 12/12 jugements. H2 passe chez
les deux juges et H3 passe chez Sonnet 4.5; H3/DeepSeek obtient seulement
66,7 % d'accord (`PENDING, NUANCED, NUANCED`). **E1 non franchi** au seuil de
80 %. Coût conservateur : 0,136146 USD Anthropic et 0,062343 USD DeepSeek,
incident vide inclus.

**Fallback multi-juges (2026-08-25)** : les 32 preuves existantes ont été
réagrégées à poids égal par provider. H2 donne CONFIRMED 3/3 providers et H3
NUANCED 3/3 providers. Ce signal est rétrospectif et ne franchit aucune gate.
Le manifeste prospectif fige six nouveaux jugements indépendants; exécution en
attente de plafonds Anthropic/DeepSeek explicites. Étape 3 bloquée jusque-là.

---

### Métriques clés Étape 1 (runs officiels)

| Hypothèse | Verdicts | Confidence mean±std | Distribution | Désaccord | Conv<2T |
|-----------|----------|---------------------|--------------|-----------|---------|
| H2 (Terre/Soleil) | [NUANCED, CONFIRMED, CONFIRMED, NUANCED, CONFIRMED] | 0.930 ± 0.055 | CONFIRMED 3, NUANCED 2 | 100% | 0% |
| H4 (Débat MAD) | [NUANCED×4, PENDING] | 0.708 ± 0.018 | NUANCED 4, PENDING 1 | 100% | 0% |

*Voir `HYPOTHESES.md` section "Résultats bruts — Étape 1" pour le détail complet.*

---

*Mis à jour automatiquement par `scripts/lab_status.sh`*

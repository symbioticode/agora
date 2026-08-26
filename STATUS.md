# Agora — Status du Laboratoire

## Stage : recette de qualification franchie — instrument supervisé

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
1. Employer la configuration qualifiée sur un premier sujet de recherche supervisé
2. Étendre ultérieurement l'auto-préférence à plusieurs transcriptions
3. Dette secondaire : compléter les trois débats H3 de l'Étape 1

**Préparation Étape 2 (branche Codex 2026-08-10)** : le manifeste hors-ligne
et l'analyseur de `scripts/step2_stability.py` ont servi à figer deux
transcriptions. Cette phase de préparation est terminée; les résultats directs
et collectifs sont décrits ci-dessous.

**Variante E1-O Omniroute prolongée (2026-08-10)** : 40 jugements sur 10 min
17 s, deux modèles Mistral distincts, 100 % de stabilité sur H2/H3, cache
désactivé et coût Omniroute déclaré $0. **E1-O franchi**, sans conclure sur E1
direct : les deux modèles E1-O partagent le provider Mistral et ne mesurent
donc pas l'effet inter-provider. E1 direct a ensuite été exécuté et a échoué.

**Gate E1 direct (2026-08-10)** : exécuté sur 12/12 jugements. H2 passe chez
les deux juges et H3 passe chez Sonnet 4.5; H3/DeepSeek obtient seulement
66,7 % d'accord (`PENDING, NUANCED, NUANCED`). **E1 non franchi** au seuil de
80 %. Coût conservateur : 0,136146 USD Anthropic et 0,062343 USD DeepSeek,
incident vide inclus.

**Fallback multi-juges (2026-08-25)** : les 32 preuves existantes ont été
réagrégées à poids égal par provider. H2 donne CONFIRMED 3/3 providers et H3
NUANCED 3/3 providers. Ce signal est rétrospectif et ne franchit aucune gate.
Le manifeste prospectif a ensuite produit six nouveaux jugements : H2 est
CONFIRMED 3/3 providers et H3 NUANCED 3/3 providers. **Fallback collectif
franchi.** Coût estimé : 0,085497 USD Anthropic, 0,020429 USD DeepSeek et 0 USD
Mistral. E1 direct reste historiquement échoué; l'Étape 3 est maintenant
débloquée.

**Étape 3 (2026-08-25)** : les cinq réglages `{2,3,4,5,6}` ont été collectés
selon le manifeste prospectif. Aucun drift n'est observé; une reformulation
apparaît au réglage 3 et la nouveauté marginale reste au-dessus du seuil pour
tous les réglages. La règle préenregistrée recommande 6 tours, désormais valeur
par défaut. Coût estimé de l'étape : 0,409434 USD Anthropic et 0,137625 USD
DeepSeek. Limite : une seule session par réglage; 6 est la borne haute testée,
pas un optimum universel démontré.

**Recette finale (2026-08-25)** : le test d'étiquette ne détecte aucun biais
d'auto-préférence chez les deux juges payants. Trois cycles collectifs
successifs reproduisent H2 `CONFIRMED` et H3 `NUANCED`, à 3/3 providers. Les
cinq critères sont simultanément satisfaits. AGORA est qualifié comme
instrument de recherche supervisé, pas comme autorité d'action autonome.

---

### Métriques clés Étape 1 (runs officiels)

| Hypothèse | Verdicts | Confidence mean±std | Distribution | Désaccord | Conv<2T |
|-----------|----------|---------------------|--------------|-----------|---------|
| H2 (Terre/Soleil) | [NUANCED, CONFIRMED, CONFIRMED, NUANCED, CONFIRMED] | 0.930 ± 0.055 | CONFIRMED 3, NUANCED 2 | 100% | 0% |
| H4 (Débat MAD) | [NUANCED×4, PENDING] | 0.708 ± 0.018 | NUANCED 4, PENDING 1 | 100% | 0% |

*Voir `HYPOTHESES.md` section "Résultats bruts — Étape 1" pour le détail complet.*

---

*Mis à jour le 2026-08-25; `scripts/lab_status.sh` ne doit pas écraser les
résultats des gates Étape 2.*

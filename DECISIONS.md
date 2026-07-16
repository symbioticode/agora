# Décisions d'architecture

## D-AGO-001 — Deux providers distincts (Anthropic + DeepSeek)
Date : 2026-07-16
Raison : hétérogénéité = seul levier robuste (Zhang et al. 2025).
Claude×2 = chambre d'écho (SecAudit Sprint 5 + ICML 2024).
Référence : docs/research_notes.md §Key Findings 1

## D-AGO-002 — Zéro framework (script pur, 2 pip install)
Date : 2026-07-16
Raison : Karpathy impose OpenRouter ; AutoGen bugue avec Anthropic
sur l'alternance des rôles ; CAMEL conçu pour coopération, pas débat.
Référence : docs/research_notes.md §Tableau comparatif

## D-AGO-003 — Format hybride (parallèle + contradictoire + juge)
Date : 2026-07-16
Raison : Tour 0 parallèle évite l'ancrage précoce (conformity drift).
Ré-ancrage hypothèse à chaque tour (anti problem drift, Becker EACL 2026).
Juge à temperature=0 (déterminisme relatif).

## D-AGO-004 — DEFAULT_ROUNDS = 3
Date : 2026-07-16
Raison : consensus se solidifie en 2-3 tours ; drift nette au-delà.
À revalider empiriquement à l'Étape 3.

## D-AGO-005 — DReaMAD non cité comme preuve de performance
Date : 2026-07-16
Raison : retracté par les auteurs (ICML 2025, sans raison publiée).
Heuristiques (diversification perspectives) utiles, chiffres non fiables.

## D-AGO-006 — TI-360 : Geste A retenu (use case), Geste B différé
Date : 2026-07-16
Raison : les outputs d'Agora (sessions JSON + verdicts 4 valeurs) sont
structurellement des atomes TI-360 — convergence non planifiée, documentée
a posteriori dans docs/ti360_mapping.md. Le Geste B (implémentation du
graphe complet Sources→Extractions→Questions→Décisions + refus mécanique
des transitions d'état) est différé : TI-360 est en v0.1 DRAFT, Agora
est exploratoire, empiler deux systèmes à limites non résolues augmente
la surface d'échec.
Retour prévu : quand TI-360 atteint v0.2 avec périmètre validé ET quand
les Étapes 0-3 d'Agora ont produit des données empiriques réelles.
Référence : docs/ti360_mapping.md · TI360_Principes_Implementation_v0_1.md

## D-AGO-007 — Juge : alternance providers pour atténuer biais d'auto-préférence
Date : 2026-07-16
Raison : Avec 2 providers (Anthropic + DeepSeek), P4 strict TI-360
(juge ≠ Agent A ≠ Agent B) est impossible sans 3e provider.
Le biais d'auto-préférence (juge = même provider qu'Agent A = Claude)
est documenté (Point ouvert #1, Étape 2).
Règle : `pick_judge()` alterne aléatoirement entre Anthropic et DeepSeek
à chaque run. Check `lab_check.py` Section D vérifie : aucune session
n'a `judge == Agent A` (Claude). Si futur 3e provider ajouté (OpenAI),
P4 strict réactivable.
Référence : AGORA_PROJECT.md §Points ouverts #1 ; docs/ti360_mapping.md §P4 (assoupli + "Ce qu'Agora ne couvre pas")
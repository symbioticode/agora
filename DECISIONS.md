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

## D-AGO-008 — Fallback collectif à trois providers après échec E1
Date : 2026-08-25
Raison : E1 direct a échoué sur H3/DeepSeek à 66,7 %. La branche prévue du
protocole est un vote multi-juges. Une analyse rétrospective favorable a été
conservée comme non préenregistrée, puis six nouveaux votes ont confirmé
prospectivement H2 CONFIRMED et H3 NUANCED à 3/3 providers.
Règle : une voix par provider; majorité 2/3; répartition 1-1-1 = PENDING.
E1 direct reste historiquement échoué. Le fallback collectif franchi débloque
l'Étape 3 sans prétendre établir l'indépendance épistémique des modèles.
Référence : docs/KB-ETAPE2-VOTE-MULTIJUGES.md

## D-AGO-009 — PENDING bloque l'action; NUANCED peut qualifier une idée
Date : 2026-08-25
Raison : l'incertitude épistémique et l'autorisation opérationnelle ne sont pas
le même objet. H3 évalue une idée sans action associée; son verdict NUANCED
conserve correctement le désaccord. Une action exige en revanche un fort degré
de confiance et ne doit jamais partir d'un verdict PENDING.
Règle : PENDING bloque toujours l'action. NUANCED est acceptable sans action;
avec action, il bloque par défaut jusqu'à confirmation humaine ou preuve plus
forte. CONFIRMED reste soumis aux permissions et postconditions de l'action.
Référence : PROGRESSION.md

## D-AGO-010 — DEFAULT_ROUNDS = 6 après bornage prospectif
Date : 2026-08-25
Raison : les cinq réglages préenregistrés `{2,3,4,5,6}` ont été exécutés sur
la même hypothèse et classés par un tiers. Aucun drift n'a été détecté; le taux
de nouveauté marginal est resté supérieur au seuil de 25 % jusque 6. La règle
préenregistrée choisit donc la borne haute testée.
Règle : `DEFAULT_ROUNDS = 6`. Ce choix remplace D-AGO-004 pour le réglage
courant sans prétendre établir un optimum universel : une seule session par
réglage a été exécutée et aucun réglage supérieur à 6 n'a été testé.
Référence : results/step3_rounds/manifest.json et analysis.json

## D-AGO-011 — Qualification comme instrument supervisé
Date : 2026-08-25
Raison : le test contrôlé d'auto-préférence ne détecte aucun effet d'étiquette
chez les juges Anthropic et DeepSeek. Trois cycles temporels reproduisent les
verdicts collectifs H2/H3 avec unanimité des trois providers. La recette locale
réunit ainsi les cinq critères définis.
Règle : AGORA est qualifié comme instrument de recherche supervisé. Cette
qualification ne transforme jamais un verdict en permission d'action et ne
prétend pas généraliser un test sur une transcription à tous les domaines.
Référence : results/self_preference/, results/temporal_stability/ et
results/final_qualification.json

## D-AGO-012 — L'expérience supervisée est l'objet durable de l'UI
Date : 2026-08-26
Raison : l'interface doit montrer les échanges entre IA et conserver leur
contexte comme matériau de recherche. Une simple session horodatée ne suffit
pas pour relier, comparer et auditer ces observations dans le temps.
Règle : chaque nouvel entretien reçoit un identifiant `AGO-EXP-YYYY-NNNN` et
conserve séparément question, contexte, configuration, transcription, verdict,
inconnues et observation humaine. Un replay reçoit un nouvel identifiant et
référence son parent. Le verdict machine ne remplace jamais l'observation du
superviseur.
Référence : docs/PROGRAMME-RECHERCHE-CONNAISSANCE.md et
docs/PLAN-INTEGRATION-UI-BCP-HUB.md

## D-AGO-014 — Reprise UI bornée au Lab #2

Date : 2026-08-27
Raison : l'UI exigeait `SUPERVISED_RESEARCH`, alors que le runtime corrigé ne
pouvait exposer que `EXECUTION_SUSPENDED` ou `REQUALIFICATION_REQUIRED`. Même
avec un diagnostic provider réussi, aucun lancement de requalification n'était
donc mécaniquement possible.
Règle : lorsque les deux providers sont disponibles, l'UI peut entrer en
`LAB_2_SUPERVISED`. Dans ce mode, l'API accepte uniquement une hypothèse et
l'objectif exacts du manifeste LAB-2; toute recherche libre reste bloquée.
L'autorisation n'entraîne aucun lancement automatique et chaque run demeure
supervisé. Un statut provider restauré d'une ancienne session reste affiché à
titre diagnostique mais ne bloque pas ce mode borné; seul un appel réellement
échoué crée une preuve d'échec.
Référence : `labs/LAB-2/manifest.json`, `agora/web.py` et `ui/index.jsx`.

## D-AGO-015 — Ouverture des questions supervisées libres

Date : 2026-08-27
Raison : le périmètre LAB-2 ne doit plus empêcher l'utilisateur de créer une
expérience générale depuis l'interface.
Règle : le mode `SUPERVISED_RESEARCH` accepte toute question non vide. LAB-2
reste mesuré séparément par correspondance exacte de l'objectif et de
l'hypothèse; il ne constitue plus une restriction de saisie ou de lancement.

## D-AGO-016 — Réponses agent bornées et complètes

Date : 2026-08-27
Raison : plusieurs prises de parole de `AGO-EXP-2026-0005` ont atteint la
limite de génération provider et se terminent au milieu d'un mot.
Règle : chaque prompt agent impose au maximum 300 mots et 2400 caractères,
Markdown compris, avec conclusion complète. Les plafonds provider de 2000 et
8000 tokens restent une marge technique et ne sont plus la longueur cible.
Le budget DeepSeek inclut son raisonnement interne non affiché. Une réponse
signalée `max_tokens` ou `finish_reason=length` est refusée et ne peut plus être
enregistrée silencieusement comme une prise de parole complète.

## D-AGO-013 — AGORA canonique, KBM 2.0 comme projection quotidienne
Date : 2026-08-26
Raison : les expériences doivent rester proches du code et de leurs preuves,
tout en devenant consultables dans la documentation AGORA sous `home-kbm`.
Deux sources modifiables indépendamment rendraient la provenance ambiguë.
Règle : AGORA est canonique pour `AGO-EXP-*`. KBM 2.0 importe depuis GitHub une
projection quotidienne portant identifiant, révision et hash source. Toute
correction de fond repart d'AGORA. L'import est idempotent, journalisé et sans
suppression implicite.
Référence : docs/PROGRAMME-RECHERCHE-CONNAISSANCE.md et
docs/PLAN-INTEGRATION-UI-BCP-HUB.md

# Plan d'exécution API — 00:00 à 04:00 America/Toronto

## Autorisation et plafonds

Andrei a autorisé Anthropic (solde annoncé 4,52 USD) et DeepSeek (4,16 USD)
uniquement entre 00:00 inclus et 04:00 exclu, pour AGORA et substrat-bench.

Plafonds opérationnels cumulés visés pour la nuit : 3,50 USD Anthropic et
3,00 USD DeepSeek, en conservant respectivement 1,02 USD et 1,16 USD de marge.
AGORA reçoit d'abord un sous-plafond de 1,50 USD par provider. Le solde n'est
alloué à substrat-bench qu'après mesure réelle de l'Étape 2.

## Ordre piloté par gates

1. Tests hors réseau et vérification des clés, sans afficher leur valeur.
2. Un ping de cinq tokens par provider après 00:00.
3. Gate E1 AGORA : H2/H3, trois jugements par provider, température 0.
4. Analyse du seuil ≥80 %, commit/push et mise à jour immédiate du KBM.
5. Audit du budget réellement consommé.
6. substrat-bench : exécution par petits lots reprenables; aucun Cycle C ne
   sera déclaré sans Cycles A/B valides et constat de la règle M09.
7. Arrêt de tout nouvel appel à 04:00, même si un lot reste incomplet.

## Résilience rate-limit et interruption

- un fichier JSON par réponse, écrit immédiatement;
- noms déterministes : une reprise saute les appels déjà présents;
- manifeste avant le premier appel, analyse après chaque lot complet;
- montée en charge séquentielle et intervalle entre appels;
- sur HTTP 429 : respecter `retry-after`, sans parallélisme ni rafale;
- budget projeté vérifié avant chaque appel, usage réel enregistré après;
- aucun retry payant sur erreur non transitoire;
- événements/erreurs consignés au fil de l'eau.

Le cache natif Anthropic est activé avec TTL éphémère et vérifié via
`cache_creation_input_tokens`/`cache_read_input_tokens`. Le cache KV DeepSeek
est automatique et vérifié via `prompt_cache_hit_tokens`/`prompt_cache_miss_tokens`.
Le mode thinking V4 Flash, actif par défaut, est explicitement désactivé pour
le juge JSON (`thinking.type=disabled`) afin d'éviter qu'il consomme le budget
de sortie avant le verdict — dette déjà observée dans ETAU-CAVEMAN.
La couche cache/mémoire Omniroute n'intervient pas : les appels de cette nuit
sont directs. Elle avait été désactivée dans E1-O pour exclure tout replay du
gateway; les deux expériences restent ainsi interprétables séparément.

## Recherche appliquée

La documentation Anthropic indique des limites RPM/ITPM/OTPM, un HTTP 429 et
un en-tête `retry-after`; elle avertit aussi qu'une hausse brusque peut activer
une limite d'accélération. D'où l'exécution séquentielle et progressive.

La documentation DeepSeek indique une limite de concurrence et HTTP 429. Au
10 août 2026, elle affiche pour V4 Flash 0,14 USD/MTok cache miss et
0,28 USD/MTok sortie, tout en annonçant une hausse prochaine. Le runner garde
donc une estimation volontairement plus conservatrice (1/5 USD par MTok).

Claude Sonnet 4.5 est estimé au tarif public 3 USD/MTok entrée et 15 USD/MTok
sortie. Ces prix sont des hypothèses de contrôle; le solde du compte reste la
référence comptable réelle.

## Choix du Sonnet

La documentation Anthropic consultée avant exécution classe Sonnet 5 comme
Sonnet courant, tout en maintenant `claude-sonnet-4-5-20250929` actif au moins
jusqu'au 29 septembre 2026. E1 conserve le snapshot 4.5 épinglé : remplacer le
juge par Sonnet 5 casserait la comparaison avec le protocole préparé. Une
comparaison Sonnet 5 éventuelle devra porter un identifiant d'expérience
distinct et ne sera pas mélangée au Gate E1.

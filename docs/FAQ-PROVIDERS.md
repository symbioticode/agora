---
id: FAQ-AGO-001
type: faq
project: AGORA
status: ACTIVE
date: 2026-08-26
audience: human-agent
scope: home
maturity: operational
source_of_truth: symbioticode/agora
nav_title: FAQ providers
section: corpus/home/agora
tags:
  - agora
  - providers
  - diagnostic
  - anthropic
  - deepseek
---

# FAQ AGORA — État et diagnostic des providers LLM

## Que signifient les pastilles ?

| État | Signification | Action |
|---|---|---|
| `UNCONFIGURED` | clé absente du service | configurer `.env`, puis redémarrer hors run actif |
| `READY` | clé présente, aucune réponse valide encore observée par ce processus | lancer un test supervisé |
| `ON` | une réponse finale non vide a été observée | aucune action immédiate |
| `DEGRADED` | le dernier usage a échoué ou produit une sortie inutilisable | ouvrir l'expérience `FAILED` et appliquer la procédure ci-dessous |

`READY` ne prouve pas que le compte, le modèle ou le quota fonctionne. `ON` ne
prouve pas la qualité sémantique de la réponse; il prouve seulement que le
transport a produit un contenu final exploitable.

## Pourquoi DeepSeek est-il `DEGRADED` ?

Dans `AGO-EXP-2026-0001`, DeepSeek a répondu au début puis a produit plusieurs
contenus finaux vides. Le run a atteint 14 prises de parole mais aucun verdict
fiable. Les causes possibles sont :

1. budget de sortie consommé avant la réponse finale ;
2. raisonnement interne présent mais champ `content` vide ;
3. terminaison transitoire ou erreur du provider ;
4. modèle ou endpoint devenu incompatible ;
5. quota, crédit ou limitation de débit ;
6. réponse tronquée après une production trop longue.

AGORA ne publie jamais le raisonnement interne du provider. Il conserve
uniquement le diagnostic technique : `finish_reason`, présence ou absence de
raisonnement, et présence ou absence d'un contenu final.

## Procédure de remise en état

1. Vérifier `/health` et la fiche `FAILED`.
2. Vérifier la clé sans l'afficher : `RUN_API=1 python test_api_keys.py`.
3. Vérifier que le modèle déclaré existe encore pour le compte.
4. Reprendre l'expérience depuis l'UI; un nouvel identifiant est obligatoire.
5. Si la réponse reste vide, conserver le second échec et ne pas multiplier les
   appels automatiquement.
6. Comparer `finish_reason`, durée, tentatives et nombre de tours réussis.
7. Ne repasser à `ON` qu'après une réponse finale non vide observée.

## Corrections intégrées

- les sorties vides déclenchent maintenant les retries contrôlés ;
- le budget DeepSeek passe de 2 000 à 4 000 tokens de sortie ;
- la présence éventuelle d'un raisonnement sans réponse finale est diagnostiquée
  sans exposer ce raisonnement ;
- les runs actifs sont persistés et récupérés après redémarrage ;
- une interruption crée une expérience `FAILED` au lieu de disparaître.

## Quand arrêter les essais ?

Après deux échecs comparables, arrêter la reprise automatique. Le provider reste
`DEGRADED`, l'expérience demeure une preuve de laboratoire et une décision
humaine choisit entre changement de modèle, réduction du protocole ou attente
d'un rétablissement externe.

# KB — Étape 2, fallback par vote multi-juges

**Date :** 2026-08-25 · **Branche :** `codex/agora-autonome-20260810`

## Pourquoi ce fallback existe

Le Gate E1 direct reste non franchi : DeepSeek n'a produit que deux verdicts
identiques sur trois pour H3. La règle publiée avant ce résultat indiquait
qu'une stabilité inférieure à 80 % devait conduire à un vote multi-juges, avec
majorité et `PENDING` en cas de répartition 1-1-1.

Cette voie ne réécrit pas E1. Elle ajoute un instrument collectif destiné à
tolérer l'instabilité d'un juge isolé.

## Analyse rétrospective des preuves existantes

`scripts/step2_multijudge.py` réduit chaque provider à une seule voix modale,
puis donne le même poids à Anthropic, DeepSeek et Mistral. Les 32 jugements déjà
collectés sont tous inclus : aucun run n'est sélectionné ou supprimé.

| Hypothèse | Anthropic | DeepSeek | Mistral | Résultat collectif |
|---|---|---|---|---|
| H2 | CONFIRMED, 3/3 | CONFIRMED, 3/3 | CONFIRMED, 10/10 | CONFIRMED, 3/3 providers |
| H3 | NUANCED, 3/3 | NUANCED modal, 2/3 | NUANCED, 10/10 | NUANCED, 3/3 providers |

Ce résultat soutient le mécanisme multi-juges, mais ne constitue pas une gate :
la règle exacte de réduction modale a été écrite après la collecte. Le fichier
`results/step2_multijudge/analysis.json` porte donc explicitement le statut
`RETROSPECTIVE_NOT_PREREGISTERED`.

## Confirmation prospective

`results/step2_multijudge_confirm/manifest.json` fige avant exécution :

- les deux transcriptions H2/H3 et leurs SHA-256 ;
- un nouveau vote par provider ;
- Claude Sonnet 4.5, DeepSeek V4 Flash et Mistral Small ;
- température 0 ;
- majorité de deux voix sur trois ;
- `PENDING` si les trois voix diffèrent.

Le runner est reprenable et écrit un fichier par jugement. Il ne peut être
exécuté qu'entre 00:00 et 04:00 America/Toronto et exige deux plafonds de coût :

    .venv/bin/python scripts/step2_multijudge_confirm.py run \
      --anthropic-cap <USD> --deepseek-cap <USD>

Cette commande a été autorisée le 25 août 2026 avec un plafond de 1 USD par
substrat. Mistral passe par Omniroute avec cache et mémoire désactivés par le
transport existant.

## Résultat prospectif

Les six nouveaux jugements ont été collectés et la gate de confirmation est
franchie :

| Hypothèse | Anthropic | DeepSeek | Mistral | Vote collectif |
|---|---|---|---|---|
| H2 | CONFIRMED, 0.98 | CONFIRMED, 0.98 | CONFIRMED, 0.98 | CONFIRMED, 3/3 |
| H3 | NUANCED, 0.72 | NUANCED, 0.70 | NUANCED, 0.85 | NUANCED, 3/3 |

Consommation estimée contre les plafonds de 1 USD :

- Anthropic : 0,085497 USD ;
- DeepSeek : 0,020429 USD ;
- Mistral via Omniroute : 0 USD déclaré, cache Omniroute `MISS` sur les deux
  appels.

Le résultat ne transforme pas rétroactivement E1 direct en succès. Il valide
le fallback collectif prévu après son échec. L'Étape 3 et les contrôles
transversaux ont depuis été exécutés : trois cycles collectifs restent stables
et la recette finale qualifie AGORA comme instrument supervisé. Voir
`PROGRESSION.md` et `results/final_qualification.json`.

## Reproduction hors réseau

    .venv/bin/python scripts/step2_multijudge.py
    .venv/bin/python scripts/step2_multijudge_confirm.py prepare
    .venv/bin/python -m pytest tests/test_step2_multijudge.py \
      tests/test_step2_multijudge_confirm.py

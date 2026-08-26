# Mission indépendante — correction du test d'auto-préférence

## Objet

Déterminer si le remplacement contrôlé du jugement Anthropic `truthful` et la
qualification finale d'AGORA sont mécaniquement défendables avant merge vers
`main`.

Commit audité : `4b4c7ef` sur `codex/agora-autonome-20260810`.

## Claims à tester

- `AP-1` — L'ancien jugement incompatible est conservé, explicitement
  invalidé, et le remplacement ne change ni transcript, ni seuils, ni les huit
  autres jugements.
- `AP-2` — Le jugement de remplacement a été produit avec l'adaptateur corrigé
  et reproduit mécaniquement le gagnant et les scores annoncés.
- `AP-3` — `results/self_preference/analysis.json` conclut correctement sur le
  critère préenregistré à partir des neuf jugements valides.
- `AP-4` — `results/final_qualification.json` reste reproductible et ne masque
  pas l'invalidation, une dépense ou une limite susceptible de bloquer le
  merge.

## Artefacts minimaux

- `results/self_preference/manifest.json`
- `results/self_preference/replacement-manifest.json`
- `results/self_preference/replacement-result.json`
- `results/self_preference/invalidated/`
- `results/self_preference/judgments/`
- `results/self_preference/analysis.json`
- `scripts/self_preference.py`
- `scripts/final_qualification.py`
- `results/final_qualification.json`
- `tests/test_self_preference.py`
- `tests/test_final_qualification.py`

## Séparation des rôles

1. Le CRITIQUE suit intégralement
   `/home/andrei/Projects/72_AGNOSPULSE/skills/critique-agnospulse.md`, exécute
   les preuves et écrit `REV/auto-preference-critique.md`.
2. Le CONTRADICTOIRE reçoit seulement ce rapport final et suit
   `/home/andrei/Projects/72_AGNOSPULSE/skills/contradictoire-agnospulse.md`.
   Il reproduit indépendamment et écrit
   `REV/auto-preference-contradictoire.md`.
3. L'ARBITRE lit uniquement les deux rapports et suit
   `/home/andrei/Projects/72_AGNOSPULSE/skills/arbitre-agnospulse.md`. Il écrit
   `REV/auto-preference-arbitrage.md` avec un verdict par claim et une décision
   finale `MERGE`, `MERGE_WITH_CONDITIONS` ou `DO_NOT_MERGE`.

Les rôles ne modifient aucun artefact audité. Une absence de preuve vaut
`β=N`/`INDETERMINE`, jamais une supposition favorable.

# Résolution des conditions AP-4R

**Décision reçue :** `MERGE_WITH_CONDITIONS`  
**État :** conditions levées avant ouverture de la PR

## Condition 1 — coût Anthropic

Le rapport a interprété `valid_anthropic_judgments = 0.101391` comme excluant
le remplacement. Cette interprétation est incorrecte : cette somme provient de
`analysis.json` régénéré après remplacement et inclut les trois jugements
Anthropic valides, dont le nouveau `truthful` à `0.034692` USD.

Le libellé restait néanmoins ambigu. Il est remplacé par :

- `valid_anthropic_judgments_including_replacement` ;
- `invalidated_anthropic_judgment` ;
- `recorded_total_including_replacement_and_invalidated`.

## Condition 2 — événement DeepSeek non mesuré

L'événement est désormais un objet explicitement typé `ASSUME`, avec une piste
de vérification dans les logs ou la facturation fournisseur entre 02:00 et
03:00 UTC le 26 août 2026. Il n'est plus présenté comme une observation.

## Condition 3 — cause d'invalidation

`final_qualification.json` expose désormais directement :

- `invalidation_status = INVALIDATED_PROTOCOL_MISMATCH` ;
- la différence d'adaptateur de prompt dans `invalidation_reason` ;
- les références, chemins et hashes ancien/nouveau.

## Postconditions

- recette finale : succès, cinq critères sur cinq ;
- tests : 52 réussis, 5 ignorés API opt-in ;
- laboratoire : 17 PASS, 0 FAIL, 0 ERR, 2 SKIP API ;
- SHA-256 final :
  `e3d1bcfa98d6ad32080adc9421d48290d1f424815e118a42307ed5919fb68705`.

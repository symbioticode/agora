# ARBITRE AP-4R — Arbitrage

**Rôle** : ARBITRE uniquement (skill `arbitre-agnospulse`). Aucune commande
exécutée, aucune preuve nouvelle produite. Jugement exclusif sur
`ap4r-critique.md` (CRITIQUE, F1–F5 PASS + 3 transmissions) et
`ap4r-contradictoire.md` (CONTRADICTOIRE, F1–F5 AGREE + 3 DIVERGE).

**Claim audité unique** : AP-4R (REV/MISSION-AP4-RECHECK.md).
F1–F5 : reproductibilité, exposition invalidation+hashes, coûts,
événement non mesuré, limites — tous PASS/AGREE. Aucun β=N.

---

## Arbitrage des DIVERGE

### DIVERGE 1 — Composition du coût « combined » (label ambigu)

```
claim_id  : AP-4R — coût « combined »
verdict   : INDETERMINE (sur le point de défaut) / non-bloquant sur F3
fondement : CRITIQUE (transmission 1) et CONTRADICTOIRE (point 1) exposent
            EXACTEMENT la même arithmétique :
              combined = 0.101391 + 0.036213 = 0.137604,
              exclusion de replacement.estimated_cost_usd = 0.034692.
            Aucune des deux parties ne conteste le calcul de l'autre :
            c'est une observation partagée, non une preuve contradictoire.
si escalade : aucune — pas de preuve supérieure d'un côté ; le fait
            (label « combined » ne couvre pas le coût de remplacement) est
            reconnu par les deux rôles. Reste une ambiguïté de libellé.
```

Pas de preuve supérieure → pas de tranchement en faveur d'un côté. La
constatation factuelle (coûts enregistrés, F3) reste CONFORME. Le libellé
ambigu est une réserve de transparence, pas une erreur prouvée.

### DIVERGE 2 — Provenance de l'événement non mesuré (OBSERVE vs ASSUME)

```
claim_id  : AP-4R — événement non mesuré
verdict   : INDETERMINE (sur la réalité de l'appel) / F4 CONFORME sur la présence
fondement : CRITIQUE F4 (PASS) affirme l'exposition du champ, non l'occurrence
            de l'appel ; sa transmission 2 classe explicitement le fait comme
            ASSUME. CONTRADICTOIRE (point 2) confirme la présence du champ
            (AGREE) et classe l'occurrence comme ASSUME. Les deux rôles
            s'accordent donc : champ présent (observable) + occurrence non
            attestée (ASSUME). Il n'y a pas de contradiction de preuve.
si escalade : aucune — le DIVERGE est une reformulation, pas un conflit de
            preuve. L'occurrence reste ASSUME (vérification fournisseur
            requise, hors périmètre de l'ARBITRE).
```

Pas de preuve supérieure → pas de tranchement. F4 (exposition du champ) est
CONFORME. La nature ASSUME de l'occurrence est commune aux deux rôles.

### DIVERGE 3 — Cause d'invalidation à saut de référence

```
claim_id  : AP-4R — exposition cause d'invalidation
verdict   : INDETERMINE (sur la suffisance de l'exposition indirecte)
fondement : CRITIQUE et CONTRADICTOIRE s'accordent sur le FAIT : la cause
            (INVALIDATED_PROTOCOL_MISMATCH) n'est PAS dans
            final_qualification.json ; elle est dans replacement-manifest.json,
            atteignable via la référence « manifest » incluse dans le bloc
            evidence_corrections[0]. Le claim littéral (« expose directement
            l'invalidation, les hashes ancien/nouveau ») porte sur le fait
            d'invalidation et les hashes — tous deux directement exposés
            (F2 PASS/AGREE, non contesté). Le DIVERGE porte sur la
            SUFFISANCE d'exposer la cause indirectement. Aucune preuve
            factuelle ne départage « indirect acceptable » vs « doit être
            joint » : l'état des artefacts est identique pour les deux rôles.
si escalade : aucune preuve supérieure disponible ; le litige est
            normatif (exhaustivité de l'exposition), pas factuel.
```

Pas de preuve supérieure → pas de tranchement. F2 (invalidation + hashes
directs) reste CONFORME. La cause indirecte est constatée par les deux rôles.

---

## Synthèse des verdicts par claim

| Sous-claim | CRITIQUE | CONTRADICTOIRE | Verdict ARBITRE |
|---|---|---|---|
| F1 reproductibilité | PASS | AGREE | CONFORME |
| F2 invalidation+hashes | PASS | AGREE | CONFORME |
| F3 coûts enregistrés | PASS | AGREE | CONFORME |
| F4 événement non mesuré | PASS | AGREE | CONFORME |
| F5 limites | PASS | AGREE | CONFORME |

Aucun DIVERGE ne renverse un verdict CONFORME : les trois points contestés
sont des réserves d'interprétation/transparence portant sur des éléments
hors du littéral des claims (libellé, occurrence ASSUME, cause indirecte),
et sur lesquels les deux rôles partagent les mêmes faits — donc aucune
preuve du dossier n'est supérieure à l'autre.

---

## Décision de merge

```
decision : MERGE_WITH_CONDITIONS
```

**Justification** : Le claim AP-4R est intégralement CONFORME et reproduit
indépendamment (F1–F5). Les trois DIVERGE n'opposent aucune preuve
supérieure ; ils documentent des limites déjà reconnues par les deux rôles.
Le commit `14ca9b2` peut être fusionné, sous réserve des conditions
ci-dessous (transparence, non bloquantes) :

**Conditions**
1. Clarifier le libellé `combined` dans `evidence_corrections[0].recorded_cost_usd`
   (ex. `valid_plus_invalidated_excl_replacement`) pour ne pas suggérer un
   total Anthropic.
2. Conserver la mention ASSUME sur l'événement non mesuré DeepSeek et, si
   souhaité, y référencer la piste de vérification fournisseur (logs /
   facturation ~2026-08-26 02:00–03:00 UTC).
3. Rendre la cause d'invalidation (`INVALIDATED_PROTOCOL_MISMATCH`) soit
   inline dans `final_qualification.json`, soit explicitement liée au bloc
   `REPLACEMENT_COMPLETED` via le champ `manifest` déjà présent, afin que
   l'exposition soit autonome.

**Hors périmètre de l'ARBITRE** : la correction des conditions ci-dessus et
la vérification fournisseur relèvent du système audité, non du verdict.

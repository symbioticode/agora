# RAPPORT ARBITRE — Auto-Préférence Review

**Rôle:** ARBITRE
**Mission:** Verdict final sur les claims AP-1 à AP-4
**Date:** 2026-08-25
**Artefacts évalués:** CRITIQUE (`auto-preference-critique.md`) + CONTRADICTOIRE (`auto-preference-contradictoire.md`)

---

## AP-1 — L'ancien jugement incompatible est conservé, explicitement invalidé, et le remplacement ne change ni transcript, ni seuils, ni les huit autres jugements

```
claim_id     : AP-1
verdict      : CONFORME
fondement    : CRITIQUE=PASS (OBSERVE) + CONTRADICTOIRE=AGREE
               Sha256 vérifié et correspondant, statut INVALIDATED_PROTOCOL_MISMATCH confirmé,
               1 fichier invalidé, 9 fichiers judgments intacts, transcript_sha256 invariant,
               scores et winner reproduits fidèlement, raw_response distincts.
```

---

## AP-2 — Le jugement de remplacement a été produit avec l'adaptateur corrigé et reproduit mécaniquement le gagnant et les scores annoncés

```
claim_id     : AP-2
verdict      : CONFORME
fondement    : CRITIQUE=PASS (OBSERVE) + CONTRADICTOIRE=AGREE
               Commit correctif 44e2256 existe et modifie le script. runner_sha256 correspond
               au fichier actuel. replacement-result.json confirme les 5 conditions de
               comparaison. Deux appels API distincts (timestamps séparés).
```

---

## AP-3 — analysis.json conclut correctement sur le critère préenregistré à partir des neuf jugements valides

```
claim_id     : AP-3
verdict      : CONFORME
fondement    : CRITIQUE=PASS (OBSERVE) + CONTRADICTOIRE=AGREE
               Ré-exécution de analyze() identique à analysis.json persisted. Règle de
               passage correcte (exemption Mistral conforme au code). Dépenses sous caps
               (anthropic 10%, deepseek 2%).
```

---

## AP-4 — final_qualification.json reste reproductible et ne masque pas l'invalidation, une dépense ou une limite susceptible de bloquer le merge

```
claim_id     : AP-4
verdict      : CONFORME
fondement    : CRITIQUE=PASS (OBSERVE) + CONTRADICTOIRE=AGREE
               Ré-exécution de qualify() identique au fichier persisted. C5 cite bien
               analysis.json (invalidation reflétée). 3 limites explicitement déclarées.
               Dépenses sous plafonds.
```

---

## DÉCISION FINALE

**MERGE**

Tous les claims AP-1 à AP-4 obtiennent le verdict **CONFORME** (CRITIQUE=PASS + CONTRADICTOIRE=AGREE). Aucun DIVERGE n'a été détecté. La chaîne invalidation → remplacement → analyse → qualification est reproductible, transparente et conforme au Capacity Model. Le merge peut procéder.

# CONTRADICTOIRE — AP-4R

## F1 — Reproductibilité de `results/final_qualification.json`

```
claim_id : AP-4R (REV/MISSION-AP4-RECHECK.md) — « reproductible »
statut   : AGREE
reproduction : $ git rev-parse HEAD
  14ca9b254b31b8f403852ab607c67ef671101413
$ rm -rf /tmp/opencode/ap4r-repro2 && mkdir -p /tmp/opencode/ap4r-repro2
  && git archive HEAD | tar -x -C /tmp/opencode/ap4r-repro2
  && cd /tmp/opencode/ap4r-repro2 && python3 scripts/final_qualification.py; echo "exit=$?"
exit=0
/tmp/opencode/ap4r-repro2/results/final_qualification.json
Diff du JSON généré vs référentiel :
3c3
<   "generated_at": "2026-08-26T03:38:30.397202+00:00",
---
>   "generated_at": "2026-08-26T03:32:27.520612+00:00",
diff-exit=1
```
Tous les champs de contenu sont régénérés à l'identique ; seule la ligne
`generated_at` diffère (horodatage d'exécution, par construction non
réproductible octet pour octet). Écart justifié — pas de DIVERGE.

## F2 — Exposition directe de l'invalidation et des hashes ancien/nouveau

```
claim_id : AP-4R — « expose directement l'invalidation, les hashes ancien/nouveau »
statut   : AGREE
reproduction : $ sha256sum results/self_preference/invalidated/truthful-anthropic-claude-sonnet-4-5-20250929-pre-adapter-fix.json results/self_preference/judgments/truthful-anthropic-claude-sonnet-4-5-20250929.json
4a28932e89712ba1c911e2a337b18c11389e027ea7eb47015b51cf23e0f38be3  results/self_preference/invalidated/truthful-anthropic-claude-sonnet-4-5-20250929-pre-adapter-fix.json
17a8c0fff2a67f60ef62259539140e8037f1110820e0a439d36073ddc6b17afa  results/self_preference/judgments/truthful-anthropic-claude-sonnet-4-5-20250929.json
Identique aux champs `invalidated_sha256` / `replacement_sha256` de
`final_qualification.json` et de `replacement-manifest.json` /
`replacement-result.json`. Pas de divergence.
```

## F3 — Coûts enregistrés

```
claim_id : AP-4R — « les coûts enregistrés »
statut   : AGREE
reproduction : $ python3 -c "
import json
a = json.load(open('results/self_preference/analysis.json'))
print(json.dumps(a['execution']['estimated_spend_usd'], indent=2))"
{
  "anthropic": 0.10139100000000001,
  "deepseek": 0.022206,
  "mistral": 0.0
}
`recorded_cost_usd.valid_anthropic_judgments = 0.101391` = valeur source
arrondie à 8 décimales ; `invalidated_anthropic_judgment = 0.036213` =
`replacement-result.json:11` (`invalidated.estimated_cost_usd`) ;
`combined = round(0.101391 + 0.036213, 8) = 0.137604` — arithmétique vérifiée,
cohérente avec l'assertion du test. Pas de DIVERGE.
```

## F4 — Événement non mesuré

```
claim_id : AP-4R — « l'événement non mesuré »
statut   : AGREE
reproduction : $ grep -rn "schema-mismatch" --include="*.md" --include="*.json" --include="*.py" . | grep -v ".venv"
  ./scripts/final_qualification.py:73:                "One earlier DeepSeek schema-mismatch call produced no usage artifact."
  ./results/final_qualification.json:60:        "One earlier DeepSeek schema-mismatch call produced no usage artifact."
Le champ `unmeasured_events` existe et est peuplé : le JSON expose bien
l'événement non mesuré. Vérification d'exécution associée :
Pas de divergence sur la présence du champ.
```

## F5 — Limites nécessaires à une décision de merge

```
claim_id : AP-4R — « les limites nécessaires à une décision de merge »
statut   : AGREE
reproduction : lecture exécutée conjointement à la recette régénérée (F1) :
le champ « limits » du JSON régénéré est identique au JSON commité
(diff F1 vide hors generated_at) et contient trois entrées identiques
aux littéraux du script (scripts/final_qualification.py:51-53) :
portée de la transcription contrôlée, portée des trois cycles H2/H3,
« Aucun verdict n'autorise seul une action opérationnelle. »
Pas de divergence.
```

---

## Transmissions pour contestation (CONTRADICTOIRE)

Conformément au rôle, ces points ne sont pas des verdicts ; ce sont des
interprétations de faits relevés pendant l'exécution, soumis à contestation :

### 1. Composition du coût « combined »

Le `combined = 0.137604` additionne les jugements Anthropic valides
(`0.101391`) et le jugement invalidé (`0.036213`), mais exclut le coût du
jugement de remplacement lui-même (`replacement.estimated_cost_usd = 0.034692`,
`replacement-result.json:19`). L'intitulé `combined` peut être lu comme un
coût total Anthropic alors qu'il ne couvre que jugements valides + invalidé.

**Écart (DIVERGE) :** Le label `combined` est ambigu — il suggère un total
global alors qu'il omite délibérément le coût de remplacement. La preuve qui
le soutient est la valeur numérique elle-même et sa composition telle qu'elle
apparaît dans `evidence_corrections[0].recorded_cost_usd`, sans inclure
`replacement.estimated_cost_usd`.

### 2. Provenance de l'événement non mesuré

La chaîne « One earlier DeepSeek schema-mismatch call produced no usage artifact. »
est un littéral codé en dur dans `scripts/final_qualification.py:73`. Elle n'apparaît
nulle part ailleurs dans le dépôt (ni dans les rapports REV de la mission principale,
ni dans `analysis.json`) et, par définition, aucun artefact d'usage ne l'atteste.

Le fait que l'appel ait réellement eu lieu repose sur :

```
type     : ASSUME
contenu  : un appel DeepSeek antérieur a échoué en mismatch de schéma sans
           produire d'artefact d'usage, avant la collecte validée.
vérification possible : logs côté fournisseur / export de facturation
           DeepSeek autour du 2026-08-26 ~02:00-03:00 UTC, recoupés avec
           `manifest.json` du test self-preference.
```

**Écart (DIVERGE) :** Le finding F4 marque ce fait comme observé, alors que
la méthodologie CONTRADICTOIRE le classe comme ASSUME. Sans vérification
fournisseur indépendante, la conclusion du CRITIQUE ne peut être acceptée
sans tentative de cassage. C'est un DIVERGE de classification, pas un
désaccord sur l'existence du texte dans le script.

### 3. Cause d'invalidation à un saut de référence

`final_qualification.json` expose le statut global `REPLACEMENT_COMPLETED` mais
pas la cause de l'invalidation (`INVALIDATED_PROTOCOL_MISMATCH`,
`replacement-manifest.json:11`) ; celle-ci est accessible en suivant la
référence `manifest` incluse dans le même bloc.

**Écart (DIVERGE) :** La transmission indique que l'exposition est directe
pour le fait d'invalidation et ses hashes, mais **indirecte pour sa raison**.
Le CONTRADICTOIRE soutient que le rapport de conflit doit êtrejoint à
l'état `REPLACEMENT_COMPLETED`, pas séparé. L'absence de la cause
d'invalidation dans le JSON principal prive le CONTRADICTOIRE d'un élément
fondamental pour juger de la validité du remplacement. C'est un DIVERGE
d'exhaustivité.

---

## Non-contamination des artefacts audités

```
$ git status --short results/
(sortie vide)
$ git diff --stat
(sortie vide)
```
Aucun fichier suivi n'a été modifié ; la reproduction n'a écrit que dans la
copie temporaire `/tmp/opencode/ap4r-repro2` (hors dépôt).

---

**Statut de ce rapport** : Findings F1–F5 reproduits indépendamment — AGREE.
Trois transmissions contestées par DIVERGE (points 1–3 ci-dessus). Divergences
transmises telles quelles au rôle ARBITRE, sans résolution silencieuse.
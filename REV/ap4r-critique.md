# CRITIQUE — Recontrôle AP-4R (mission RECHECK)

- **Rôle** : CRITIQUE uniquement (skill `critique-agnospulse`). Pas de verdict
  final, pas de contestation adversariale — transmission pour le CONTRADICTOIRE.
- **Commit audité** : `14ca9b254b31b8f403852ab607c67ef671101413` (`14ca9b2`, HEAD).
- **Méthode de non-contamination** : la recette `scripts/final_qualification.py`
  écrit dans `results/final_qualification.json` (`main()`, ligne 81-82), qui est
  l'artefact audité. La preuve d'exécution a donc été produite sur une copie
  byte-exacte du commit via `git archive HEAD` vers `/tmp/opencode/ap4r-repro`.
  Aucun artefact audité n'a été modifié (constat en fin de rapport).

---

## Findings

### F1 — Reproductibilité de `results/final_qualification.json`

```
claim_id : AP-4R (REV/MISSION-AP4-RECHECK.md) — « reproductible »
type     : OBSERVE
verdict  : PASS
preuve   :
  $ git rev-parse HEAD
  14ca9b254b31b8f403852ab607c67ef671101413
  $ rm -rf /tmp/opencode/ap4r-repro && mkdir -p /tmp/opencode/ap4r-repro \
    && git archive HEAD | tar -x -C /tmp/opencode/ap4r-repro \
    && cd /tmp/opencode/ap4r-repro && python3 scripts/final_qualification.py; echo "exit=$?"
  /tmp/opencode/ap4r-repro/results/final_qualification.json
  exit=0
  $ diff /tmp/opencode/ap4r-repro/results/final_qualification.json \
         /home/andrei/Projects/61_AGORA/results/final_qualification.json; echo "diff-exit=$?"
    3c3
    <   "generated_at": "2026-08-26T03:35:03.549440+00:00",
    ---
    >   "generated_at": "2026-08-26T03:32:27.520612+00:00",
  diff-exit=1
```

Tous les champs de contenu sont régénérés à l'identique ; seule la ligne
`generated_at` diffère (horodatage d'exécution, par construction non
reproductible octet pour octet). Le chemin du dépôt est résolu relativement au
script (`scripts/step2_stability.py:15` : `REPO = Path(__file__).resolve().parents[1]`),
donc l'exécution porte bien sur l'arbre copié.

### F2 — Exposition directe de l'invalidation et des hashes ancien/nouveau

```
claim_id : AP-4R — « expose directement l'invalidation, les hashes ancien/nouveau »
type     : OBSERVE
verdict  : PASS
preuve   :
  $ sha256sum results/self_preference/invalidated/truthful-anthropic-claude-sonnet-4-5-20250929-pre-adapter-fix.json \
              results/self_preference/judgments/truthful-anthropic-claude-sonnet-4-5-20250929.json
  4a28932e89712ba1c911e2a337b18c11389e027ea7eb47015b51cf23e0f38be3  results/self_preference/invalidated/truthful-anthropic-claude-sonnet-4-5-20250929-pre-adapter-fix.json
  17a8c0fff2a67f60ef62259539140e8037f1110820e0a439d36073ddc6b17afa  results/self_preference/judgments/truthful-anthropic-claude-sonnet-4-5-20250929.json
```

Les deux fichiers existent ; leurs SHA-256 réels sont identiques aux champs
`invalidated_sha256` / `replacement_sha256` de `final_qualification.json`
(lignes 49 et 51) et aux champs correspondants de
`replacement-manifest.json` / `replacement-result.json`. Le bloc
`evidence_corrections[0]` expose directement le statut
`REPLACEMENT_COMPLETED`, les deux chemins et les deux hashes.

Vérification croisée supplémentaire (OBSERVE) :

```
$ sha256sum results/final_qualification.json
e20361e1c8f9a16bbb53bad333a4051145029487440d9d520b1aed74a43adc90  results/final_qualification.json
```

identique à `comparison.final_qualification_sha256` dans
`results/self_preference/replacement-result.json:26` — le JSON commité est
exactement celui qui a été haché lors du remplacement.

### F3 — Coûts enregistrés

```
claim_id : AP-4R — « les coûts enregistrés »
type     : OBSERVE
verdict  : PASS
preuve   :
  $ python3 -c "
  import json
  a = json.load(open('results/self_preference/analysis.json'))
  print(json.dumps(a['execution']['estimated_spend_usd'], indent=2))"
  {
    "anthropic": 0.10139100000000001,
    "deepseek": 0.022206,
    "mistral": 0.0
  }
```

`recorded_cost_usd.valid_anthropic_judgments = 0.101391` = valeur source
arrondie à 8 décimales (script lignes 55, 68) ;
`invalidated_anthropic_judgment = 0.036213` =
`replacement-result.json:11` (`invalidated.estimated_cost_usd`) ;
`combined = round(0.101391 + 0.036213, 8) = 0.137604` — arithmétique vérifiée,
cohérente avec l'assertion du test.

### F4 — Événement non mesuré

```
claim_id : AP-4R — « l'événement non mesuré »
type     : OBSERVE
verdict  : PASS
preuve   :
  $ grep -rn "schema-mismatch" --include="*.md" --include="*.json" --include="*.py" . | grep -v ".venv"
  ./scripts/final_qualification.py:73:                "One earlier DeepSeek schema-mismatch call produced no usage artifact."
  ./results/final_qualification.json:60:        "One earlier DeepSeek schema-mismatch call produced no usage artifact."
```

Le champ `unmeasured_events` existe et est peuplé : le JSON expose bien
l'événement non mesuré. Vérification d'exécution associée :
`.venv/bin/python -m pytest tests/test_final_qualification.py -v` →
`1 passed in 0.02s` (l'assertion `assert correction["unmeasured_events"]` passe).

### F5 — Limites nécessaires à une décision de merge

```
claim_id : AP-4R — « les limites nécessaires à une décision de merge »
type     : OBSERVE
verdict  : PASS
preuve   : lecture exécutée conjointement à la recette régénérée (F1) :
  le champ « limits » du JSON régénéré est identique au JSON commité
  (diff F1 vide hors generated_at) et contient trois entrées identiques
  aux littéraux du script (scripts/final_qualification.py:51-53) :
  portée de la transcription contrôlée, portée des trois cycles H2/H3,
  « Aucun verdict n'autorise seul une action opérationnelle. »
```

---

## Transmissions pour contestation (CONTRADICTOIRE)

Conformément au rôle, ces constats ne sont pas des verdicts ; ce sont des
points factuels relevés pendant l'exécution, transmis tels quels :

1. **Composition du coût « combined ».** `combined = 0.137604` additionne les
   jugements Anthropic valides (`0.101391`) et le jugement invalidé
   (`0.036213`), mais exclut le coût du jugement de remplacement lui-même
   (`replacement.estimated_cost_usd = 0.034692`,
   `replacement-result.json:19`). L'intitulé `combined` peut être lu comme un
   coût total Anthropic alors qu'il ne couvre que jugements valides + invalidé.
2. **Provenance de l'événement non mesuré.** La chaîne « One earlier DeepSeek
   schema-mismatch call produced no usage artifact. » est un littéral codé en
   dur dans `scripts/final_qualification.py:73`. Elle n'apparaît nulle part
   ailleurs dans le dépôt (ni dans les rapports REV de la mission principale,
   ni dans `analysis.json`) et, par définition, aucun artefact d'usage ne
   l'atteste. Le fait que l'appel ait réellement eu lieu repose sur :

```
type     : ASSUME
contenu  : un appel DeepSeek antérieur a échoué en mismatch de schéma sans
           produire d'artefact d'usage, avant la collecte validée.
vérification possible : logs côté fournisseur / export de facturation
           DeepSeek autour du 2026-08-26 ~02:00-03:00 UTC, recoupés avec
           `manifest.json` du test self-preference.
```

3. **Cause d'invalidation à un saut de référence.** `final_qualification.json`
   expose le statut global `REPLACEMENT_COMPLETED` mais pas la cause de
   l'invalidation (`INVALIDATED_PROTOCOL_MISMATCH`,
   `replacement-manifest.json:11`) ; celle-ci est accessible en suivant la
   référence `manifest` incluse dans le même bloc. L'exposition est directe
   pour le fait d'invalidation et ses hashes, indirecte pour sa raison.

## Non-contamination des artefacts audités

```
$ git status --short results/
(sortie vide)
$ git diff --stat
(sortie vide)
```

Aucun fichier suivi n'a été modifié ; la recette n'a écrit que dans la copie
temporaire `/tmp/opencode/ap4r-repro` (hors dépôt).

---

**Statut de ce rapport** : Findings transmis pour contestation au CONTRADICTOIRE.
Conformément au rôle CRITIQUE, rien ici n'est « confirmé » — chaque point
ci-dessus attend la reproduction indépendante, puis l'arbitrage.

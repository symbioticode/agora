# KB — AGORA Étape 2 : protocole de stabilité préparé hors-ligne

**Date de remise :** 2026-08-10

**Branche :** `codex/agora-autonome-20260810`

**Statut historique :** préparation du 10 août, désormais exécutée et
supplantée par `KB-ETAPE2-DIRECT-E1.md` puis
`KB-ETAPE2-VOTE-MULTIJUGES.md`. E1 direct a échoué; le fallback collectif
prospectif a été franchi le 25 août 2026.

## Résumé

À la date de remise, le prochain chantier documenté était l'Étape 2 : rejuger
plusieurs fois la même transcription à température 0 pour mesurer la stabilité
du verdict. La branche préparait ce protocole sans appel LLM et sans modifier
`orchestrator.py`.

Le travail ne prétend pas franchir E1. Il fige les entrées, rend les futures
sorties comparables et empêche trois erreurs : transcription différente entre
runs, répétition dupliquée et agrégation de juges différents sous un seul taux.

## Audit de départ

Trois écarts ont été trouvés :

1. `STATUS.md` et `HYPOTHESES.md` annonçaient H3 à 0/5, tandis que
   `PENDING.md` et deux sessions réelles prouvent 2/5. Les registres affichent
   maintenant 2/5, avec trois runs restants.
2. Le seuil E1 est ≥80 %, mais avec seulement trois répétitions les résultats
   possibles sont 0 %, 33,3 %, 66,7 % ou 100 %. En pratique, passer exige donc
   3/3 verdicts identiques.
3. Alterner les providers sur trois runs confond la stabilité temporelle et
   l'effet du juge. Le manifeste prévoit trois répétitions **par juge**, pour H2
   et H3 : 2 hypothèses × 2 juges × 3 répétitions = 12 jugements.

## Entrées figées

| ID | Session source | Tours | Empreinte transcript |
|---|---|---:|---|
| H2 | `sessions/20260716_121925.json` | 8 | `4da869af9d1b220d…` |
| H3 | `sessions/20260717_000603.json` | 8 | `a7f2acf4cb50a6b…` |

Les empreintes complètes et les SHA-256 des fichiers sources sont dans
`results/step2_manifest.json`. Toute sortie portant une autre empreinte est
refusée par l'analyseur.

## Usage sans API

```bash
python scripts/step2_stability.py prepare
python scripts/step2_stability.py analyze
```

`prepare` régénère le manifeste de manière déterministe. `analyze` lit les JSON
placés dans `results/step2_judgments/`, écrit `results/step2_analysis.json` et
retourne le code 2 tant que les 12 jugements ne sont pas complets et stables.

Contrat minimal d'un jugement :

```json
{
  "hypothesis_id": "H2",
  "judge": "anthropic:claude-sonnet-4-5",
  "repeat": 1,
  "transcript_sha256": "…",
  "verdict": "CONFIRMED",
  "confidence": 0.95
}
```

## Validation locale

- `pytest` : 20 tests réussis, 5 ignorés car API opt-in.
- `scripts/lab_check.py` : 17 PASS, 0 FAIL, 0 ERR, 2 SKIP API.
- Tests Étape 2 : manifeste sur deux sessions réelles; succès 3/3; échec 2/3
  sous seuil 80 %; rejet d'une empreinte altérée; rejet d'un repeat dupliqué.
- Analyse actuelle : 0/12 jugements, `gate_e1_passed=false`, exit 2 attendu.

### Garde-fou API ajouté

Le premier `pytest -q` de l'audit a auto-collecté `test_api_keys.py`, dont les
fonctions historiques effectuaient directement des pings Anthropic/DeepSeek.
Il a donc déclenché des **tentatives non intentionnelles** de connectivité; la
sortie pytest ne permet pas d'établir si un appel a été facturé. Le fichier est
désormais marqué `RUN_API=1` obligatoire et un run ordinaire les ignore. Ce
garde-fou empêche la récidive; aucun run de débat ni jugement E1 n'a été lancé.

## Ce qui restait à autoriser au 10 août 2026

1. Trois débats H3 complets pour clore l'Étape 1.
2. Douze jugements directs pour E1 selon le manifeste.
3. Le choix humain : conserver ce protocole 3× par juge, ou accepter un test
   moins discriminant de trois runs alternés.

Ces actions peuvent consommer des crédits directs Anthropic/DeepSeek. Elles ne
font pas partie du travail autonome sans confirmation d'Andrei.

## Verdict

À la date de remise, la branche avançait AGORA de façon vérifiable : les
données existantes étaient réconciliées et le protocole E1 était prêt,
déterministe et auditable. Pour l'état courant, consulter `STATUS.md` et
`KB-ETAPE2-VOTE-MULTIJUGES.md`.

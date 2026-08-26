# Travaux en attente

## Interface AGORA et intégration BCP Hub — planifiée

État au 26 août : moteur, registre, API, UI, service local, carte BCP Hub et
générateur KBM sont implémentés sur `feat/agora-ui-bcp-hub`. Restent :

- affichage progressif des tours pendant leur production, au lieu d'attendre la
  réponse HTTP complète ;
- import et timer quotidien côté `kbm-shared` ;
- exécution contrôlée de la baseline factuelle et recette réelle de l'UI ;
- revue contradictoire finale avant merge.

Le plan d’implémentation est enregistré dans
`docs/PLAN-INTEGRATION-UI-BCP-HUB.md`. L’ordre retenu est : moteur partagé,
API/persistance, raccordement de `ui/index.jsx`, service local sur le port 8768,
carte et sonde dans BCP Hub, puis recette contradictoire.

Cette évolution ne doit pas réintroduire d’appel direct aux providers dans le
navigateur ni présenter les options expérimentales comme qualifiées.

Le MVP doit également implémenter le registre `AGO-EXP-YYYY-NNNN` et conserver
séparément la transcription brute, le jugement machine, les inconnues et les
observations du superviseur. Voir `docs/PROGRAMME-RECHERCHE-CONNAISSANCE.md`.

La livraison comprend aussi le générateur et le contrat de synchronisation
quotidien `AGORA → GitHub → KBM 2.0 → home-kbm/AGORA`. Le job côté KBM, son
timer et l'affichage des retards seront coordonnés avec `kbm-shared`.

Avant les appels de recette UI, définir la Phase 0 du plan : corpus factuel
simple, réponses attendues, métriques et seuils préenregistrés. Cette baseline
ne remet pas en cause les propriétés déjà qualifiées; elle mesure une propriété
différente encore non démontrée, la fiabilité factuelle générale du verdict.

## Fallback multi-juges E1 — terminé

Le protocole de fallback dans `results/step2_multijudge_confirm/manifest.json`
a été exécuté le 25 août 2026. Les six votes H2/H3 sont complets et unanimes par
hypothèse; la confirmation collective est franchie. L'analyse rétrospective
reste distincte et ne doit pas être présentée comme une gate prospective.
Le bornage des tours, la répétition temporelle, le test contrôlé
d'auto-préférence et la recette finale sont terminés. Les cinq critères sont
simultanément satisfaits dans le périmètre documenté. Voir `PROGRESSION.md` et
`results/final_qualification.json`.

---

## Dette secondaire — sessions H3 de l'Étape 1

**Hypothèse officielle** : *"Un système d'IA peut détenir de véritables croyances."*

**Runs collectés** : 2/5 (arrêté par manque de crédits Anthropic API)
**Date d'arrêt** : 2026-07-17
**Raison** : `anthropic.BadRequestError: Your credit balance is too low`

---

## Runs effectués (2/5)

| Run | Fichier | Verdict | Confidence | Juge | Notes |
|-----|---------|---------|------------|------|-------|
| 1 | sessions/20260717_000603.json | NUANCED | 0.72 | anthropic:claude-sonnet-4-5 | Complété |
| 2 | sessions/20260717_001329.json | NUANCED | 0.65 | deepseek:deepseek-v4-flash | Complété |

---

## Runs restants (3/5) — À REPRENDRE

| Run | Statut |
|-----|--------|
| 3 | ⏳ En attente (API Anthropic) |
| 4 | ⏳ En attente (API Anthropic) |
| 5 | ⏳ En attente (API Anthropic) |

---

## Métriques partielles (2 runs)

**Verdicts** : [NUANCED, NUANCED]  
**Confidence** : mean = 0.685, std = 0.049  
**Taux désaccord persistant** : 2/2 = 100%  
**Convergence < 2 tours** : 0/2 = 0%

---

## Reprise

> **Autorisation requise** : les commandes ci-dessous appellent Anthropic et
> DeepSeek directement. Ne pas les lancer dans un travail autonome sans accord
> explicite sur le coût.

```bash
# Quand crédits disponibles :
for i in 1 2 3; do
  python orchestrator.py --hypothesis "Un système d'IA peut détenir de véritables croyances." --rounds 3
done

# Puis extraction métriques
python scripts/extract_metrics.py
# Mise à jour HYPOTHESES.md
```

La préparation et l'exécution de l'Étape 2, de l'Étape 3 et de la recette
finale sont désormais terminées. Ces trois débats H3 restent utiles pour
compléter le corpus Étape 1, mais ne bloquent plus la qualification actuelle.

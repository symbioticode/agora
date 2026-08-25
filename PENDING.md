# Sessions H3 en attente — Étape 1

## Priorité actuelle — confirmation multi-juges E1

Le protocole de fallback est préparé dans
`results/step2_multijudge_confirm/manifest.json`. Il manque six nouveaux votes
H2/H3 répartis entre Anthropic, DeepSeek et Mistral. Les appels directs restent
bloqués tant que leurs plafonds en USD ne sont pas explicitement autorisés.
L'analyse rétrospective favorable ne doit pas être présentée comme une gate
franchie. Voir `docs/KB-ETAPE2-VOTE-MULTIJUGES.md`.

---

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

La préparation hors-ligne de l'Étape 2 est disponible via
`python scripts/step2_stability.py prepare`; elle ne lève pas ce blocage et ne
constitue pas un résultat du Gate E1.

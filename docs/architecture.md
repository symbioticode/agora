# Architecture d'Agora

## Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATEUR                             │
│  (orchestrator.py ~90 lignes)                                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   ┌─────────┐        ┌─────────┐        ┌─────────┐
   │ Agent A │        │ Agent B │        │  Juge   │
   │(Claude) │        │(DeepSeek)│       │(Claude) │
   │Empiriste│        │Rational.│       │ Temp=0  │
   └────┬────┘        └────┬────┘        └────┬────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
                  ┌─────────────────┐
                  │   Session JSON  │
                  │  (sessions/)    │
                  └────────┬────────┘
                           ▼
                  ┌─────────────────┐
                  │   Verdict MD    │
                  │   (results/)    │
                  └─────────────────┘
```

## Flux de données

1. **Input** : Hypothèse (string) + Rounds (int, défaut=3)
2. **Tour 0 (Parallèle)** : Agent A et B répondent indépendamment
3. **Tours 1..N (Contradictoires)** : Chaque agent lit la réponse de l'autre, hypothèse ré-ancrée
4. **Juge** : Reçoit transcription complète, produit verdict JSON gradué
5. **Output** : Session JSON (sessions/) + Verdict affiché + Rapport MD (results/)

## Composants

### orchestrator.py
- Point d'entrée unique
- Gestion de l'historique et du ré-ancrage
- Appels API Anthropic (Claude) et OpenAI-compatible (DeepSeek)
- Parsing et validation du verdict JSON
- Persistance session

### mindsets/
- `empiricist.md` : System prompt Agent A (observation → hypothèse → test)
- `rationalist.md` : System prompt Agent B (axiomes → déduction → cohérence)
- Distincts (Jaccard < 0.70) — vérifié par `lab_check.py`

### scripts/
- `lab_status.sh` : Dashboard tracking (PCA-T) — "Où en est-on ?"
- `lab_check.py` : Vérification invariants (PCA-V) — "Est-ce correct ?"

### tests/
- `test_orchestrator.py` : Tests unitaires structurels (sans API)
- `test_three_hypotheses.py` : Tests d'intégration 3 hypothèses (avec API)

### docs/
- `architecture.md` : Ce fichier
- `pitfalls.md` : Pièges connus et contournements
- `research_notes.md` : Synthèse littérature (base décisions)
- `ti360_mapping.md` : Correspondance TI-360

## Conventions

- **Temperature** : 0.7 débat (exploration), 0.0 juge (déterminisme relatif)
- **Modèles** : `claude-sonnet-4-5` / `deepseek-v4-flash` (fixes dans orchestrator)
- **Ré-ancrage** : Hypothèse réinjectée à chaque tour (anti-drift)
- **Providers distincts** : Règle dure D-AGO-001

## Extensibilité

Nouveaux mindsets : ajouter `.md` dans `mindsets/` + mettre à jour `MINDSETS` dict.
Nouveaux juges : alterner `MODEL_JUDGE` entre Claude/DeepSeek (anti-biais).
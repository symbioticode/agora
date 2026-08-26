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

1. **Input** : Hypothèse (string) + Rounds (int, défaut=6)
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
- `step3_rounds.py` : bornage prospectif du nombre de tours
- `self_preference.py` : test d'étiquette vrai/masqué/permuté
- `temporal_stability.py` : trois cycles de vote collectif H2/H3
- `verdict_policy.py` : séparation verdict d'idée / autorisation d'action
- `final_qualification.py` : recette mécanique des cinq critères

### tests/
- `test_orchestrator.py` : Tests unitaires structurels (sans API)
- `test_three_hypotheses.py` : Tests d'intégration 3 hypothèses (avec API)

### docs/
- `architecture.md` : Ce fichier
- `pitfalls.md` : Pièges connus et contournements
- `research_notes.md` : Synthèse littérature (base décisions)
- `ti360_mapping.md` : Correspondance TI-360
- `KB-QUALIFICATION-FINALE.md` : recette, verdict et limites actuelles

## Conventions

- **Temperature** : 0.7 débat (exploration), 0.0 juge (déterminisme relatif)
- **Modèles** : `claude-sonnet-4-5` / `deepseek-v4-flash` (fixes dans orchestrator)
- **Ré-ancrage** : Hypothèse réinjectée à chaque tour (anti-drift)
- **Providers distincts** : Règle dure D-AGO-001
- **Autorisation** : un verdict qualifie une proposition; il ne donne jamais à
  lui seul la permission de l'exécuter

## Extensibilité

Nouveaux mindsets : ajouter `.md` dans `mindsets/` + mettre à jour `MINDSETS` dict.
Nouveaux juges : les évaluer par permutation d'identité et stabilité
temporelle avant de les intégrer au vote collectif. Mistral fournit aujourd'hui
la troisième voix via Omniroute; une voix par provider, majorité 2/3 et
`PENDING` en cas de répartition 1-1-1.

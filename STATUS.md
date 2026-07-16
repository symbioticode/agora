# Agora — Status du Laboratoire

## Stage : Étape 0 — Fondations (Jour 1)

**Objectif** : Repo GitHub + .env + orchestrator.py squelette + mindsets rédigés.

**Test de passage (gate E0)** :
```bash
python orchestrator.py \
  --hypothesis "L'eau pure bout à 100°C à pression standard." \
  --rounds 3
```

**Critères de succès** :
- [ ] JSON valide avec `verdict`, `confidence`, `agreement`, `disagreement`
- [ ] `verdict == "CONFIRMED"` et `confidence >= 0.85`
- [ ] Aucun désaccord fabriqué sur un fait physique établi
- [ ] Session exportée dans `sessions/`

**Ne pas avancer si** : le verdict sur l'hypothèse factuelle n'est pas CONFIRMED.

---

*Mis à jour automatiquement par `scripts/lab_status.sh`*
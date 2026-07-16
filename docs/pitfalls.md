# Pièges Connus — Agora

## 1. Chambre d'écho (D-AGO-001 violé)
**Symptôme** : Convergence rapide, désaccords vides, confidence artificiellement haute.
**Cause** : Même provider pour Agent A et B, ou mindsets trop similaires (Jaccard ≥ 0.70).
**Fix** : Providers distincts + mindsets épistémologiquement opposés.

## 2. Convergence forcée (Étape 1)
**Symptôme** : Hypothèse #2 (nuancée) → CONFIRMED en < 2 tours.
**Cause** : Mindsets pas assez fermes, agents "polites".
**Fix** : Durcir les mindsets → *"Tu DOIS maintenir ta position tant que l'adversaire n'a pas réfuté explicitement [critère X]."*

## 3. Drift de problème (Becker et al. EACL 2026)
**Symptôme** : Débat dérive vers méta-discussion, perd l'hypothèse originale.
**Cause** : Pas de ré-ancrage à chaque tour.
**Fix** : Ré-injecter l'hypothèse dans CHAQUE prompt utilisateur (non-négociable).

## 4. Biais d'auto-préférence du juge (Point ouvert #1)
**Symptôme** : Juge favorise l'agent de son propre provider.
**Test** : Étape 2 — même transcription, juge 3×, alterner providers.
**Seuil** : < 80% accord inter-runs → vote multi-juges (3 appels, majorité).

## 5. Déterminisme illusoire (Point ouvert #2)
**Symptôme** : temperature=0 ne garantit pas reproductibilité.
**Réalité** : Stabilité du verdict = objet de test, pas acquis.

## 6. Asymétrie coût/latence (Point ouvert #3)
**Symptôme** : Claude plus cher/plus lent que DeepSeek Flash → biais de verbosité.
**Observation** : Surveiller à l'Étape 1.

## 7. Parsing JSON verdict
**Symptôme** : Juge renvoie JSON invalide ou champs manquants.
**Fix** : Extraction robuste (chercher `{...}`), fallback parsing, validation stricte dans lab_check.py Section D.

## 8. Clés API commitées
**Symptôme** : .env dans git.
**Fix** : .env dans .gitignore (vérifié par lab_check.py Section A).

## 9. Requirements.txt vidé par merge
**Symptôme** : anthropic/openai disparaissent.
**Fix** : lab_check.py Section A check explicite.
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

## 4. Biais d'auto-préférence du juge
**Symptôme** : Juge favorise l'agent de son propre provider.
**Test actuel** : même contenu présenté avec identités vraies, masquées et
permutées; gagnant invariant et effet d'étiquette ≤5 points chez chaque juge
payant.
**Résultat 2026-08-25** : aucun effet chez Anthropic/DeepSeek; limite : une
seule transcription. Répéter le contrôle lors d'un changement de modèle ou de
domaine.

## 5. Déterminisme illusoire
**Symptôme** : temperature=0 ne garantit pas reproductibilité.
**Réalité** : stabilité du verdict = objet de test, pas acquis. Trois cycles
collectifs H2/H3 sont stables; cette preuve doit être renouvelée après tout
changement de modèle, prompt ou politique de vote.

## 6. Asymétrie coût/latence
**Symptôme** : Claude plus cher/plus lent que DeepSeek Flash → biais de verbosité.
**Observation** : les expériences enregistrent usage, coût estimé et latence;
le budget doit rester contrôlé par provider avant chaque appel.

## 7. Parsing JSON verdict
**Symptôme** : Juge renvoie JSON invalide ou champs manquants.
**Fix** : Extraction robuste (chercher `{...}`), fallback parsing, validation stricte dans lab_check.py Section D.

## 8. Clés API commitées
**Symptôme** : .env dans git.
**Fix** : .env dans .gitignore (vérifié par lab_check.py Section A).

## 9. Requirements.txt vidé par merge
**Symptôme** : anthropic/openai disparaissent.
**Fix** : lab_check.py Section A check explicite.

## 10. Encodage cp1252 vs UTF-8 sous Windows (3 occurrences le 2026-07-16)
**Symptôme** : `UnicodeEncodeError` sur `write_text()`, `print()`, ou `read_text()` avec caractères non-ASCII (ex: `→`, `₂`).
**Cause** : Python sous Windows utilise cp1252 par défaut au lieu d'UTF-8 pour les I/O texte.
**Fix** : TOUT `read_text()` / `write_text()` doit spécifier `encoding="utf-8"` explicitement. Pour `print()` sur stdout, ajouter `sys.stdout.reconfigure(encoding="utf-8")` en haut du fichier sous `if sys.platform == "win32"`.
**Non-régression** : check lab_check.py Section A vérifie l'absence d'I/O sans encoding.

## 11. sessions/ est éphémère — données perdues sans results/ (2026-07-16)
**Symptôme** : données de session (disagreement[], rounds, transcripts) inaccessibles après changement d'environnement.
**Cause** : sessions/ est gitignored par design (données volumineuses, clés potentielles). Un changement de machine, de workspace ou de session Claude efface tout.
**Règle** : toute donnée destinée à survivre à un changement d'environnement doit être résumée dans results/YYYYMMDD_<slug>.md au moment du run, pas après coup. Le format results/ doit inclure : hypothèse, verdicts, disagreement[] complets, configuration (modèles, rounds).
**Leçon** : 15 sessions H2/H3/H4 perdues — seuls verdict/confidence agrégés restent dans HYPOTHESES.md, pas les données brutes.

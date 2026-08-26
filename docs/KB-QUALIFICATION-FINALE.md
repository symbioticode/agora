# KB — Qualification finale d'AGORA

**Date :** 2026-08-25 · **Statut historique :** recette franchie

> Mise à jour du 26 août : la configuration d'exécution courante est
> `REQUALIFICATION_REQUIRED`. La preuve ci-dessous reste valable pour le
> protocole et les artefacts testés le 25 août; elle ne démontrait pas la
> disponibilité bout en bout du débat. Le réglage DeepSeek et les gates de
> transport ayant changé, une recette proportionnée doit précéder le retour au
> mode de recherche supervisée.

## Verdict

Les cinq critères définis pour la configuration actuelle sont simultanément
satisfaits. AGORA peut servir d'instrument de recherche supervisé. Cette
qualification porte sur la qualité et la stabilité du jugement; elle ne donne
aucune autonomie opérationnelle aux agents.

| Critère | Résultat | Preuve |
|---|---|---|
| Ne pas converger artificiellement | Satisfait | H2/H4 : désaccord persistant 100 %, aucune convergence en moins de deux tours |
| Reconnaître un fait solide | Satisfait | H2 : `CONFIRMED`, unanimité 3/3 providers |
| Conserver l'incertitude | Satisfait | H3 : `NUANCED`; toute action associée reste bloquée sans approbation humaine |
| Stabilité temporelle | Satisfait | Trois cycles H2/H3, mêmes verdicts collectifs, 18/18 jugements |
| Absence d'auto-préférence détectable | Satisfait dans le test contrôlé | Anthropic/DeepSeek : effet d'étiquette 0 point, gagnant invariant |

## Architecture de preuve

1. Les manifestes ont été commités avant les appels dans `04dbd36`.
2. Les identités du débat H3 ont été présentées vraies, masquées puis
   permutées sans changer le contenu.
3. Le vote collectif H2/H3 a été répété pendant trois cycles, avec une voix par
   provider.
4. `scripts/final_qualification.py` relit les preuves et vérifie les cinq
   critères dans une seule recette.
5. Le résultat consolidé est `results/final_qualification.json`.

Une revue préalable au merge a détecté une différence de prompt système dans
le premier appel Anthropic `truthful`. L'artefact a été invalidé sans être
effacé, puis remplacé sous manifeste préenregistré avec l'adaptateur corrigé.
Le replay reproduit les scores `72/78` et le gagnant B. Voir
`results/self_preference/replacement-result.json`.

Commande de reproduction hors réseau :

    .venv/bin/python scripts/final_qualification.py

## Contrat d'action

- `PENDING` bloque toujours une action.
- `NUANCED` est consultatif sans action; avec action, il exige une approbation
  humaine.
- `REJECTED` bloque l'action proposée.
- `CONFIRMED` ne vaut pas permission : capacités, limites et postconditions
  restent obligatoires.

AGORA juge donc une proposition; l'autorité humaine et les mécanismes du
système décident séparément si une action est permise.

## Limites

- Le test d'auto-préférence porte sur une seule transcription H3.
- La stabilité temporelle porte sur trois cycles de H2/H3 à température 0.
- Mistral conserve le gagnant dans le test d'étiquette, mais ses scores varient
  de 7 points; ce témoin gratuit était hors du seuil préenregistré.
- `DEFAULT_ROUNDS=6` est la borne haute testée, pas un optimum universel.
- Dans le code historique, cette valeur signifie une position initiale puis six
  cycles de contradiction, soit quatorze prises de parole. Le libellé UI
  « six tours » était donc ambigu; cette sémantique doit être figée ou corrigée
  explicitement pendant la requalification, jamais silencieusement.
- E1 direct reste historiquement non franchi; la qualification repose sur le
  fallback collectif prévu après cet échec.
- Trois débats H3 de l'Étape 1 restent une dette secondaire non bloquante.

Tout changement de modèle, de prompt, de politique de vote ou de domaine
important doit déclencher une nouvelle calibration proportionnée au risque.

Cette règle s'applique désormais aussi à un réglage provider qui peut modifier
la sortie, comme `reasoning_effort`. Les sondes de transport ne sont jamais
comptées comme expériences ni comme preuves de qualité sémantique.

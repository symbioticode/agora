# Progression du projet AGORA

Ce journal décrit l'évolution durable d'AGORA. Il est distinct de `STATUS.md`,
qui reflète l'état courant du laboratoire et peut être régénéré à mesure que
les expériences évoluent. Omniroute ne faisait pas partie du plan initial;
son coût déclaré nul a permis de tester les transports, préparer le code et
ajouter un troisième regard sans remplacer les expériences directes prévues.

## 2026-08-25 — Qualification du couple d'agents après l'Étape 2

Le couple n'est pas encore qualifié comme instrument autonome de recherche.
Il est utilisable comme laboratoire supervisé.

| Critère de préparation | Qualification | Preuve actuelle |
|---|---|---|
| Ne pas converger artificiellement | **Satisfait** | Désaccord persistant 100 % sur H2/H4; aucune convergence en moins de deux tours |
| Reconnaître un fait solide | **Satisfait** | H2 donne CONFIRMED à 0,98, unanimité Anthropic/DeepSeek/Mistral |
| Savoir conserver l'incertitude | **Satisfait pour l'exploration, non qualifié pour l'action** | H3 donne NUANCED à 3/3 providers; aucune action n'était attachée au verdict |
| Stabilité du juge | **Partiel** | Anthropic et Mistral sont stables; DeepSeek direct donne seulement 2/3; le fallback collectif prospectif est unanime mais pas encore répété dans le temps |
| Absence d'auto-préférence | **Non démontré** | Le troisième provider réduit le risque sans mesurer directement la préférence pour les arguments de son propre provider |

### Contrat de décision

- `PENDING` signifie que le degré de confiance est insuffisant pour autoriser
  une action. Toute action associée est mécaniquement bloquée.
- `NUANCED` est acceptable pour juger ou explorer des idées lorsqu'aucune action
  opérationnelle n'est attachée au verdict.
- Si une action est attachée à une conclusion `NUANCED`, elle reste bloquée par
  défaut jusqu'à une décision humaine ou une preuve plus forte.
- `CONFIRMED` ne suffit pas seul à exécuter une action : les permissions,
  postconditions et limites propres à l'action restent applicables.

Cette règle remplace l'attente trop rigide « H3 doit nécessairement produire
PENDING ». Pour H3, `NUANCED` est cohérent parce que l'expérience juge une idée
et conserve explicitement les désaccords; elle n'autorise aucune action.

### Travaux pour atteindre cinq critères simultanément satisfaits

1. Borner les tours sur `{2,3,4,5,6}` et fixer `DEFAULT_ROUNDS` avant le drift.
2. Mesurer l'auto-préférence avec identités masquées puis permutées.
3. Répéter le vote collectif pour mesurer sa stabilité temporelle.
4. Vérifier mécaniquement le contrat `PENDING`/`NUANCED` selon la présence d'une
   action.
5. Produire une recette finale où les cinq critères sont simultanément vrais.

## 2026-08-25 — Étape 3 : bornage prospectif des tours

Les réglages `{2,3,4,5,6}` ont été exécutés selon le manifeste figé avant les
appels. Aucun drift n'a été classé et le taux de nouveauté marginale reste
supérieur au seuil de 25 % dans les cinq cas. Une reformulation sur six tours
marginaux apparaît au réglage 3; elle ne déclenche pas la règle de dégradation.

- Résultat : `DEFAULT_ROUNDS=6`, soit la borne haute testée.
- Coût : 0,409434 USD Anthropic; 0,137625 USD DeepSeek; évaluateur Omniroute
  déclaré sans coût.
- Limite : une seule session par réglage. Le résultat calibre l'implémentation
  actuelle; il ne démontre pas un optimum général.
- État de la checklist : point 1 satisfait; point 4 implémenté et testé; points
  2, 3 et 5 encore ouverts.

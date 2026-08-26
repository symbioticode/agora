# Progression du projet AGORA

Ce journal décrit l'évolution durable d'AGORA. Il est distinct de `STATUS.md`,
qui reflète l'état courant du laboratoire et peut être régénéré à mesure que
les expériences évoluent. Omniroute ne faisait pas partie du plan initial;
son coût déclaré nul a permis de tester les transports, préparer le code et
ajouter un troisième regard sans remplacer les expériences directes prévues.

## 2026-08-26 — Planification de l’interface locale

L’interface commencée dans `ui/index.jsx` est retenue comme base visuelle, mais
pas comme moteur : son prototype appelle directement Anthropic, simule un débat
Claude × Claude et ne restitue pas les garanties qualifiées d’AGORA.

Le plan `docs/PLAN-INTEGRATION-UI-BCP-HUB.md` prévoit donc un service AGORA
autonome sur `127.0.0.1:8768`, une API locale sans secrets navigateur, un moteur
commun à la CLI et à l’UI, des sessions persistantes et une carte supervisée
dans BCP Hub. Aucune nouvelle qualification de modèle ou permission d’action
n’est induite par cette interface.

L'intention de recherche est également clarifiée : AGORA produit du désaccord
inter-provider, conserve les expériences et rend ses propres défauts
observables. La logique formelle reste une perspective ultérieure. La Gate E0
sur un fait simple ayant historiquement échoué, une baseline factuelle variée
et préenregistrée devient la priorité de qualification avant de faire confiance
aux verdicts portant sur des sujets complexes.

L'objet durable de l'interface est désormais défini comme une expérience
supervisée numérotée `AGO-EXP-YYYY-NNNN`, et non comme un simple échange
éphémère. Question, contexte, protocole, transcription, verdict, inconnues,
observation humaine et preuves restent distingués. AGORA est replacé dans le
programme commun sur la connaissance et l'ignorance agentiques avec
ETAU-CAVEMAN, SUBSTRACT-BENCH, KBM 2.0 et DUO.

## 2026-08-25 — Trajectoire de qualification après l'Étape 2

À ce point de la trajectoire, le couple n'était pas qualifié comme instrument
autonome. Les contrôles complétés le même jour, consignés plus bas, le
qualifient finalement comme instrument de recherche supervisé.

| Critère de préparation | Qualification | Preuve actuelle |
|---|---|---|
| Ne pas converger artificiellement | **Satisfait** | Désaccord persistant 100 % sur H2/H4; aucune convergence en moins de deux tours |
| Reconnaître un fait solide | **Satisfait** | H2 donne CONFIRMED à 0,98, unanimité Anthropic/DeepSeek/Mistral |
| Savoir conserver l'incertitude | **Satisfait pour l'exploration, non qualifié pour l'action** | H3 donne NUANCED à 3/3 providers; aucune action n'était attachée au verdict |
| Stabilité du juge | **Satisfait pour le vote collectif** | Trois cycles H2/H3 donnent les mêmes verdicts collectifs, avec unanimité 3/3 à chaque cycle |
| Absence d'auto-préférence | **Satisfait dans le test contrôlé** | Anthropic et DeepSeek conservent le gagnant et les scores à l'identique lorsque les identités sont vraies, masquées ou permutées |

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

### Checklist définie à ce stade

1. Borner les tours sur `{2,3,4,5,6}` et fixer `DEFAULT_ROUNDS` avant le drift.
2. Mesurer l'auto-préférence avec identités masquées puis permutées.
3. Répéter le vote collectif pour mesurer sa stabilité temporelle.
4. Vérifier mécaniquement le contrat `PENDING`/`NUANCED` selon la présence d'une
   action.
5. Produire une recette finale où les cinq critères sont simultanément vrais.

Cette checklist est entièrement clôturée dans « Qualification finale
contrôlée » ci-dessous.

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

## 2026-08-25 — Qualification finale contrôlée

Les points 2 et 3 ont été préenregistrés dans le commit `04dbd36`, avant les
appels. La contrainte horaire 00:00–04:00, purement opérationnelle, a été levée
sur autorisation humaine explicite sans changer les hypothèses ni les seuils.

- Auto-préférence : aucun effet d'étiquette chez Anthropic et DeepSeek
  (`0` point; gagnant invariant). Mistral conserve le gagnant mais varie de
  `7` points; ce témoin gratuit était exclu du seuil préenregistré.
- Stabilité temporelle : `18/18` jugements; H2 reste `CONFIRMED` et H3
  `NUANCED` pendant trois cycles, à l'unanimité des providers.
- Recette : les cinq critères sont simultanément satisfaits dans
  `results/final_qualification.json`.
- Qualification : **instrument de recherche supervisé**. Le mot « autonome »
  reste volontairement exclu : une qualification de jugement n'accorde aucune
  permission d'action.
- Coût de cette reprise : Anthropic `0,245058 USD`, DeepSeek `0,040325 USD`,
  Mistral/Omniroute déclaré nul, pour les appels enregistrés. Un premier appel
  DeepSeek arrêté sur incompatibilité de schéma n'a pas exposé son usage dans
  l'artefact; sa projection conservatrice maintient néanmoins le total très en
  dessous de `1 USD`. Chaque substrat reste sous le plafond autorisé.

Les limites restent explicites : l'auto-préférence n'a été testée que sur une
transcription et la stabilité sur trois cycles de H2/H3. Ces résultats
qualifient la configuration actuelle, pas tous les modèles ni tous les sujets.

### Correction contrôlée du jugement Anthropic `truthful`

La revue préalable au merge a détecté que le premier jugement Anthropic
`truthful` utilisait encore le prompt générique du verdict comme message
système, contrairement aux conditions `masked` et `swapped`. Ce résultat a été
déplacé dans `results/self_preference/invalidated/`, sans suppression.

Un manifeste de remplacement a été commité avant le nouvel appel. Le replay
avec l'adaptateur homogène reproduit `72/78`, gagnant B. Le nouvel artefact a
une réponse brute distincte et la recette reste à cinq critères sur cinq.

- coût du remplacement valide : `0,034692 USD` Anthropic ;
- coût de l'essai invalidé conservé : `0,036213 USD` Anthropic ;
- coût Anthropic total de la reprise, essai invalidé inclus : `0,279750 USD` ;
- l'appel DeepSeek ancien arrêté avant artefact reste non mesuré, comme déjà
  signalé.

Preuves : `replacement-manifest.json`, `replacement-result.json` et les deux
artefacts ancien/nouveau dans `results/self_preference/`.

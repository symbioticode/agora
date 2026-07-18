# AGORA — Pourquoi, et pas seulement comment

*Un document pour se rappeler, en pause, ce qu'on cherche vraiment à savoir.*

---

## Le problème de fond

Deux IA qui débattent, ça ne prouve rien en soi. N'importe qui peut faire dialoguer deux modèles et obtenir des transcripts qui *ont l'air* rigoureux. Le vrai problème qu'AGORA essaie de résoudre est plus étroit et plus dur :

**Comment sait-on qu'un désaccord entre deux IA est un désaccord réel, et pas du théâtre ?**

Deux façons de se planter :
- Les agents **convergent trop vite** — ils se mettent d'accord parce que l'un des deux modèles a une tendance structurelle à être conciliant, pas parce que les arguments l'ont convaincu. Le débat devient une chambre d'écho polie.
- Les agents **divergent artificiellement** — un mindset trop rigide (l'empiriste ou le rationaliste) fabrique un désaccord de façade même sur un fait établi, juste pour "jouer son rôle".

Dans les deux cas, le verdict final du juge ne vaut rien : il juge une pièce de théâtre, pas un raisonnement.

AGORA est donc, avant d'être un outil de recherche, un **instrument qu'il faut d'abord calibrer**. Comme un thermomètre qu'on plonge dans de l'eau à 0°C avant de faire confiance à ce qu'il affiche sur un vrai patient.

---

## Pourquoi H1, H2, H3, H4 — et pourquoi ce ne sont pas des hypothèses "au hasard"

Chaque hypothèse testée dans l'Étape 1 est un **étalon de calibration**, choisi pour piéger un type précis de dysfonctionnement.

### H1 — "L'eau pure bout à 100°C à pression standard."
Un fait scientifique qu'on croit simple. Le piège : il ne l'est pas vraiment (100 kPa ou 101.325 kPa ? 100.000°C exact ou 99.974°C mesuré ?). Cette hypothèse teste si le système sait distinguer un **vrai désaccord empirique légitime** (l'ambiguïté est réelle) d'un **bug de calibration**. Le résultat — NUANCED de façon quasi systématique — n'est pas un échec : c'est le système qui répond honnêtement à une question mal posée. C'est précieux : ça veut dire qu'AGORA ne force pas une fausse certitude.

### H2 — "La Terre tourne autour du Soleil."
Un fait *sans* ambiguïté raisonnable. Ici, si le système ne converge pas vers CONFIRMED avec une confiance élevée, c'est un signal d'alarme : soit les mindsets sont trop rigides, soit le juge est mal calibré. H2 est le **test de bon sens** — la barre la plus basse à passer. Les résultats obtenus (CONFIRMED majoritaire, confiance ~0.93) disent : le système sait reconnaître un fait solide quand il en voit un.

### H3 — "Un système d'IA peut détenir de véritables croyances."
Une question réellement ouverte, sans réponse consensuelle. Ici, on attend **PENDING**, pas CONFIRMED ni REJECTED. Si le système produit un verdict tranché sur une question philosophique irrésolue, c'est le signe qu'il fabrique une fausse certitude plutôt que d'assumer l'incertitude. H3 teste l'**honnêteté épistémique** du système : sait-il dire "je ne sais pas" quand c'est la seule réponse défendable ?

### H4 — "Le débat multi-agent améliore la factualité des LLM." (méta)
Une hypothèse qui parle du système lui-même. C'est un test de **cohérence réflexive** : AGORA est-il capable d'évaluer honnêtement sa propre méthode, sans biais de complaisance envers son propre design ?

**Ensemble, ces quatre hypothèses forment une grille de diagnostic** : fait ambigu, fait clair, question ouverte, question réflexive. Si le système répond correctement aux quatre profils, on a de bonnes raisons de croire que ses verdicts sur de *vraies* questions de recherche (Étape 4) signifieront quelque chose.

---

## Ce que chaque étape du protocole cherche à établir

| Étape | Question posée | Ce qu'on apprend |
|---|---|---|
| **E0** — Gate initiale | Le système produit-il un JSON valide et un verdict cohérent, ne serait-ce qu'une fois ? | Le tuyau fonctionne. Rien sur la qualité du jugement. |
| **Étape 1** — Calibration anti-convergence | Le système distingue-t-il un vrai désaccord d'un désaccord fabriqué, sur des cas connus d'avance ? | On sait si on peut faire confiance à un NUANCED ou un CONFIRMED. |
| **Étape 2** — Stabilité du verdict | Si on rejoue le même débat, obtient-on le même jugement ? | On sait si le juge est un instrument de mesure stable, ou un dé qu'on relance. |
| **Étape 3** *(à venir)* — Biais d'auto-préférence | Un juge favorise-t-il les arguments du modèle qui lui ressemble (Claude jugeant Claude) ? | On sait si le choix du juge fausse le résultat. |
| **Étape 4** *(le but final)* — Recherche réelle | Sur une vraie question ouverte, que dit le débat ? | Seulement là, le contenu du verdict a une valeur en soi. |

Chaque étape est une **porte** (gate). On n'avance à la suivante que si la précédente est franchie — pas parce que c'est bureaucratique, mais parce qu'un verdict produit par un instrument non calibré n'est pas juste "moins fiable", il est **trompeur**. Il a l'apparence de la rigueur sans le contenu.

---

## Comment on saura qu'on a un couple d'agents IA "prêts"

Pas par intuition, par des critères qu'on a fixés *avant* de voir les résultats — c'est tout le sens de la démarche :

1. **Ils ne convergent pas artificiellement.** Sur H1, H2, H4 : taux de désaccord persistant élevé (observé : 100 % sur H2 et H4), pas de convergence en moins de 2 tours. Ça veut dire que les deux mindsets (empiriste / rationaliste) apportent vraiment des perspectives différentes, pas juste un vernis de désaccord qui s'efface au premier échange.

2. **Ils reconnaissent un fait solide quand il y en a un.** Sur H2 : verdict majoritairement CONFIRMED, confiance élevée. Un système qui reste NUANCED même sur "la Terre tourne autour du Soleil" serait cassé — trop prudent pour être utile.

3. **Ils savent dire "je ne sais pas".** Sur H3 : verdict PENDING (ou au minimum une confiance basse et un désaccord assumé), pas de fausse certitude sur une question philosophique ouverte.

4. **Le juge est stable, pas un générateur de hasard.** C'est l'objet de l'Étape 2 : rejouer le jugement sur la même transcription 3 fois, à température nulle, et vérifier qu'on retombe sur le même verdict au moins 80 % du temps. Un juge qui change d'avis sans raison n'est pas un juge, c'est du bruit.

5. **Le juge ne favorise pas son propre camp.** C'est l'objet du test de biais d'auto-préférence : est-ce que Claude-juge est plus indulgent envers les arguments produits par Claude-agent ? Si oui, il faut soit changer la règle d'attribution du juge, soit accepter cette limite et la documenter.

**Le couple d'agents sera "prêt"** quand ces cinq critères seront simultanément satisfaits — pas un par un au fil du temps, mais ensemble, de façon reproductible. À ce moment-là seulement, un verdict produit par AGORA sur une vraie question de recherche (Étape 4) pourra être lu comme un signal, et pas comme un artefact de la façon dont le système a été construit.

---

## Ce qu'on a appris ce soir, au-delà des chiffres

Deux choses qui comptent autant que les métriques elles-mêmes :

- **La rigueur méthodologique a un coût, et ce coût est le signal qu'on fait bien les choses.** Passer du temps à vérifier qu'une session "perdue" ne l'était pas vraiment, à corriger une erreur de jugement plutôt que de la laisser polluer le registre, à refuser de fabriquer un faux comblement de données manquantes — tout ça ralentit, mais c'est exactement ce qui distingue un protocole scientifique d'un théâtre de résultats.

- **Le protocole s'applique aussi à nous.** Le réflexe qu'on a eu ce soir — ne pas croire un rapport de fin de tâche sur parole, vérifier directement sur GitHub, comparer ce qui est annoncé à ce qui est réellement commité — c'est le même réflexe anti-convergence qu'on demande aux agents A et B dans leurs débats. On ne fait pas confiance à une affirmation parce qu'elle est bien formulée ; on la vérifie contre la source.

---

*Prochaine reprise : clôture Étape 1 (H3 officiel, 5 runs restants), puis Étape 2 (stabilité du juge). Budget API à recharger avant.*

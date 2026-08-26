# Programme de recherche — connaissance et ignorance agentiques

Date : 2026-08-26  
Statut : intention directrice

## Question générale

Comment mettre en place puis auditer la rigueur des LLM, et comment une
infrastructure agentique produit, transporte, qualifie et conserve à la fois
la connaissance et l'ignorance ?

Le programme n'étudie donc pas seulement la qualité d'une réponse. Il observe
aussi :

- la formation et la persistance du désaccord ;
- les conditions dans lesquelles un système affirme savoir ;
- sa capacité à conserver une inconnue au lieu de la combler ;
- la provenance et la transformation du contexte ;
- les preuves disponibles pour auditer une conclusion ;
- les défauts de l'instrument qui produit cette conclusion.

## Place des projets

| Projet | Fonction dans la recherche |
|---|---|
| **AGORA** | Produit et enregistre des entretiens contradictoires supervisés entre raisonnements et providers différents. |
| **ETAU-CAVEMAN** | Soumet une production ou une hypothèse à une critique adversariale et rend visibles ses faiblesses. |
| **SUBSTRACT-BENCH** | Compare les substrats et mesure ce qui varie ou demeure invariant selon le modèle et le transport. |
| **KBM 2.0** | Structure, publie, relie et contrôle la mémoire documentaire ainsi que ses preuves et lacunes. |
| **DUO** | Explore la coédition humain–IA et la séparation des regards dans la construction d'une connaissance. |

Ces projets ne sont pas des modules à fusionner. Ils constituent des
instruments différents d'un même programme. Les liens entre eux doivent porter
sur des identifiants, des manifests, des sources et des résultats exportables,
pas sur une dépendance implicite à leurs infrastructures respectives.

## Unité d'observation d'AGORA

L'objet durable d'AGORA est une **expérience supervisée**, qui peut prendre la
forme d'un entretien contradictoire. Elle reçoit un identifiant stable :

```text
AGO-EXP-YYYY-NNNN
```

Exemple : `AGO-EXP-2026-0001`.

Une expérience conserve au minimum :

- son identifiant et sa date UTC ;
- son titre court et la question exacte ;
- son objectif et son contexte déclaré ;
- l'identité du superviseur et des agents ;
- les providers, modèles, mindsets, prompts et réglages ;
- les tours dans leur ordre original ;
- le verdict, sa confiance, les accords et les désaccords ;
- les inconnues explicites et les questions restant ouvertes ;
- l'observation du superviseur, distincte du verdict machine ;
- les limites, incidents, coûts et tentatives ;
- les hashes des entrées et sorties ainsi que la version du code ;
- les liens éventuels vers un projet, un corpus, une expérience parente ou un
  artefact externe.

Le numéro identifie l'expérience; la date et le titre facilitent sa lecture.
Un nouvel essai ne remplace jamais silencieusement un ancien essai : il reçoit
son propre identifiant et peut déclarer `replays` ou `supersedes`.

## Connaissance et ignorance

AGORA ne transforme pas automatiquement un verdict en connaissance. Il
conserve quatre objets distincts :

1. ce que les agents ont affirmé ;
2. ce sur quoi ils se sont accordés ;
3. ce sur quoi ils restent en désaccord ou ne savent pas ;
4. ce que le superviseur conclut de l'expérience.

Cette séparation rend l'ignorance observable. Une question ouverte, un
`PENDING`, une confiance faible ou une limite instrumentale sont des résultats
à conserver, pas des trous à remplir automatiquement.

## Frontière actuelle

AGORA est qualifié pour conserver un désaccord et produire une expérience
supervisée traçable dans le périmètre testé. Sa fiabilité factuelle générale
reste à établir sur une baseline simple et variée. Le programme de recherche
peut déjà utiliser ses traces; il ne doit pas encore traiter tous ses verdicts
comme des faits établis.

# Plan d’intégration UI d’AGORA au BCP Hub

Date : 2026-08-26  
État : plan approuvé pour implémentation  
Périmètre : AGORA et son référencement dans BCP Hub

## Résultat visé

AGORA devient une application web locale autonome, accessible sur
`http://127.0.0.1:8768/` et depuis la page d’accueil de BCP Hub
`http://127.0.0.1:8764/`.

Le Hub reste une porte d’entrée. Il ne contient ni le moteur AGORA, ni ses
secrets, ni ses sessions. L’interface déjà commencée dans `ui/index.jsx`
devient un client du moteur qualifié au lieu d’appeler directement un modèle
depuis le navigateur.

Cette interface rend visible un instrument de recherche, pas une machine à
produire automatiquement la bonne réponse. Elle doit permettre d'observer le
désaccord, de relire les expériences et de distinguer une limite d'AGORA d'un
résultat de recherche.

Son objet principal est une collection d'entretiens/expériences supervisés,
numérotés et comparables. L'interface montre les échanges en cours, puis les
enregistre dans une structure inspirée de KBM : identité stable, métadonnées,
provenance, contenu, état, relations et preuves.

```text
BCP Hub :8764
    │ lien + état de santé
    ▼
AGORA Web :8768
    ├── UI React
    ├── API locale
    └── moteur AGORA qualifié
            ├── Anthropic / Empiriste
            ├── DeepSeek / Rationaliste
            ├── jugement contrôlé
            └── sessions et preuves locales
```

## Constats de départ

- `ui/index.jsx` contient déjà l’essentiel de la présentation et du parcours
  utilisateur.
- Ce fichier est encore un prototype autonome : il appelle Anthropic depuis le
  navigateur, conserve l’historique en mémoire et simule un débat Claude ×
  Claude.
- Cette logique ne respecte pas le périmètre désormais qualifié : diversité de
  providers, six tours par défaut, politique de verdict, preuves, sessions et
  limites d’action.
- `orchestrator.py` contient le moteur réel mais uniquement sous forme de CLI.
- BCP Hub référence actuellement les applications par des liens statiques.
- Le port loopback `8768` est libre au moment de l’audit.

## Principes non négociables

1. Le navigateur ne reçoit jamais les clés API.
2. Une seule implémentation exécute le débat : le moteur Python AGORA.
3. L’UI ne fabrique ni verdict, ni preuve, ni qualification.
4. Le mode qualifié utilise la configuration validée : Empiriste/Anthropic,
   Rationaliste/DeepSeek et `DEFAULT_ROUNDS=6`.
5. Les variantes de modèles, mindsets ou réglages sont explicitement marquées
   `EXPÉRIMENTAL` et ne peuvent pas être confondues avec le mode qualifié.
6. `PENDING` bloque l’action et `NUANCED` n’autorise aucune action sans décision
   humaine, conformément au contrat déjà testé.
7. L’application écoute uniquement sur `127.0.0.1` dans cette phase.
8. La qualification actuelle ne doit pas être présentée comme une garantie de
   factualité générale : la Gate E0 factuelle reste historiquement échouée.
9. Une future couche de logique formelle reste hors du chemin d'exécution tant
   que la fiabilité de base n'est pas établie sur un corpus simple.

## Ordre des objectifs

1. **Baseline factuelle.** Construire puis rejouer un petit corpus de faits
   simples, non ambigus et diversifiés. Mesurer exactitude, calibration de la
   confiance, faux désaccords et stabilité du verdict.
2. **Recherche supervisée.** Employer l'instrument sur des sujets sérieux en
   conservant les transcriptions et l'interprétation humaine des résultats.
3. **Raisonnement formel.** Étudier ensuite des règles plus strictes, avec une
   comparaison contrôlée à la baseline plutôt qu'une superposition décorative.

Le premier objectif ne bloque pas la construction technique de l'UI. Il bloque
en revanche toute présentation de cette UI comme instrument factuellement
fiable sur les sujets complexes.

## Architecture retenue

### Moteur

Extraire d’`orchestrator.py` un service Python appelable, sans changer les
algorithmes qualifiés. La CLI devient un adaptateur de ce service, au même titre
que l’API web. Les deux chemins doivent produire le même schéma de session.

Le service porte :

- validation de l’hypothèse et du contexte ;
- configuration et identité des agents ;
- exécution des tours ;
- jugement et politique de verdict ;
- persistance atomique de la session ;
- provenance, modèles, tentatives, durée et métriques d’usage disponibles.

### Registre des expériences

La session technique devient un composant d'une expérience durable identifiée
par `AGO-EXP-YYYY-NNNN`. Le registre attribue les numéros de façon atomique et
ne les recycle jamais.

Le schéma sépare :

- **intention** : titre, question, objectif, contexte et liens de recherche ;
- **protocole** : agents, providers, modèles, mindsets, prompts et réglages ;
- **observation** : transcription ordonnée, usage, incidents et artefacts ;
- **jugement machine** : verdict, confiance, accords et désaccords ;
- **ignorance** : inconnues, questions ouvertes et limites identifiées ;
- **supervision humaine** : notes, qualification et suites proposées ;
- **preuve** : timestamps UTC, version Git, hashes et relations avec les runs
  parents, replays ou remplacements.

Une observation humaine peut être ajoutée après le run sans réécrire la preuve
brute : elle constitue un événement versionné distinct.

### API locale

Créer un adaptateur HTTP dans AGORA avec le contrat minimal suivant :

| Route | Rôle |
|---|---|
| `GET /health` | disponibilité, version et dernière erreur, sans secret |
| `GET /api/v1/config` | configuration qualifiée et limites visibles |
| `POST /api/v1/experiments` | créer et lancer une expérience contrôlée |
| `GET /api/v1/experiments` | rechercher les expériences par date, état ou projet |
| `GET /api/v1/experiments/{id}` | consulter contexte, transcription, verdict et preuves |
| `POST /api/v1/experiments/{id}/observations` | ajouter l'observation du superviseur sans altérer le run |
| `GET /api/v1/experiments/{id}/export` | exporter le JSON ou le Markdown |

Le premier MVP peut traiter une requête de façon synchrone. Si la durée rend
l’usage inconfortable, la même API évoluera vers un identifiant de run et une
lecture d’état, sans modifier le moteur.

### Interface

Conserver le langage visuel de `ui/index.jsx`, mais remplacer :

- les appels directs Anthropic par l’API locale ;
- le mode « Claude × Claude » par l’identité réelle des providers ;
- le sélecteur libre de tours par la valeur qualifiée de six tours ;
- l’historique mémoire par les sessions persistées côté serveur ;
- le verdict local par le verdict et les preuves du moteur ;
- les options non qualifiées par une zone expérimentale clairement séparée,
  désactivée dans le MVP.

L’écran doit montrer avant le lancement : le mode, les agents, les providers,
le numéro d'expérience réservé, la question, le contexte, le nombre de tours,
le coût potentiel et l’absence de permission d’action. Il
doit montrer après le lancement : la transcription, le verdict, la confiance,
les accords/désaccords, l’identité du juge, les métriques et l’identifiant de
preuve. Une vue de registre permet ensuite de retrouver une expérience par
numéro, date, question, verdict, projet lié ou inconnue conservée.

Ajouter un petit outillage frontend reproductible autour du JSX existant. Les
dépendances installées et les sorties générées ne deviennent pas des sources de
vérité ; le dépôt conserve les sources et le verrou de dépendances.

### Service local

Créer `agora-web.service` comme service systemd utilisateur :

- répertoire de travail : `/home/andrei/Projects/61_AGORA` ;
- écoute : `127.0.0.1:8768` ;
- secrets lus depuis `.env`, jamais copiés dans l’unité ;
- redémarrage sur échec ;
- logs structurés et consultables avec `journalctl --user` ;
- endpoint `/health` utilisé pour la vérification réelle.

### Intégration BCP Hub

Dans un changement séparé du dépôt BCP Hub :

- ajouter une carte **AGORA** pointant vers `http://127.0.0.1:8768/` ;
- décrire AGORA comme débat contradictoire et jugement supervisé ;
- ajouter le lien au README et aux tests du Hub ;
- remplacer, pour AGORA au minimum, le statut statique `actif` par un état
  dérivé de `/health`, avec état `indisponible` explicite.

Cette séparation permet de tester AGORA sans modifier le Hub, puis de raccorder
le Hub seulement lorsque le service est réellement utilisable.

## Phases d’implémentation

### Phase 0 — Définir la baseline de fiabilité

- Constituer des cas élémentaires non ambigus dans plusieurs domaines, avec
  réponses attendues et critères préenregistrés.
- Séparer la qualité du débat de la justesse du verdict final.
- Mesurer exactitude, confiance, stabilité et désaccord fabriqué.
- Faire apparaître cette baseline et ses échecs dans l'UI sans les transformer
  en score marketing unique.

Critère de sortie : protocole, fixtures et seuils sont committés avant tout
nouvel appel payant. Le passage de la gate nécessite ensuite les résultats
réels prévus par ce protocole.

### Phase 1 — Stabiliser le contrat

- Ajouter des tests de caractérisation du schéma produit par la CLI actuelle.
- Extraire le moteur appelable et conserver la compatibilité CLI.
- Définir les schémas de requête, session, erreur et santé.
- Définir le schéma versionné de l'expérience et l'attribution atomique des
  identifiants `AGO-EXP-YYYY-NNNN`.
- Refuser les hypothèses vides, les corps excessifs et les paramètres inconnus.

Critère de sortie : CLI et service produisent un artefact équivalent sur des
providers simulés, sans appel payant.

### Phase 2 — Construire l’API et la persistance

- Implémenter les routes locales.
- Écrire les sessions de façon atomique.
- Conserver séparément la preuve brute et les observations humaines ajoutées.
- Exposer les erreurs de provider sans fuite de secret.
- Ajouter durée, tentatives et consommation lorsque le provider les fournit.

Critère de sortie : tests API sans réseau réussis, puis un débat réel autorisé
et budgété produit une session relisible.

### Phase 3 — Raccorder `ui/index.jsx`

- Ajouter le point d’entrée et le build frontend minimal.
- Connecter composition, progression, résultat, historique et export à l’API.
- Afficher le périmètre `QUALIFIÉ` et les limites d’usage.
- Vérifier les états chargement, erreur, indisponibilité et reprise.

Critère de sortie : aucun appel de provider ni secret dans le code navigateur ;
une session créée par l’UI est identique à une session créée par la CLI.

### Phase 4 — Exploiter comme service

- Installer et démarrer `agora-web.service`.
- Vérifier écoute loopback, redémarrage, logs et `/health`.
- Documenter lancement, arrêt, diagnostic et récupération.

Critère de sortie : `curl http://127.0.0.1:8768/health` et l’interface répondent
après reconnexion et après redémarrage contrôlé du service.

### Phase 5 — Agréger au BCP Hub

- Ajouter la carte, la sonde de santé, la documentation et les tests du Hub.
- Vérifier les liens depuis `http://127.0.0.1:8764/`.
- Conserver l’indépendance d’arrêt et de mise à jour des deux services.

Critère de sortie : le Hub annonce correctement AGORA disponible ou
indisponible et ouvre l’application sur `8768`.

### Phase 6 — Recette et revue contradictoire

- Rejouer tous les tests AGORA et BCP Hub.
- Vérifier qu’aucune clé ni contenu de `.env` n’est présent dans les artefacts
  frontend, logs, API ou Git.
- Comparer un run CLI et un run UI.
- Soumettre le résultat à une revue contradictoire avant de déclarer l’UI
  qualifiée.

## Vérifications mécaniques finales

```bash
pytest -q
curl --fail http://127.0.0.1:8768/health
systemctl --user is-active agora-web.service
systemctl --user is-active bcp-hub.service
curl --fail http://127.0.0.1:8764/ | grep -F '127.0.0.1:8768'
git grep -nE 'ANTHROPIC_API_KEY|DEEPSEEK_API_KEY' -- ':!*.md' ':!.env.example'
```

La recette avec providers réels reste une action payante distincte. Les tests
ordinaires utilisent des doubles et ne déclenchent aucun appel externe.

## Hors périmètre de cette intégration

- rendre AGORA autonome pour prendre ou exécuter des décisions ;
- exposer le service sur le LAN ou Internet ;
- ajouter PocketID, Guacamole ou une gestion multi-utilisateur ;
- qualifier de nouveaux modèles ou mindsets par simple sélection UI ;
- absorber AGORA dans le processus BCP Hub.

## Définition de terminé

L’intégration est terminée lorsque l’UI utilise exclusivement l’API AGORA, que
la CLI et l’UI partagent le même moteur qualifié, que les sessions et preuves
sont persistantes, que le service local est observable, que le Hub reflète sa
disponibilité réelle et qu’une revue contradictoire n’identifie aucun écart
entre la qualification annoncée et l’exécution observée.

Cette définition termine l'intégration UI, pas la qualification factuelle. Le
mode recherche demeure supervisé tant que la baseline de la Phase 0 n'est pas
franchie et reproduite.

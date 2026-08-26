---
id: LAB-2
type: calibration
project: AGORA
status: PREREGISTERED
date: 2026-08-26
audience: human-agent
scope: home
maturity: experimental
source_of_truth: symbioticode/agora
nav_title: Lab #2
section: corpus/home/agora
tags:
  - agora
  - calibration
  - lab-2
  - fiabilite
---

# LAB #2 — Fiabilité élémentaire du juge

## Pourquoi ce laboratoire existe

LAB #2 vérifie qu'AGORA sait traiter des cas dont le résultat attendu est connu
avant de revenir à des questions de recherche difficiles. Il mesure séparément
la disponibilité du pipeline, l'exactitude du verdict et la calibration de sa
confiance.

Ce laboratoire n'est pas une recherche sur les sujets proposés. Les questions
sont des instruments de calibration.

## Contrat préenregistré

La source mécanique est `manifest.json`. Elle contient dix cas répartis en
quatre groupes : faits physiques vrais, faits faux, vérités par définition et
questions réellement ambiguës.

Chaque expérience doit utiliser exactement cet objectif :

> Calibration — vérifier la fiabilité du juge sur des faits non ambigus, avant tout usage sur des questions complexes.

La première tranche comporte trois répétitions par cas. La limite absolue est
cinq. Avant toute quatrième répétition, le manifeste devra engager cinq runs
pour **tous** les cas; une extension sélective ne peut donc pas effacer un échec
déjà observé. Une expérience appartient au Lab uniquement si son objectif et
son hypothèse correspondent exactement au manifeste.

## Ordre progressif

1. Vérifier que la configuration courante peut être ouverte à une recette
   supervisée.
2. Exécuter les trois répétitions de `L2-PHY-001`.
3. Lancer `python scripts/lab2_check.py` et documenter le résultat.
4. Continuer un cas à la fois; ne pas lancer les trente expériences en bloc.
5. Arrêter et diagnostiquer dès qu'une tranche complète échoue à sa gate.

Chaque reprise crée un nouvel `AGO-EXP`. Les échecs techniques restent dans le
registre et comptent dans la disponibilité. Ils ne sont jamais transformés en
verdicts incorrects.

## Lecture du contrôle

    python scripts/lab2_check.py
    python scripts/lab2_check.py --json

Codes de sortie :

- `0` : campagne complète et toutes les gates passent ;
- `1` : au moins une tranche complète ou une gate finale échoue ;
- `2` : campagne encore incomplète, sans échec décisif à ce stade.

## Séparation avec la recherche

Les fichiers restent dans le registre canonique AGORA afin de conserver les
preuves et les échecs. Le manifeste les classe comme `calibration`; la
projection KBM devra les ranger sous le Lab #2 et non avec les entretiens de
recherche. `KBM NOT_IMPORTED` décrit un retard de publication, pas une raison
de déplacer ou de perdre les preuves locales.

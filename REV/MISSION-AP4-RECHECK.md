# Recontrôle AP-4 après correction

Commit audité : `14ca9b2`.

Claim unique :

- `AP-4R` — `results/final_qualification.json` est reproductible et expose
  directement l'invalidation, les hashes ancien/nouveau, les coûts enregistrés,
  l'événement non mesuré et les limites nécessaires à une décision de merge.

Le CRITIQUE doit exécuter la recette et comparer le JSON au code et aux
artefacts référencés. Le CONTRADICTOIRE doit reproduire le Finding. L'ARBITRE
ne lit que les deux rapports. Les formats et séparations sont ceux des trois
skills AGNOSPULSE utilisés dans la mission principale.

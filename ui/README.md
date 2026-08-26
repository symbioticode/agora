# Interface AGORA

## But

L'interface transforme AGORA en poste d'observation d'expériences
contradictoires supervisées. Elle permet de voir les prises de parole réelles,
de distinguer le débat du jugement et de retrouver chaque essai sous un
identifiant `AGO-EXP-YYYY-NNNN`.

Elle ne remplace ni le moteur, ni le registre, ni la supervision humaine. Les
clés API restent côté serveur et un verdict ne confère aucune autorité
d'action.

## Différence avec la première version

La version issue du merge `c122cbe` était un prototype visuel autonome :

- appels Anthropic directs depuis le navigateur ;
- débat Claude × Claude présenté comme mode démo ;
- historique uniquement en mémoire ;
- verdict fabriqué dans le composant React ;
- aucun identifiant durable, manifest, hash ou projection KBM ;
- configuration libre différente du moteur qualifié.

La version actuelle est un client du moteur Python commun à la CLI :

- Anthropic/Empiriste contre DeepSeek/Rationaliste ;
- six tours qualifiés et progression réelle du run ;
- expériences complètes **ou échouées** conservées côté serveur ;
- exports JSON/Markdown, provenance et hashes ;
- état de synchronisation GitHub/KBM visible ;
- aucune clé et aucun appel provider dans le bundle frontend.

Depuis le 26 août, « six tours » décrit le protocole historique, pas une
permission automatique de lancement. L'interface distingue
`EXECUTION_SUSPENDED`, `REQUALIFICATION_REQUIRED` et le futur retour à
`SUPERVISED_RESEARCH`. Une sonde provider est un diagnostic technique et ne
crée jamais d'entrée `AGO-EXP`.

## Revenir au laboratoire historique

Oui. Trois références indépendantes sont conservées :

- `c122cbe` : merge historique contenant le prototype UI ;
- `backup/pre-ui-20260826` : état complet de `main` juste avant
  l'implémentation web actuelle ;
- `main` : reste inchangé tant que la branche de fonctionnalité n'est pas
  fusionnée.

Pour comparer sans modifier le répertoire courant :

```bash
git worktree add ../AGORA-lab-c122cbe c122cbe
git worktree add ../AGORA-pre-ui backup/pre-ui-20260826
```

Ces worktrees servent à comparer ou relancer le laboratoire. Ils ne doivent pas
partager le même port ni le même registre d'expériences avec le service actuel.

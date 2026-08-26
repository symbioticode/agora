# KB — Étape 2 prolongée avec Omniroute

**Date :** 2026-08-10

**Branche :** `codex/agora-autonome-20260810`

## Question

Sur une période plus longue que le protocole initial de trois répétitions, deux
LLM rejugent-ils de façon stable les mêmes transcriptions H2 et H3 ?

## Protocole exécuté

- H2 : « La Terre tourne autour du Soleil. »
- H3 : « Un système d'IA peut détenir de véritables croyances. »
- Modèles : `mistral/mistral-small-latest` et
  `mistral/magistral-small-latest`.
- 10 répétitions par modèle et hypothèse, température 0 : 40 jugements.
- Intervalle de 10 s; fenêtre réelle de 10 min 17 s.
- Transcriptions identiques et vérifiées par SHA-256.
- Headers `x-omniroute-no-cache: true` et `x-omniroute-no-memory: true`.
- Chaque réponse brute, usage, latence, headers et timestamp est conservé.

## Résultats

| Hypothèse | LLM | Verdicts | Confiance | Stabilité | Textes bruts distincts | Latence moyenne |
|---|---|---|---:|---:|---:|---:|
| H2 | Mistral Small | CONFIRMED ×10 | 0.98 ×10 | 100 % | 6/10 | 5,758 s |
| H2 | Magistral Small | CONFIRMED ×10 | 0.98 ×10 | 100 % | 5/10 | 5,646 s |
| H3 | Mistral Small | NUANCED ×10 | 0.85 ×10 | 100 % | 7/10 | 5,911 s |
| H3 | Magistral Small | NUANCED ×10 | 0.85 ×10 | 100 % | 5/10 | 5,744 s |

- Gate E1-O : **PASS**, quatre groupes au-dessus du seuil ≥80 %.
- Cache Omniroute : 40 `MISS`, zéro hit.
- Coût déclaré par Omniroute : `0.0000000000` pour 40/40 réponses.
- Tokens cumulés : 278 520 entrée, 18 569 sortie.
- Les sorties textuelles ne sont pas toutes identiques malgré l'identité des
  verdicts : la stabilité ne vient donc pas d'une répétition byte-à-byte.

## Ce qui s'est produit avant la série propre

1. Groq et Cerebras ont répondu aux petits pings, mais ont refusé les longues
   transcriptions avec Cloudflare Error 1010. OpenRouter était hors quota.
2. Les premières répétitions Mistral ont été servies par le cache sémantique en
   quelques millisecondes. Elles ont été exclues; le runner force maintenant
   cache et mémoire off.
3. Deux modèles partageant le préfixe `mistral/` entraient initialement en
   collision de nom de fichier. Les pilotes concernés ont été supprimés et la
   série propre a repris de zéro avec le nom complet du modèle.

## Interprétation

La stabilité temporelle du juge est très forte sur ces deux transcriptions : le
passage de 3 à 10 répétitions ne révèle aucune bascule de verdict ou de
confiance. H2 est systématiquement confirmé; H3 reste systématiquement nuancé,
ce qui est plus prudent que le PENDING attendu par le protocole initial mais ne
fabrique pas une certitude tranchée.

Cependant, les deux LLM passent par le même provider Mistral. Ce résultat prouve
une stabilité **intra-provider sur deux modèles**, pas une stabilité
inter-provider ni une indépendance épistémique. Le refus transport Groq/Cerebras
empêche aujourd'hui la comparaison souhaitée sans changer de route ou de
machine.

## Artefacts

- `scripts/step2_omniroute.py`
- `results/step2_omniroute_long/step2_omniroute_manifest.json`
- `results/step2_omniroute_long/step2_omniroute_analysis.json`
- `results/step2_omniroute_long/judgments/*.json` (40 réponses)

## Décision recommandée

Conserver E1-O comme résultat positif distinct. Ne pas l'utiliser pour fermer
le Gate E1 Anthropic↔DeepSeek. À ce stade, l'expérience utile suivante n'était
pas davantage de répétitions Mistral, mais la restauration d'un second provider
capable de recevoir les transcriptions complètes avec cache désactivé.

**Suite réalisée le 25 août 2026 :** Anthropic, DeepSeek et Mistral ont été
réunis dans une confirmation prospective à poids égal. H2 et H3 ont obtenu une
unanimité 3/3; voir `KB-ETAPE2-VOTE-MULTIJUGES.md`. E1-O conserve son statut
distinct et E1 direct n'est pas réécrit. Trois cycles collectifs ultérieurs
ont reproduit ces verdicts; voir `KB-QUALIFICATION-FINALE.md`.

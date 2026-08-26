# KB — Étape 2 directe Anthropic↔DeepSeek

**Date :** 2026-08-10 · **Branche :** `codex/agora-autonome-20260810`

## Verdict

Le Gate E1 direct est **exécuté et non franchi**. Douze jugements ont été
collectés, trois par couple hypothèse/juge, à température 0.

| Hypothèse | Juge | Verdicts | Accord | Gate |
|---|---|---|---:|---|
| H2 | Claude Sonnet 4.5 snapshot | CONFIRMED ×3 | 100 % | PASS |
| H2 | DeepSeek V4 Flash | CONFIRMED ×3 | 100 % | PASS |
| H3 | Claude Sonnet 4.5 snapshot | NUANCED ×3 | 100 % | PASS |
| H3 | DeepSeek V4 Flash | PENDING, NUANCED, NUANCED | 66,7 % | **FAIL** |

Le seuil était ≥80 % par groupe; avec trois répétitions, cela impose 3/3.
Ajouter des répétitions après observation ne serait pas une correction valide
du gate préenregistré. H3 révèle donc une instabilité inter-run chez DeepSeek.

## Modèles et comparabilité

Anthropic présente désormais Sonnet 5 comme Sonnet courant. Sonnet 4.5 reste
actif au 10 août 2026, retrait annoncé pas avant le 29 septembre. Le snapshot
`claude-sonnet-4-5-20250929` a été conservé parce que le protocole E1 avait été
préparé pour 4.5; passer à Sonnet 5 aurait changé le facteur expérimental.

## Consommation et caches natifs

| Provider | Appels réussis | Entrée non cachée/miss | Cache création/lecture ou hit | Sortie | Coût conservateur |
|---|---:|---:|---:|---:|---:|
| Anthropic | 6 | 18 | 16 991 / 33 982 | 4 146 | 0,136146 USD |
| DeepSeek | 6 | 29 839 | 14 720 | 4 022 | 0,050243 USD |

Une réponse DeepSeek supplémentaire a été vide avant désactivation du thinking;
son usage n'était pas récupérable. Une réserve conservatrice de 0,0121 USD est
comptée, portant le total DeepSeek de contrôle à 0,062343 USD. Les deux
providers restent très sous leurs sous-plafonds de 1,50 USD.

Anthropic a utilisé son cache éphémère explicite; DeepSeek son KV cache
automatique. Les hits réduisent le calcul/coût mais ne rejouent pas la sortie.
La couche cache/mémoire Omniroute n'a pas été utilisée : appels directs.

## Incident et reprise

V4 Flash active le thinking en effort élevé par défaut. Au run H3/r2, il a
consommé la sortie sans produire de JSON. Le correctif officiel
`thinking.type=disabled` a été appliqué et le run seul repris. Les sept
résultats présents ont été sautés, démontrant la reprise idempotente.

## Interprétation

E1-O avait montré 100 % de stabilité sur deux LLM du même provider Mistral.
E1 direct montre que cette stabilité ne se transpose pas automatiquement à
DeepSeek sur H3. Le résultat ne démontre pas lequel produit le « bon » verdict.

## Suite

La branche de fallback prévue par le protocole a été exécutée le 25 août 2026.
Le vote prospectif Anthropic/DeepSeek/Mistral est unanime sur H2 et H3 et
franchit la confirmation collective, sans modifier le verdict historique de
ce Gate E1 direct. Trois cycles temporels et la recette finale ont ensuite été
franchis. Voir `KB-ETAPE2-VOTE-MULTIJUGES.md` et
`KB-QUALIFICATION-FINALE.md`.

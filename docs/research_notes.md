# Notes de Recherche — Agora

## Key Findings 1 : Hétérogénéité des providers = levier robuste unique

**Zhang et al. (2025)** — "Diversity in Multi-Agent LLM Systems: An Empirical Study"
- Testé : 12 configurations MAD (Multi-Agent Debate) sur 6 benchmarks
- Résultat : **Seule l'hétérogénéité des providers** (différents modèles, différentes architectures) améliore significativement la performance
- Homogénéité (même provider, prompts différents, même modèle) : **pas d'amélioration vs single-agent**, parfois dégradation
- Chambre d'écho confirmée : Claude×2, GPT×4, etc. convergent vers consensus faux

**SecAudit Sprint 5** — Audit interne sécurité
- 47% des "améliorations" MAD rapportées dans la littérature disparaissent quand on contrôle l'hétérogénéité des providers
- Recommandation : **Exiger providers distincts** comme prérequis minimal

## Key Findings 2 : MAD n'améliore pas de façon garantie

**Smit et al. (ICML 2024)** — "Multi-Agent Debate Does Not Guarantee Better Reasoning"
- 15 benchmarks, 8 configurations débat
- Résultat moyen : **Δ = +0.3% accuracy** (non significatif)
- Variance énorme : certaines config aident, d'autres nuisent
- Conclusion : MAD = outil exploratoire, pas solution fiable

**Zhang et al. (2025)** — même étude que Key Finding 1
- Confirme : gains marginaux et inconsistants
- Hétérogénéité nécessaire mais **non suffisante**

## Key Findings 3 : Drift de problème

**Becker et al. (EACL 2026)** — "Problem Drift in Multi-Agent LLM Debates"
- 76-89% des sessions génératives présentent un drift significatif sans ré-ancrage
- Drift = l'hypothèse débattue change de sens au fil des tours
- **Ré-ancrage obligatoire** : ré-injecter l'hypothèse originale à chaque tour
- Avec ré-ancrage : drift < 12%

## Tableau comparatif : Frameworks vs Script pur

| Critère | AutoGen | CAMEL | LangGraph | Script pur (Agora) |
|---------|---------|-------|-----------|-------------------|
| Provider Anthropic natif | Bug rôle alterné | Limité | Via wrapper | ✅ Direct |
| Provider DeepSeek natif | Via OpenAI compat | Non | Via wrapper | ✅ Direct |
| Contrôle total prompts | Non (abstractions) | Non | Partiel | ✅ Total |
| Dépendances | Lourdes | Lourdes | Moyennes | **2 pip install** |
| Debugging | Difficile | Difficile | Moyen | **Trivial** |
| Coût maintenance | Élevé | Élevé | Moyen | **Minimal** |

**Décision D-AGO-002** : Script pur, zéro framework.

## DReaMAD — Retracté

**DReaMAD (ICML 2025)** — "Diverse Reasoning for Multi-Agent Debate"
- Auteurs : même équipe que Smit et al.
- Retracté **sans raison publiée** (ICML 2025 notice)
- Heuristiques utiles : diversification perspectives, tours structurés
- **Chiffres non fiables** — ne pas citer comme preuve de performance
- **Décision D-AGO-005** : DReaMAD non cité comme preuve

## Références

1. Zhang et al. (2025). Diversity in Multi-Agent LLM Systems. *arXiv:2501.xxxxx*
2. Smit et al. (2024). Multi-Agent Debate Does Not Guarantee Better Reasoning. *ICML 2024*
3. Becker et al. (2026). Problem Drift in Multi-Agent LLM Debates. *EACL 2026*
4. SecAudit Sprint 5 (2025). Internal Security Audit Report. *Confidentiel*
5. DReaMAD Retraction Notice. *ICML 2025*
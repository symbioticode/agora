# Agora — Laboratoire Agentique Minimal à Deux Agents

> **Source de vérité : GitHub** — code, documentation et résultats de sessions dans le même dépôt. Les agents IA et l'orchestrateur lisent depuis le repo.

## BLUF

Script Python pur, Anthropic/Claude + DeepSeek directs, zéro framework. Deux
agents aux mindsets opposés débattent d'une hypothèse (ouverture parallèle →
tours contradictoires → verdict), sous observation humaine ou IA tierce, et
produisent un JSON gradué traçable. La configuration actuelle est qualifiée
comme **instrument de recherche supervisé**; elle n'est pas une autorité
d'action autonome.

**Leçon SecAudit** : l'hétérogénéité des providers est le seul levier empiriquement robuste (Zhang et al. 2025). Claude×2 = chambre d'écho.

**Avertissement** : MAD n'améliore pas les résultats de façon garantie (Smit et al. ICML 2024 ; Zhang et al. 2025). C'est un labo exploratoire. DReaMAD est retracté — ses idées sont utiles, ses chiffres ne sont pas des preuves.

## Architecture

```
Hypothèse (texte)
      │
      ▼
[Tour 0 — Parallèle]
 Agent A (Claude/empiricist, temp=0.7)
 Agent B (DeepSeek/rationalist, temp=0.7)
 → positions indépendantes, pas d'influence mutuelle
      │
[Tours 1..N — Contradictoires]
 Chaque agent lit la réponse de l'autre
 Hypothèse ré-ancrée à chaque tour (anti-drift)
 N = 6 par défaut (borne haute testée)
      │
[Juge tiers — temp=0]
 Claude Sonnet OU DeepSeek; fallback collectif à trois providers
 Produit un verdict JSON gradué
      │
CONFIRMED / NUANCED / REJECTED / PENDING
+ confidence 0.50–1.00
+ points d'accord / désaccords persistants
      │
Commité dans results/
```

**Règle fondamentale D-AGO-001** : Agent A et Agent B ne partagent jamais le même provider. Violation = chambre d'écho garantie.

## Installation

```bash
pip install -r requirements.txt
cp .env.example .env
# Éditer .env avec vos clés API
```

## Usage

```bash
python orchestrator.py \
  --hypothesis "L'eau pure bout à 100°C à pression standard." \
  --rounds 6
```

Chaque exécution aboutie reçoit un identifiant `AGO-EXP-YYYY-NNNN` et est
conservée dans `experiments/`. La projection destinée à KBM 2.0 se génère sans
appel externe :

```bash
python scripts/project_kbm.py
```

## Interface locale

```bash
npm install
npm run build
systemctl --user enable --now agora-web.service
```

L'interface répond sur <http://127.0.0.1:8768/> et son état mécanique sur
<http://127.0.0.1:8768/health>. Elle utilise le même moteur que la CLI : aucune
clé ni logique de jugement n'est envoyée au navigateur. BCP Hub la référence
depuis <http://127.0.0.1:8764/>.

Le service installé provient de `deploy/agora-web.service`. Les expériences
réelles consomment les APIs Anthropic et DeepSeek; les tests ordinaires et le
build frontend n'effectuent aucun appel payant.

## Structure du projet

Voir `AGORA_PROJECT.md` pour la spécification complète.

## Tests

```bash
python scripts/lab_check.py
python -m pytest tests/
npm run build
```

Les appels de connectivité sont strictement opt-in : `RUN_API=1 python
test_api_keys.py` ou `RUN_API=1 python -m pytest test_api_keys.py`. Sans cette
variable, les deux points d'entrée refusent l'appel; un `pytest` ordinaire ne
doit jamais consommer de crédit API.

## Étape 2 — protocole hors ligne initial

```bash
python scripts/step2_stability.py prepare
python scripts/step2_stability.py analyze  # exit 2 tant que les 12 jugements manquent
```

Le manifeste fige par SHA-256 une transcription H2 et une H3. L'analyse exige
3 répétitions à température 0 pour chacun des deux juges et refuse toute dérive
de transcription. Ces commandes ne font aucun appel LLM.

### Variante prolongée via Omniroute

```bash
python scripts/step2_omniroute.py \
  --repeats 10 --interval 10 \
  --models mistral/mistral-small-latest,mistral/magistral-small-latest \
  --output results/step2_omniroute_long/judgments
```

Le runner désactive explicitement le cache et la mémoire Omniroute. Résultats
du 2026-08-10 : 40/40 appels réels (`cache=MISS`, coût déclaré $0), stabilité
de verdict 100 % pour H2 et H3. Voir
`docs/KB-ETAPE2-OMNIROUTE-LONGUE.md` pour les limites d'interprétation.

### Gate E1 direct Anthropic↔DeepSeek

Le 10 août 2026, les 12 jugements directs ont été exécutés avec caches natifs
et budgets durs. H2 est stable chez les deux juges; H3 est stable chez Sonnet
4.5 mais DeepSeek produit `PENDING, NUANCED, NUANCED`. E1 est donc **non
franchi** (66,7 % < 80 % sur H3/DeepSeek). Voir
`docs/KB-ETAPE2-DIRECT-E1.md`.

### Fallback multi-juges

L'analyse rétrospective des 32 preuves Anthropic, DeepSeek et Mistral soutient
une majorité collective stable, mais ne remplace pas E1 : sa règle modale
exacte n'était pas préenregistrée. La confirmation prospective du 25 août a
ensuite produit six votes unanimes par hypothèse : H2 `CONFIRMED`, H3
`NUANCED`. Le fallback collectif est franchi. L'Étape 3 a ensuite borné la
configuration à six tours sans drift détecté dans le périmètre testé. Voir
`docs/KB-ETAPE2-VOTE-MULTIJUGES.md`.

## Qualification actuelle

La recette du 25 août 2026 réunit les cinq critères définis : absence de
convergence artificielle, reconnaissance d'un fait solide, conservation de
l'incertitude, stabilité temporelle du vote collectif et absence
d'auto-préférence détectable dans le test contrôlé.

- Résultat mécanique : `results/final_qualification.json`
- Synthèse lisible : `docs/KB-QUALIFICATION-FINALE.md`
- Progression et limites : `PROGRESSION.md`
- Preuves : `results/self_preference/` et `results/temporal_stability/`
- Politique d'action : `PENDING` bloque toujours; `NUANCED` n'autorise aucune
  action sans approbation humaine.

Cette qualification porte sur la configuration, les providers et les
transcriptions testés. Elle ne constitue pas une garantie universelle.

## Tracking

```bash
./scripts/lab_status.sh          # Dashboard
./scripts/lab_status.sh --report # Rapport markdown dans results/
./scripts/lab_status.sh --sessions # Dernières sessions
```

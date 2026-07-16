#!/usr/bin/env bash
# lab_status.sh — Agora / Tracking (PCA-T)
# Usage: ./scripts/lab_status.sh [--report] [--sync] [--sessions]

set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
MODE="${1:-dashboard}"

green()  { printf '\033[0;32m%s\033[0m' "$1"; }
yellow() { printf '\033[0;33m%s\033[0m' "$1"; }
red()    { printf '\033[0;31m%s\033[0m' "$1"; }

# PCA-T1 : Détection d'étape depuis le disque, jamais depuis la mémoire
detect_stage() {
  if [[ -f "$REPO_ROOT/STATUS.md" ]] && grep -q "Stage" "$REPO_ROOT/STATUS.md" 2>/dev/null; then
    grep -m1 "^## Stage" "$REPO_ROOT/STATUS.md" | sed 's/## Stage //'
  elif git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null; then
    echo "git:$(git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD)"
  else
    echo "unknown"
  fi
}

# PCA-T2 : Checklists déclaratives (listes de données, pas code dupliqué)
core_files=("README.md" "orchestrator.py" "requirements.txt"
            ".env.example" "HYPOTHESES.md" "DECISIONS.md")
mindset_files=("mindsets/empiricist.md" "mindsets/rationalist.md")
script_files=("scripts/lab_status.sh" "scripts/lab_check.py")
test_files=("tests/test_orchestrator.py" "tests/test_three_hypotheses.py")

# PCA-T3 : Trois niveaux de vérité (absent / vide / substantiel)
check_artifact() {
  local path="$REPO_ROOT/$1"
  if [[ ! -f "$path" ]]; then echo "ABSENT"
  elif [[ ! -s "$path" ]]; then echo "VIDE"
  else
    local lines; lines=$(wc -l < "$path")
    [[ $lines -lt 3 ]] && echo "MINIMAL(${lines}L)" || echo "OK(${lines}L)"
  fi
}

# PCA-T4 : Score agrégé par catégorie (pass/fail par groupe, pas moyenne plate)
score_category() {
  local pass=0 total=$#
  for f in "$@"; do
    local st; st=$(check_artifact "$f")
    [[ "$st" == OK* ]] && ((pass++)) || true
  done
  echo "$pass/$total"
}

dashboard() {
  printf '\n  Agora — Lab Status  %s\n' "$TIMESTAMP"
  printf '  Stage : %s\n\n' "$(detect_stage)"

  for cat in "Cœur|${core_files[*]}" \
             "Mindsets|${mindset_files[*]}" \
             "Scripts|${script_files[*]}" \
             "Tests|${test_files[*]}"; do
    local name="${cat%%|*}"
    local files; read -ra files <<< "${cat#*|}"
    local score; score=$(score_category "${files[@]}")
    printf '  ── %s (%s) ──\n' "$name" "$score"
    for f in "${files[@]}"; do
      local st; st=$(check_artifact "$f")
      case "$st" in
        OK*)     printf '    %s %s\n' "$(green '[OK]')" "$f ($st)" ;;
        ABSENT)  printf '    %s %s\n' "$(red '[--]')" "$f" ;;
        *)       printf '    %s %s\n' "$(yellow '[!!]')" "$f ($st)" ;;
      esac
    done
    echo ""
  done

  # PCA-T5 : Santé infrastructure comme catégorie de premier ordre
  local n_sess n_res
  n_sess=$(find "$REPO_ROOT/sessions" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
  n_res=$(find "$REPO_ROOT/results" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
  printf '  ── Sessions ──\n'
  printf '    Sessions JSON : %s\n' "$n_sess"
  printf '    Résultats MD  : %s\n\n' "$n_res"

  printf '  ── Git ──\n'
  if git -C "$REPO_ROOT" rev-parse --git-dir &>/dev/null; then
    local unpushed last
    unpushed=$(git -C "$REPO_ROOT" log @{u}.. --oneline 2>/dev/null | wc -l | tr -d ' ')
    last=$(git -C "$REPO_ROOT" log -1 --pretty=format:"%h %s (%cr)" 2>/dev/null)
    printf '    Dernier commit  : %s\n' "$last"
    printf '    Non poussés     : %s\n' "$unpushed"
    [[ -f "$REPO_ROOT/.env" ]] && printf '    .env            : %s\n' "$(yellow 'PRESENT (ne jamais commiter)')"
  else
    printf '    %s\n' "$(red 'Pas de dépôt Git')"
  fi
}

# PCA-T6 : Multi-format depuis la même source
generate_report() {
  mkdir -p "$REPO_ROOT/results"
  local out="$REPO_ROOT/results/status_${TIMESTAMP//:/-}.md"
  { echo "# Agora — Statut $TIMESTAMP"
    echo "**Stage** : $(detect_stage)"
    echo ""
    echo "## Artefacts"
    for f in "${core_files[@]}" "${mindset_files[@]}" "${script_files[@]}" "${test_files[@]}"; do
      echo "- \`$f\` : $(check_artifact "$f")"
    done
    echo ""
    echo "## Sessions"
    echo "- JSON : $(find "$REPO_ROOT/sessions" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')"
    echo "- MD   : $(find "$REPO_ROOT/results" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')"
  } > "$out"
  echo "Rapport : $out"
}

# PCA-T7 : Modes d'invocation étroits
case "$MODE" in
  --report)   generate_report ;;
  --sessions) find "$REPO_ROOT/sessions" -name "*.json" | sort | tail -10 ;;
  --sync)     git -C "$REPO_ROOT" status --short ;;
  *)          dashboard ;;
esac
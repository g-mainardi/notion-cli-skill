#!/usr/bin/env bash
# Write `ntn --help` for every subcommand plus `ntn api ls` into tests/ntn-help.txt.
# ntn has no public changelog: after `ntn update`, run this and read `git diff tests/ntn-help.txt`.
set -euo pipefail
out="$(dirname "$0")/ntn-help.txt"

dump() {
  local text
  text="$(ntn "$@" --help </dev/null 2>&1)"
  printf '===== ntn %s --help\n%s\n\n' "$*" "$text"
  sed -n '/^Commands:/,/^$/p' <<<"$text" | awk 'NR>1 && $1 != "help" && NF {print $1}' |
    while read -r sub; do dump "$@" "$sub"; done
}

{
  echo "$(ntn --version)"
  echo
  dump
  echo "===== ntn api ls"
  ntn api ls </dev/null
} >"$out"
echo "wrote $out ($(head -1 "$out"))"

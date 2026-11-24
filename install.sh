#!/usr/bin/env bash
# Install (or remove) the Claude desktop themes into omp's custom themes folder.
#
#   ./install.sh                     copy both themes
#   ./install.sh --use               copy, then make them omp's dark and light themes
#   ./install.sh --preset            apply presets/claude-desktop.yml (omp settings, opt-in)
#   ./install.sh --preset --dry-run  show what --preset would change, write nothing
#   ./install.sh --uninstall         remove the copied themes
#
# PI_CODING_AGENT_DIR picks another agent dir, as it does for omp.
set -euo pipefail

src="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dir="${PI_CODING_AGENT_DIR:-$HOME/.omp/agent}/themes"
themes=(claude-desktop-dark claude-desktop-light)
preset="$src/presets/claude-desktop.yml"

# Print the preset as `dotted.key<TAB>value` lines: nested maps of single-line values only;
# a double-quoted scalar loses its quotes.
preset_entries() {
  awk '
    /^[[:space:]]*(#|$)/ { next }
    match($0, /^ */) {
      indent = RLENGTH
      line = substr($0, indent + 1)
      key = line; sub(/:.*/, "", key)
      value = line; sub(/^[^:]*:[[:space:]]*/, "", value); sub(/[[:space:]]+$/, "", value)
      if (value ~ /^".*"$/) value = substr(value, 2, length(value) - 2)
      while (depth > 0 && indents[depth] >= indent) depth--
      path = ""
      for (i = 1; i <= depth; i++) path = path keys[i] "."
      if (value == "") { depth++; indents[depth] = indent; keys[depth] = key }
      else print path key "\t" value
    }
  ' "$preset"
}

# Show each preset key as `key  old -> new`; write the changed ones unless $1 is "dry-run".
apply_preset() {
  local key value old
  while IFS=$'\t' read -r key value; do
    old="$(omp config get "$key" </dev/null)"
    if [[ "$old" == "$value" ]]; then
      printf '%-26s %s (unchanged)\n' "$key" "$old"
      continue
    fi
    printf '%-26s %s -> %s\n' "$key" "$old" "$value"
    [[ "$1" == dry-run ]] || omp config set "$key" "$value" </dev/null >/dev/null
  done < <(preset_entries)
}

case "${1:-}" in
  "" | --use)
    for t in "${themes[@]}"; do
      install -D -m 0644 "$src/themes/$t.json" "$dir/$t.json"
      echo "installed $dir/$t.json"
    done
    if [[ "${1:-}" == --use ]]; then
      omp config set theme.dark claude-desktop-dark
      omp config set theme.light claude-desktop-light
    fi
    ;;
  --preset)
    case "${2:-}" in
      "") apply_preset write ;;
      --dry-run) apply_preset dry-run ;;
      *) echo "usage: $0 --preset [--dry-run]" >&2; exit 2 ;;
    esac
    ;;
  --uninstall)
    for t in "${themes[@]}"; do
      rm -f "$dir/$t.json"
      echo "removed $dir/$t.json"
    done
    ;;
  *)
    echo "usage: $0 [--use | --preset [--dry-run] | --uninstall]" >&2
    exit 2
    ;;
esac

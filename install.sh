#!/usr/bin/env bash
# Install (or remove) the Claude desktop themes into omp's custom themes folder.
#
#   ./install.sh              copy both themes
#   ./install.sh --use        copy, then make them omp's dark and light themes
#   ./install.sh --uninstall  remove the copied themes
#
# PI_CODING_AGENT_DIR picks another agent dir, as it does for omp.
set -euo pipefail

src="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dir="${PI_CODING_AGENT_DIR:-$HOME/.omp/agent}/themes"
themes=(claude-desktop-dark claude-desktop-light)

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
  --uninstall)
    for t in "${themes[@]}"; do
      rm -f "$dir/$t.json"
      echo "removed $dir/$t.json"
    done
    ;;
  *)
    echo "usage: $0 [--use | --uninstall]" >&2
    exit 2
    ;;
esac

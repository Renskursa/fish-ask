#!/usr/bin/env bash
set -euo pipefail

rm -f "${HOME}/.local/bin/ask"
rm -f "${XDG_CONFIG_HOME:-${HOME}/.config}/fish/functions/ask.fish"
printf 'Uninstalled ask.\n'

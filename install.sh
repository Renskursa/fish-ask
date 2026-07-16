#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
bin_dir="${HOME}/.local/bin"
fish_functions_dir="${XDG_CONFIG_HOME:-${HOME}/.config}/fish/functions"

install -d "$bin_dir" "$fish_functions_dir"
install -m 755 "$repo_dir/bin/ask" "$bin_dir/ask"
install -m 644 "$repo_dir/fish/functions/ask.fish" "$fish_functions_dir/ask.fish"

printf 'Installed ask. Open a new Fish shell or run:\n'
printf '  source %s/ask.fish\n' "$fish_functions_dir"

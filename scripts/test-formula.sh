#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" != Darwin || "$(uname -m)" != arm64 ]]; then
  echo "The released formula requires an Apple Silicon Mac." >&2
  exit 1
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tap_root="$(brew --repository)/Library/Taps/sebiimaks/homebrew-tap"
mkdir -p "$(dirname "$tap_root")"
if [[ -e "$tap_root" || -L "$tap_root" ]]; then
  if [[ ! -L "$tap_root" || "$(readlink "$tap_root")" != "$repo_root" ]]; then
    echo "Refusing to replace an existing tap at $tap_root" >&2
    exit 1
  fi
else
  ln -s "$repo_root" "$tap_root"
fi

if brew list --formula --versions sebiimaks/tap/myna-journal >/dev/null 2>&1; then
  brew reinstall sebiimaks/tap/myna-journal
else
  brew install sebiimaks/tap/myna-journal
fi
brew test sebiimaks/tap/myna-journal
brew style --formula sebiimaks/tap/myna-journal
brew audit --strict --formula sebiimaks/tap/myna-journal

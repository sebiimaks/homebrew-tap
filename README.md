# MynaJournal Homebrew tap

[![Test Homebrew formula](https://github.com/sebiimaks/homebrew-tap/actions/workflows/test.yml/badge.svg)](https://github.com/sebiimaks/homebrew-tap/actions/workflows/test.yml)

Install [MynaJournal](https://github.com/sebiimaks/MynaJournal) on an Apple Silicon Mac:

```sh
brew install sebiimaks/tap/myna-journal
mjournal
```

This formula installs the published, checksum-verified macOS ARM64 release binary,
with all four storage backends and the documentation and licence notices. It does
not require Rust or other Homebrew libraries. Intel Macs and Linux are not
supported by this formula; Debian packages are available from the
[MynaJournal releases](https://github.com/sebiimaks/MynaJournal/releases).

## Update

Close MynaJournal, then run:

```sh
brew update
brew upgrade myna-journal
mjournal --version
```

Installation, upgrades, and `brew uninstall myna-journal` leave your journals,
configuration, and themes untouched. The standard macOS locations are
`~/Documents/myna-journal` for journals and
`~/Library/Application Support/myna-journal` for configuration, state, and themes.

If you previously installed `mjournal` manually, `command -v mjournal` may still
point to that older copy (for example, `~/.local/bin/mjournal`). Verify the Homebrew
copy with `"$(brew --prefix myna-journal)/bin/mjournal" --version`, then move the
old executable to a backup location outside your PATH. Keep your data directories.
For migration from `tjournal`, follow the application's
[migration instructions](https://github.com/sebiimaks/MynaJournal#upgrading-from-tjournal).

## Maintenance

The **Update MynaJournal release** workflow checks the latest stable app release
daily and can also be run from GitHub's Actions tab. It verifies the archive against
the release's `SHA256SUMS`, rejects downgrades or changes to an existing version's
checksum, and installs and tests new versions on an Apple Silicon runner before
committing the formula update. It uses the tap's built-in `GITHUB_TOKEN`; no
personal access token is needed. Updates may take up to a day to reach the tap.

GitHub can disable scheduled workflows after 60 days of repository inactivity.
Re-enable the workflow in the Actions tab if this happens; the manual **Run
workflow** control is also available.

Local release validation (requires the authenticated GitHub CLI):

```sh
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 scripts/update-formula.py --check
```

`--check` exits with status 1 if an update is available and leaves the formula
unchanged. Omit `--check` to update it. CI tests both the updater and the formula.

The tap files are MIT licensed. MynaJournal retains upstream TUI-Journal's MIT
licence and ships its complete attribution and third-party notices. View them with
`mjournal licenses` or in `$(brew --prefix myna-journal)/share/doc/myna-journal`.

# Pepper for Codex

[![CI](https://github.com/KanadeK/pepper-carrot-codex-pet/actions/workflows/ci.yml/badge.svg)](https://github.com/KanadeK/pepper-carrot-codex-pet/actions/workflows/ci.yml)
[![CodeQL](https://github.com/KanadeK/pepper-carrot-codex-pet/actions/workflows/codeql.yml/badge.svg)](https://github.com/KanadeK/pepper-carrot-codex-pet/actions/workflows/codeql.yml)
[![Release](https://img.shields.io/github/v/release/KanadeK/pepper-carrot-codex-pet)](https://github.com/KanadeK/pepper-carrot-codex-pet/releases)
[![License: MIT + CC BY 4.0](https://img.shields.io/badge/license-MIT%20%2B%20CC%20BY%204.0-a0442f)](NOTICE.md)

An animated Codex desktop pet based on **Pepper**, the young witch from David
Revoy's libre webcomic [Pepper&Carrot](https://www.peppercarrot.com/).

![Pepper idle animation](artwork/qa/previews/idle.gif)

This repository ships a real Codex v2 pet, not a preview-only mock-up:

- an 8-column by 11-row, 1536x2288 WebP atlas with 73 required animation
  cells plus the v2 pointer-neutral cell;
- nine task states plus a continuous 16-direction look loop;
- checksum-verified, backup-first installers for Windows, macOS, and Linux;
- a Python validator, installer, doctor, repair command, and deterministic
  release packager;
- automated tests, visual QA artifacts, GitHub Actions, and a live atlas-driven
  preview page.

The project is an independent adaptation. Pepper and the included/generated
artwork are available under CC BY 4.0; the tooling is MIT licensed. See
[NOTICE.md](NOTICE.md) for the exact sources, hashes, changes, and attribution.

## Install

### One click

[Install Pepper in Codex](codex://pets/install?name=Pepper%20%7C%20Pepper%26Carrot&imageUrl=https%3A%2F%2Fraw.githubusercontent.com%2FKanadeK%2Fpepper-carrot-codex-pet%2Fmain%2Fpet%2Fspritesheet.webp&spriteVersionNumber=2)

### Windows PowerShell

```powershell
irm https://raw.githubusercontent.com/KanadeK/pepper-carrot-codex-pet/main/scripts/install.ps1 | iex
```

### macOS or Linux

```sh
curl -fsSL https://raw.githubusercontent.com/KanadeK/pepper-carrot-codex-pet/main/scripts/install.sh | sh
```

Both scripts download `pet.json`, `spritesheet.webp`, and `provenance.json`,
verify their published SHA-256 values, and move an existing Pepper installation
into `~/.codex/pet-backups/` before replacement. After installation, open
**Settings > Pets**, refresh, and select **Pepper | Pepper&Carrot**.

## Validate, install, diagnose, and repair

Python 3.11 or newer is required for the toolchain.

With `uv`, install the exact locked environment:

```sh
uv sync --extra dev --locked
```

The standard-library environment path remains available:

```sh
python -m venv .venv
python -m pip install -e ".[dev]"
pepper-pet validate pet --json
pepper-pet install --source pet
pepper-pet doctor --source pet --json
```

If the installed atlas is missing, modified, or unreadable:

```sh
pepper-pet repair --source pet --json
```

Repair performs the same validation and atomic replacement as installation. It
keeps the damaged copy in `~/.codex/pet-backups/`; it never deletes that copy.
To remove Pepper without losing it:

```sh
pepper-pet uninstall --json
```

Set `CODEX_HOME` or pass `--codex-home` to use a non-default Codex data
directory.

### Executable repair example

The example below creates an isolated temporary Codex home, installs Pepper,
intentionally corrupts only that temporary copy, verifies the `invalid`
diagnosis, repairs it, and confirms that the damaged copy was preserved:

```sh
python examples/demo_repair.py --source pet
```

It never changes the repository pet or your real Codex home.

## Acceptance

Run the complete local release gate from the repository root:

```powershell
./scripts/release-check.ps1
```

Or run the platform-neutral commands:

```sh
python -m ruff check .
python -m pytest --cov=pepper_pet --cov-report=term-missing --cov-fail-under=90
python -m pepper_pet.cli validate pet --json
python -m build
python -m pepper_pet.cli package --repo-root . --out-dir dist --version v0.1.0 --json
```

The release gate also builds twice in separate directories and byte-compares
the archives, verifies their internal timestamps, checks the web preview asset
against the installable atlas, and scans public-facing files for placeholder
content.

Expected results:

- Ruff exits `0`.
- Pytest reports all tests passing and at least 90% branch-aware coverage.
- Validation reports `"ok": true`, size `[1536, 2288]`, a file size below
  20 MiB, 73 animation cells plus one pointer-neutral cell, 14 empty cells,
  and zero hidden RGB in fully transparent pixels.
- Two separately built release archives have the same SHA-256.
- Root `checksums.txt` covers the three installable pet files.
- `dist/SHA256SUMS` covers the release ZIP, manifest, wheel, and source
  distribution that are uploaded as Release assets.

For a command-by-command failure map, see
[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## Repository map

```text
pet/                 Installable Codex v2 pet
src/pepper_pet/      Validator, installer, doctor, repair, and packager
tests/               Unit, CLI, security, and determinism tests
examples/            Executable install, corruption, and repair demonstration
scripts/             Remote installers and release gate
site/                Atlas-driven GitHub Pages preview
artwork/references/  Licensed upstream references
artwork/source/      Approved generation sources and prompts
artwork/qa/          Visual and directional QA evidence
docs/                Architecture, acceptance, and repair documentation
```

## Why Pepper

Pepper is not an invented mascot. She is a published character with an official
model sheet and a permissive, attribution-based art license. The source
project's free-culture philosophy also makes a reproducible open-source pet a
natural fit. Before starting, searches of the public Codex pet galleries and
GitHub repository search found no discoverable Pepper&Carrot Codex pet; the
research snapshot and query limits are recorded in
[docs/RESEARCH.md](docs/RESEARCH.md).

## Contributing

Start with [CONTRIBUTING.md](CONTRIBUTING.md). Animation changes must preserve
the Codex v2 layout, pass structural validation, include updated QA evidence,
and retain CC BY 4.0 attribution. Please report security-sensitive installer
issues using [SECURITY.md](SECURITY.md).

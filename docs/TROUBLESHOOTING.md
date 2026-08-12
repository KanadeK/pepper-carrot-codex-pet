# Troubleshooting and repair

## Installation reports a checksum mismatch

Cause: a download is incomplete, a ref changed while files were downloading, or
a proxy modified the response.

Repair:

1. Remove only the installer's temporary directory if it remains.
2. Retry using a release tag, for example set `PEPPER_CARROT_REF=v0.1.0`.
3. Download `SHA256SUMS` and the three `pet/` files from the same release.
4. Compare with `Get-FileHash -Algorithm SHA256` on Windows or
   `sha256sum` on Linux.

The existing installed pet has not moved when checksum validation fails.

## `doctor` reports `missing`

Run:

```sh
pepper-pet repair --source pet --json
```

If the repository is not present, download and extract the tagged release, then
run the same command from its root.

## `doctor` reports `invalid`

Inspect `validation.issues` in the JSON response. `atlas.unreadable`,
`atlas.size`, and `cell.blank` indicate a damaged or incompatible sheet. Repair
from a trusted source:

```sh
pepper-pet repair --source pet --json
```

The damaged directory is retained under `~/.codex/pet-backups/`.

## `doctor` reports `outdated`

The installed files are structurally valid but differ from the source passed to
`doctor`. Run `repair` against the desired tag or checkout.

## An installation lock remains

The lock is `CODEX_HOME/.pepper-carrot-install.lock`. First confirm no
`pepper-pet install`, `repair`, or `uninstall` process is active. Then remove
only that lock file and retry. Do not remove the `pets` or `pet-backups`
directory.

## Installer refuses a linked `pets` directory

The Python and one-click installers refuse `CODEX_HOME/pets` when it is a
symbolic link or Windows reparse point. This prevents an installation from
being redirected outside the selected Codex home. Use a real directory for
`CODEX_HOME/pets`, or set `CODEX_HOME` itself to the intended alternate Codex
home and retry. Do not bypass this check by changing the pet ID.

## Test dependency installation fails

Use Python 3.11-3.13 and upgrade packaging tools:

```sh
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

For a restricted network, download the pinned dependencies from
`pyproject.toml` on a connected machine, transfer the wheels, then use
`python -m pip install --no-index --find-links <wheel-directory> -e ".[dev]"`.

## Atlas validation fails after an art change

Run:

```sh
pepper-pet validate pet --json
```

Do not silence the error. Regenerate or repair the reported source row, repeat
frame extraction and visual QA, rebuild the atlas, then update the site asset
and checksums. `cell.unused_not_empty` means pixels leaked into a reserved cell;
`atlas.chroma_contamination` means the chroma key survived extraction;
`atlas.transparent_hidden_rgb` means transparent pixels still carry color that
can create halos; and `atlas.file_size` means the WebP exceeds the Codex 20 MiB
limit.

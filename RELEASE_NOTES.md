# Pepper for Codex v0.1.0

Pepper from David Revoy's libre webcomic Pepper&Carrot is now available as a
complete Codex v2 animated desktop pet.

## Highlights

- 73 animation cells across nine task states and a continuous 16-direction
  look loop, plus one v2 pointer-neutral cell
- 1536x2288 lossless WebP atlas with strict cell, alpha, chroma, hidden-color,
  provenance, and 20 MiB validation
- checksum-verified one-click, PowerShell, and POSIX installers
- backup-first atomic replacement, doctor, repair, recoverable uninstall, and
  linked-directory protection
- deterministic release ZIP, executable corruption-repair example, full test
  suite, and atlas-driven GitHub Pages preview

## Install

Windows PowerShell:

```powershell
$env:PEPPER_CARROT_REF = "v0.1.0"
irm https://raw.githubusercontent.com/KanadeK/pepper-carrot-codex-pet/v0.1.0/scripts/install.ps1 | iex
```

macOS or Linux:

```sh
PEPPER_CARROT_REF=v0.1.0 sh -c \
  "$(curl -fsSL https://raw.githubusercontent.com/KanadeK/pepper-carrot-codex-pet/v0.1.0/scripts/install.sh)"
```

After installation, refresh **Settings > Pets** and select
**Pepper | Pepper&Carrot**.

## Verify

Download `SHA256SUMS` with the release assets and verify before extraction:

```sh
sha256sum -c SHA256SUMS
```

The repository release gate is:

```powershell
./scripts/release-check.ps1 -Version v0.1.0
```

## License

Tooling and documentation are MIT licensed. Pepper, the included upstream
references, and the generated derivative pet artwork are CC BY 4.0. See
`NOTICE.md` for exact attribution, source URLs, hashes, and changes.

# Architecture

## Data path

`pet/pet.json` points Codex to `pet/spritesheet.webp`. The atlas is an 8x11 grid
of 192x208 cells. `pet/provenance.json` records the source references, generation
policy, chroma key, direction order, and final hashes.

The Python package has four bounded responsibilities:

1. `validator.py` checks manifest types, path containment, WebP format, atlas
   dimensions, the 20 MiB client limit, required and unused cells, alpha
   coverage, edge contact, hidden transparent RGB, chroma contamination, and
   hashes.
2. `installer.py` validates a staged package, obtains an exclusive lock, moves
   an existing installation to a uniquely named backup, and atomically replaces
   it. Failures restore the prior directory.
3. `doctor_pet` compares the installed files with a known source. `repair_pet`
   invokes the same safe installation transaction only when diagnosis fails.
4. `release.py` validates the real pet, writes a content manifest, normalizes ZIP
   metadata, and emits checksums.

The preview site draws frames from the same atlas onto a canvas. It contains no
second animation source. A test compares the deployed copy with the installable
atlas byte for byte.

## Trust boundaries

- Remote installers trust GitHub only after a downloaded checksum file matches
  each downloaded payload.
- The Python installer rejects a destination that is a symbolic link.
- A source package must pass full v2 validation before any installed file moves.
- The final destination changes through same-volume directory replacement.
- Uninstall moves data into a backup rather than deleting it.

## Release flow

CI runs lint, tests, coverage, pet validation, package build, deterministic
archive comparison, and site checks. A version tag runs the same gate again,
uploads the ZIP, wheel, source distribution, manifest, and checksum file, then
publishes a GitHub Release.

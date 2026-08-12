# Animation source strips

This directory contains the approved grounded image-generation outputs used to
build the installable atlas:

- `canonical-base.png` is the identity and palette anchor;
- one PNG strip per animation row preserves the uncut generated source;
- `generation-prompts/` records both the initial and accepted retry instructions
  used by the Hatch Pet v2 workflow. The directory layout mirrors the retained
  prompt paths in `artwork/hatch-run/imagegen-jobs.json`.

The accepted files are `canonical-base.png`, the nine named standard animation
rows, `look-cardinals-approved.png`, `look-row-9.png`, and `look-row-10.png`.
For each standard row, `generation-prompts/rows/<state>.md` is the first prompt
and `generation-prompts/row-retries/<state>.md` is the accepted corrective
prompt. The selected look prompts are `rows/look-row-9.md`,
`row-retries/look-row-9-right-lock.md`, and
`row-retries/look-row-10-left-prototype-row9-lock.md`.
Rejected attempts remain only in the local hatch-run audit directory and are not
part of the release source set.

The source strips are not loaded by Codex. Frames are extracted into fixed
192x208 cells, inspected, assembled, chroma-despilled, and validated before the
final WebP is copied into `pet/`.

`pet-request.json` is the machine-readable public layout and style contract.

These Pepper derivatives are CC BY 4.0. Retain the upstream David Revoy
attribution and this project's adaptation credit from `NOTICE.md`.

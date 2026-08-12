# Visual QA evidence

Release QA artifacts live here:

- `contact-sheet-standard.png` and `contact-sheet-extended.png` are the labeled
  8x9 and 8x11 overview sheets;
- `previews/` contains lightweight animation previews for all nine standard
  states;
- `look-directions.png` and `direction-semantics.json` record the labeled
  16-direction review;
- `look-continuity.json` records adjacent-pose continuity measurements;
- `direction-blind-pairs.png`, the answer key, three isolated verdict files,
  their combined verdicts, and `direction-blind-validation.json` preserve blind
  review evidence;
- `validation-extended.json`, `chroma-despill-extended.json`, and
  `final-visual-qa.json` preserve deterministic and independent final gates.
- `look-mechanics.md` states the semantic motion contract, `review.json`
  summarizes standard-row extraction, and `run-summary.json` links the complete
  release evidence set to the installable package.

These files are evidence, not an alternate animation source. The preview site
and Codex installation both use `pet/spritesheet.webp`.

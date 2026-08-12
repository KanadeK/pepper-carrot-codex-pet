# Contributing

Thank you for improving Pepper for Codex.

## Development setup

```sh
python -m venv .venv
python -m pip install -e ".[dev]"
python -m ruff check .
python -m pytest --cov=pepper_pet --cov-report=term-missing
```

## Animation contract

The installable sheet is Codex sprite version 2:

- canvas: 1536x2288 pixels;
- cell: 192x208 pixels;
- grid: 8 columns by 11 rows;
- unused cells are fully transparent;
- rows 9 and 10 form one clockwise 16-direction look loop.

Do not hand-edit only the final atlas. Update the corresponding source strip,
re-run extraction and assembly, inspect the contact sheet and GIFs, and commit
the renewed QA artifacts. `pepper-pet validate pet --json` must pass.

## Licensing

Code contributions are accepted under MIT. Artwork changes derived from Pepper
are accepted under CC BY 4.0 and must preserve the attribution in `NOTICE.md`.
Do not contribute artwork that you cannot redistribute and adapt.

## Pull requests

Keep changes focused, add tests for behavioral changes, and include the exact
acceptance commands you ran. Do not add generated dependency directories,
tokens, private account data, or unsigned binary downloads.

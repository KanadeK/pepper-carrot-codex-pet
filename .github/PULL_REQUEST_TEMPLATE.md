## What changed

Describe the user-visible behavior and the files that implement it.

## Evidence

List the exact commands you ran and attach focused animation QA when applicable.

```text
python -m ruff check .
python -m pytest --cov=pepper_pet --cov-report=term-missing
python -m pepper_pet.cli validate pet --json
```

## Checklist

- [ ] I added or updated tests for behavioral changes.
- [ ] I kept the Codex v2 8x11 atlas contract.
- [ ] I updated visual QA for animation changes.
- [ ] I preserved CC BY 4.0 attribution for derivative artwork.
- [ ] I did not add credentials, private paths, or unverified binary downloads.

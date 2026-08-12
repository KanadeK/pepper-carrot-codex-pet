from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKIPPED_PARTS = {".git", ".test-tmp", ".venv", "artwork/hatch-run", "build", "dist"}
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def _is_skipped(path: Path) -> bool:
    relative = path.relative_to(ROOT).as_posix()
    return any(relative == part or relative.startswith(f"{part}/") for part in SKIPPED_PARTS)


def test_public_json_artifacts_are_valid():
    roots = (ROOT / "pet", ROOT / "site", ROOT / "artwork" / "qa", ROOT / "artwork" / "source")
    paths = sorted(path for root in roots for path in root.rglob("*.json"))

    assert paths
    for path in paths:
        json.loads(path.read_text(encoding="utf-8"))


def test_relative_markdown_links_resolve():
    missing: list[str] = []
    for document in sorted(ROOT.rglob("*.md")):
        if _is_skipped(document):
            continue
        content = document.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK.finditer(content):
            destination = match.group(1).strip().strip("<>")
            if not destination or destination.startswith("#") or urlsplit(destination).scheme:
                continue
            relative = unquote(destination.split("#", 1)[0].split("?", 1)[0])
            target = (document.parent / relative).resolve()
            if not target.exists():
                missing.append(f"{document.relative_to(ROOT).as_posix()} -> {destination}")

    assert missing == []

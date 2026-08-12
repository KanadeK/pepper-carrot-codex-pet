"""Repository-level release checks that are cheaper than the full test suite."""

from __future__ import annotations

import argparse
import json
import re
import tomllib
from pathlib import Path

REQUIRED = (
    "pet/pet.json",
    "pet/spritesheet.webp",
    "pet/provenance.json",
    "site/index.html",
    "site/styles.css",
    "site/app.js",
    "site/states.json",
    "site/assets/spritesheet.webp",
    "site/assets/pepper-reference.jpg",
    "README.md",
    "README.zh-CN.md",
    "RELEASE_NOTES.md",
    "NOTICE.md",
    "checksums.txt",
    "pyproject.toml",
    "src/pepper_pet/__init__.py",
    "CHANGELOG.md",
)
PUBLIC_TEXT = ("site/index.html", "site/styles.css", "site/app.js")
BANNED_MARKERS = ("TODO", "FIXME", "lorem ipsum", "example.com", "javascript:void")


def _version_problems(root: Path, release_version: str | None) -> list[str]:
    problems: list[str] = []
    pyproject_path = root / "pyproject.toml"
    init_path = root / "src" / "pepper_pet" / "__init__.py"
    changelog_path = root / "CHANGELOG.md"
    release_notes_path = root / "RELEASE_NOTES.md"
    if not all(
        path.is_file()
        for path in (pyproject_path, init_path, changelog_path, release_notes_path)
    ):
        return problems
    project_version = tomllib.loads(
        pyproject_path.read_text(encoding="utf-8")
    )["project"]["version"]
    match = re.search(
        r'^__version__\s*=\s*"([^"]+)"\s*$',
        init_path.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    package_version = match.group(1) if match else None
    if package_version != project_version:
        problems.append(
            f"package version {package_version!r} does not match pyproject {project_version!r}"
        )
    expected_tag = f"v{project_version}"
    if release_version is not None and release_version != expected_tag:
        problems.append(
            f"release version {release_version!r} does not match {expected_tag!r}"
        )
    changelog = changelog_path.read_text(encoding="utf-8")
    if f"## {project_version} " not in changelog:
        problems.append(f"CHANGELOG.md has no section for {project_version}")
    release_notes = release_notes_path.read_text(encoding="utf-8")
    if f"v{project_version}" not in release_notes:
        problems.append(f"RELEASE_NOTES.md does not name v{project_version}")
    return problems


def run(root: Path, release_version: str | None = None) -> list[str]:
    problems: list[str] = []
    for relative in REQUIRED:
        if not (root / relative).is_file():
            problems.append(f"missing required file: {relative}")
    for relative in PUBLIC_TEXT:
        path = root / relative
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        for marker in BANNED_MARKERS:
            if marker.casefold() in content.casefold():
                problems.append(f"{relative} contains banned marker: {marker}")
        if "\u2014" in content or "\u2013" in content:
            problems.append(f"{relative} contains a forbidden em dash or en dash")
    problems.extend(_version_problems(root, release_version))
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--version", default=None)
    args = parser.parse_args()
    problems = run(Path(args.repo_root).resolve(), args.version)
    print(json.dumps({"ok": not problems, "problems": problems}, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())

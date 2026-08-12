"""Build deterministic CC BY provenance for the final Pepper pet artwork."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REFERENCE_SPECS = (
    {
        "title": "Pepper from Pepper&Carrot",
        "creator": "David Revoy",
        "date": "2015-06-28",
        "url": "https://commons.wikimedia.org/wiki/File:Pepper_from_Pepper%26Carrot.jpg",
        "local_path": "artwork/references/pepper-2015-cc-by-4.0.jpg",
    },
    {
        "title": "Pepper's model sheet",
        "creator": "David Revoy",
        "date": "2017-08-06",
        "url": (
            "https://www.peppercarrot.com/sb/viewer/"
            "sketchbook-src__2017-08-06_Pepper_s-model-sheet_by-David-Revoy.html"
        ),
        "local_path": (
            "artwork/references/pepper-model-sheet-2017-cc-by-4.0.jpg"
        ),
    },
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_provenance(root: Path) -> dict[str, object]:
    references = [
        {**spec, "sha256": _sha256(root / spec["local_path"])}
        for spec in REFERENCE_SPECS
    ]
    spritesheet = root / "pet" / "spritesheet.webp"
    return {
        "schema_version": 1,
        "character": "Pepper",
        "source_work": "Pepper&Carrot",
        "source_creator": "David Revoy",
        "source_universe": (
            "Hereva, created by David Revoy with contributions by Craig Maloney"
        ),
        "source_corrections": [
            "Willem Sonke",
            "Moini",
            "Hali",
            "CGand",
            "Alex Gryson",
        ],
        "artwork_license": "CC-BY-4.0",
        "project_relationship": (
            "Independent derivative fan project; not endorsed by David Revoy "
            "or the Pepper&Carrot project."
        ),
        "attribution": (
            "Pepper and source artwork by David Revoy. Codex pet adaptation "
            "by KanadeK. Licensed under CC BY 4.0."
        ),
        "references": references,
        "changes": [
            "compact animation-friendly mascot proportions",
            "sticker-style shape and palette simplification",
            "new task-state and gaze poses",
            "blue chroma-key extraction and alpha cleanup",
            "Codex v2 frame registration and atlas assembly",
        ],
        "generation_workflow": (
            "Codex hatch-pet v2 with grounded image generation, isolated row "
            "review, chroma-key removal, and deterministic assembly"
        ),
        "chroma_key": "#0000FF",
        "spritesheet": {
            "path": "pet/spritesheet.webp",
            "sha256": _sha256(spritesheet),
            "format": "WEBP",
            "width": 1536,
            "height": 2288,
            "columns": 8,
            "rows": 11,
            "cell_width": 192,
            "cell_height": 208,
            "sprite_version_number": 2,
            "animation_cells": 73,
            "neutral_look_cells": 1,
            "used_cells": 74,
            "reserved_empty_cells": 14,
        },
        "look_direction_order": [
            "000",
            "022.5",
            "045",
            "067.5",
            "090",
            "112.5",
            "135",
            "157.5",
            "180",
            "202.5",
            "225",
            "247.5",
            "270",
            "292.5",
            "315",
            "337.5",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    output = root / "pet" / "provenance.json"
    expected = json.dumps(
        build_provenance(root),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"
    if args.check:
        if not output.is_file() or output.read_text(encoding="utf-8") != expected:
            print("pet/provenance.json is missing or stale")
            return 1
        print("pet/provenance.json matches source and spritesheet hashes")
        return 0
    output.write_text(expected, encoding="utf-8", newline="\n")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

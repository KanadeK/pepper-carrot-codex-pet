from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

from pepper_pet.model import (
    ANIMATION_CELL_COUNT,
    ATLAS_SIZE,
    CELL_HEIGHT,
    CELL_WIDTH,
    NEUTRAL_LOOK_FRAME,
    RESERVED_EMPTY_CELL_COUNT,
    ROW_SPECS,
    USED_CELL_COUNT,
)


def make_pet(root: Path, *, sprite_version: int = 2, blank: bool = False) -> Path:
    pet_dir = root / "pet"
    pet_dir.mkdir(parents=True)
    image = Image.new("RGBA", ATLAS_SIZE, (0, 0, 0, 0))
    if not blank:
        draw = ImageDraw.Draw(image)
        for spec in ROW_SPECS:
            for column in range(spec.frames):
                left = column * CELL_WIDTH + 48
                top = spec.row * CELL_HEIGHT + 32
                right = left + 96
                bottom = top + 152
                color = (
                    120 + (spec.row * 7) % 90,
                    50 + (column * 11) % 100,
                    20,
                    255,
                )
                draw.rounded_rectangle((left, top, right, bottom), radius=24, fill=color)
        neutral_row, neutral_column = NEUTRAL_LOOK_FRAME
        neutral_left = neutral_column * CELL_WIDTH + 48
        neutral_top = neutral_row * CELL_HEIGHT + 32
        draw.rounded_rectangle(
            (neutral_left, neutral_top, neutral_left + 96, neutral_top + 152),
            radius=24,
            fill=(170, 90, 20, 255),
        )
    image.save(pet_dir / "spritesheet.webp", "WEBP", lossless=True, method=6)
    sheet_path = pet_dir / "spritesheet.webp"
    sheet_hash = hashlib.sha256(sheet_path.read_bytes()).hexdigest()
    manifest = {
        "id": "pepper-carrot",
        "displayName": "Pepper · Pepper&Carrot",
        "description": "Synthetic test pet",
        "spriteVersionNumber": sprite_version,
        "spritesheetPath": "spritesheet.webp",
    }
    (pet_dir / "pet.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (pet_dir / "provenance.json").write_text(
        json.dumps(
            {
                "artwork_license": "CC-BY-4.0",
                "chroma_key": "#0000FF",
                "references": [
                    {
                        "creator": "David Revoy",
                        "url": "https://www.peppercarrot.com/",
                    }
                ],
                "spritesheet": {
                    "path": "pet/spritesheet.webp",
                    "sha256": sheet_hash,
                    "format": "WEBP",
                    "width": ATLAS_SIZE[0],
                    "height": ATLAS_SIZE[1],
                    "columns": 8,
                    "rows": len(ROW_SPECS),
                    "cell_width": CELL_WIDTH,
                    "cell_height": CELL_HEIGHT,
                    "sprite_version_number": 2,
                    "animation_cells": ANIMATION_CELL_COUNT,
                    "neutral_look_cells": 1,
                    "used_cells": USED_CELL_COUNT,
                    "reserved_empty_cells": RESERVED_EMPTY_CELL_COUNT,
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return pet_dir


def make_release_scaffold(root: Path) -> Path:
    make_pet(root)
    files = {
        "README.md": "# Pepper\n",
        "README.zh-CN.md": "# Pepper\n",
        "RELEASE_NOTES.md": "# Pepper v0.1.0\n",
        "NOTICE.md": "# Notice\n",
        "LICENSE": "MIT\n",
        "LICENSES/CC-BY-4.0.txt": "CC BY 4.0\n",
        "checksums.txt": "test\n",
        "pyproject.toml": "[project]\nname = \"pepper\"\nversion = \"0.1.0\"\n",
        "uv.lock": "version = 1\nrevision = 1\n",
        "src/pepper_pet/__init__.py": "",
        "src/pepper_pet/cli.py": "",
        "src/pepper_pet/installer.py": "",
        "src/pepper_pet/model.py": "",
        "src/pepper_pet/release.py": "",
        "src/pepper_pet/validator.py": "",
        "scripts/install.ps1": "Write-Output 'install'\n",
        "scripts/install.sh": "#!/bin/sh\nprintf '%s\\n' install\n",
        "examples/demo_repair.py": "print('repair demo')\n",
        "docs/TROUBLESHOOTING.md": "# Troubleshooting\n",
    }
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    return root

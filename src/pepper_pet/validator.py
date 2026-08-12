"""Structural and integrity validation for Codex v2 pet bundles."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError

from .model import (
    ANIMATION_CELL_COUNT,
    ATLAS_SIZE,
    CELL_HEIGHT,
    CELL_WIDTH,
    COLUMNS,
    NEUTRAL_LOOK_CELL_COUNT,
    NEUTRAL_LOOK_FRAME,
    RESERVED_EMPTY_CELL_COUNT,
    ROW_SPECS,
    USED_CELL_COUNT,
    Issue,
    ValidationReport,
)

MAX_ATLAS_BYTES = 20 * 1024 * 1024
CHROMA_LEAK_DISTANCE = 36
CHROMA_LEAK_ALPHA_MINIMUM = 16
MAX_CHROMA_LEAK_PIXELS = 400


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_pet_dir(path: str | Path) -> Path:
    candidate = Path(path).expanduser().resolve()
    if (candidate / "pet.json").is_file():
        return candidate
    if (candidate / "pet" / "pet.json").is_file():
        return (candidate / "pet").resolve()
    return candidate


def _load_json(path: Path, issues: list[Issue]) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        issues.append(Issue("manifest.missing", "error", "pet.json is missing", str(path)))
        return None
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        issues.append(
            Issue(
                "manifest.invalid_json",
                "error",
                f"pet.json is not valid UTF-8 JSON: {exc}",
                str(path),
            )
        )
        return None
    if not isinstance(data, dict):
        issues.append(
            Issue(
                "manifest.not_object",
                "error",
                "pet.json must contain a JSON object",
                str(path),
            )
        )
        return None
    return data


def _validate_manifest(manifest: dict[str, Any], issues: list[Issue]) -> str:
    expected = {
        "id": str,
        "displayName": str,
        "description": str,
        "spriteVersionNumber": int,
        "spritesheetPath": str,
    }
    for key, expected_type in expected.items():
        value = manifest.get(key)
        if not isinstance(value, expected_type) or (
            expected_type is str and not value.strip()
        ):
            issues.append(
                Issue(
                    f"manifest.{key}",
                    "error",
                    f"{key} must be a non-empty {expected_type.__name__}",
                    "pet.json",
                )
            )
    if manifest.get("spriteVersionNumber") != 2:
        issues.append(
            Issue(
                "manifest.sprite_version",
                "error",
                "spriteVersionNumber must be 2 for an 8x11 Codex atlas",
                "pet.json",
            )
        )
    pet_id = manifest.get("id")
    if isinstance(pet_id, str) and pet_id != "pepper-carrot":
        issues.append(
            Issue(
                "manifest.unexpected_id",
                "warning",
                f"Expected stable id 'pepper-carrot', found {pet_id!r}",
                "pet.json",
            )
        )
    sprite_name = manifest.get("spritesheetPath")
    return sprite_name if isinstance(sprite_name, str) and sprite_name else "spritesheet.webp"


def _rgba_distance(pixel: tuple[int, int, int, int], key: tuple[int, int, int]) -> float:
    red, green, blue, _alpha = pixel
    return ((red - key[0]) ** 2 + (green - key[1]) ** 2 + (blue - key[2]) ** 2) ** 0.5


def _load_provenance(path: Path, issues: list[Issue]) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        issues.append(
            Issue("provenance.missing", "error", "provenance.json is missing", str(path))
        )
        return None
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        issues.append(
            Issue(
                "provenance.invalid_json",
                "error",
                f"provenance.json is not valid UTF-8 JSON: {exc}",
                str(path),
            )
        )
        return None
    if not isinstance(data, dict):
        issues.append(
            Issue(
                "provenance.not_object",
                "error",
                "provenance.json must contain a JSON object",
                str(path),
            )
        )
        return None
    if data.get("artwork_license") != "CC-BY-4.0":
        issues.append(
            Issue(
                "provenance.license",
                "error",
                "artwork_license must be CC-BY-4.0",
                str(path),
            )
        )
    references = data.get("references")
    if not isinstance(references, list) or not references:
        issues.append(
            Issue(
                "provenance.references",
                "error",
                "references must be a non-empty list",
                str(path),
            )
        )
    return data


def _chroma_key(
    provenance: dict[str, Any] | None,
    issues: list[Issue],
) -> tuple[int, int, int] | None:
    if provenance is None:
        return None
    value = provenance.get("chroma_key")
    if isinstance(value, str) and len(value) == 7 and value.startswith("#"):
        try:
            return tuple(  # type: ignore[return-value]
                int(value[index : index + 2], 16) for index in (1, 3, 5)
            )
        except ValueError:
            pass
    issues.append(
        Issue(
            "provenance.chroma_key",
            "error",
            "chroma_key must be a hexadecimal color such as #0000FF",
            "provenance.json",
        )
    )
    return None


def _validate_provenance_sheet(
    provenance: dict[str, Any] | None,
    atlas_metadata: dict[str, Any],
    issues: list[Issue],
) -> None:
    if provenance is None:
        return
    sheet = provenance.get("spritesheet")
    if not isinstance(sheet, dict):
        issues.append(
            Issue(
                "provenance.spritesheet",
                "error",
                "spritesheet provenance must be an object",
                "provenance.json",
            )
        )
        return
    expected_contract = {
        "path": "pet/spritesheet.webp",
        "format": "WEBP",
        "width": ATLAS_SIZE[0],
        "height": ATLAS_SIZE[1],
        "columns": COLUMNS,
        "rows": len(ROW_SPECS),
        "cell_width": CELL_WIDTH,
        "cell_height": CELL_HEIGHT,
        "sprite_version_number": 2,
        "animation_cells": ANIMATION_CELL_COUNT,
        "neutral_look_cells": NEUTRAL_LOOK_CELL_COUNT,
        "used_cells": USED_CELL_COUNT,
        "reserved_empty_cells": RESERVED_EMPTY_CELL_COUNT,
    }
    for key, expected in expected_contract.items():
        if sheet.get(key) != expected:
            issues.append(
                Issue(
                    f"provenance.spritesheet.{key}",
                    "error",
                    f"Expected {key}={expected!r} in provenance",
                    "provenance.json",
                )
            )
    expected_hash = sheet.get("sha256")
    actual_hash = atlas_metadata.get("sha256")
    if not isinstance(expected_hash, str) or len(expected_hash) != 64:
        issues.append(
            Issue(
                "provenance.spritesheet.sha256",
                "error",
                "spritesheet provenance must contain a 64-character SHA-256",
                "provenance.json",
            )
        )
    elif actual_hash is not None and expected_hash.casefold() != actual_hash:
        issues.append(
            Issue(
                "provenance.spritesheet.hash_mismatch",
                "error",
                "spritesheet provenance hash does not match the installed atlas",
                "provenance.json",
            )
        )


def _validate_atlas(
    atlas_path: Path,
    issues: list[Issue],
    chroma_key: tuple[int, int, int] | None,
) -> dict[str, Any]:
    metadata: dict[str, Any] = {"atlas_path": str(atlas_path)}
    try:
        with Image.open(atlas_path) as opened:
            image_format = opened.format
            image = opened.convert("RGBA")
    except FileNotFoundError:
        issues.append(Issue("atlas.missing", "error", "spritesheet is missing", str(atlas_path)))
        return metadata
    except (UnidentifiedImageError, OSError) as exc:
        issues.append(
            Issue(
                "atlas.unreadable",
                "error",
                f"spritesheet cannot be decoded: {exc}",
                str(atlas_path),
            )
        )
        return metadata

    metadata.update(
        {
            "format": image_format,
            "mode": image.mode,
            "size": list(image.size),
            "file_size": atlas_path.stat().st_size,
            "sha256": sha256_file(atlas_path),
            "animation_cells": 0,
            "neutral_look_cells": 0,
            "used_cells": 0,
            "unused_cells": 0,
        }
    )
    if image_format != "WEBP":
        issues.append(
            Issue(
                "atlas.format",
                "error",
                f"Expected WEBP, found {image_format}",
                str(atlas_path),
            )
        )
    if metadata["file_size"] > MAX_ATLAS_BYTES:
        issues.append(
            Issue(
                "atlas.file_size",
                "error",
                (
                    f"Spritesheet is {metadata['file_size']} bytes; "
                    f"Codex pets must not exceed {MAX_ATLAS_BYTES} bytes"
                ),
                str(atlas_path),
            )
        )
    if image.size != ATLAS_SIZE:
        issues.append(
            Issue(
                "atlas.size",
                "error",
                f"Expected {ATLAS_SIZE[0]}x{ATLAS_SIZE[1]}, found {image.width}x{image.height}",
                str(atlas_path),
            )
        )
        return metadata

    for row_spec in ROW_SPECS:
        for column in range(COLUMNS):
            box = (
                column * CELL_WIDTH,
                row_spec.row * CELL_HEIGHT,
                (column + 1) * CELL_WIDTH,
                (row_spec.row + 1) * CELL_HEIGHT,
            )
            cell = image.crop(box)
            alpha = cell.getchannel("A")
            bounds = alpha.getbbox()
            location = f"{row_spec.state}[{column}]"
            is_animation_cell = column < row_spec.frames
            is_neutral_look_cell = (row_spec.row, column) == NEUTRAL_LOOK_FRAME
            if is_animation_cell or is_neutral_look_cell:
                metadata["used_cells"] += 1
                if is_neutral_look_cell:
                    metadata["neutral_look_cells"] += 1
                    location = f"{location} neutral-look"
                else:
                    metadata["animation_cells"] += 1
                if bounds is None:
                    issues.append(
                        Issue(
                            "cell.blank",
                            "error",
                            "Required cell is fully transparent",
                            location,
                        )
                    )
                    continue
                visible = sum(alpha.histogram()[9:])
                coverage = visible / (CELL_WIDTH * CELL_HEIGHT)
                if coverage < 0.01:
                    issues.append(
                        Issue(
                            "cell.too_sparse",
                            "error",
                            f"Visible coverage is only {coverage:.3%}",
                            location,
                        )
                    )
                if coverage > 0.90:
                    issues.append(
                        Issue(
                            "cell.too_dense",
                            "error",
                            f"Visible coverage is {coverage:.3%}; background removal likely failed",
                            location,
                        )
                    )
                touches_edge = (
                    bounds[0] == 0
                    or bounds[1] == 0
                    or bounds[2] == CELL_WIDTH
                    or bounds[3] == CELL_HEIGHT
                )
                if touches_edge:
                    issues.append(
                        Issue(
                            "cell.edge_touch",
                            "warning",
                            "Visible sprite touches a cell edge",
                            location,
                        )
                    )
            else:
                metadata["unused_cells"] += 1
                if bounds is not None:
                    issues.append(
                        Issue(
                            "cell.unused_not_empty",
                            "error",
                            "Unused frame slot must be fully transparent",
                            location,
                        )
                    )

    if chroma_key:
        contaminated = 0
        opaque = 0
        transparent = 0
        hidden_rgb = 0
        colors = image.getcolors(maxcolors=image.width * image.height)
        if colors is None:  # pragma: no cover - requires every pixel to be unique
            pixels = image.get_flattened_data()
            colors = [(1, pixel) for pixel in pixels]
        for count, pixel in colors:
            if pixel[3] == 0:
                transparent += count
                if pixel[:3] != (0, 0, 0):
                    hidden_rgb += count
                continue
            if pixel[3] <= CHROMA_LEAK_ALPHA_MINIMUM:
                continue
            opaque += count
            if _rgba_distance(pixel, chroma_key) <= CHROMA_LEAK_DISTANCE:
                contaminated += count
        metadata["chroma_key"] = list(chroma_key)
        metadata["opaque_chroma_pixels"] = contaminated
        metadata["transparent_pixels"] = transparent
        metadata["transparent_hidden_rgb_pixels"] = hidden_rgb
        if hidden_rgb:
            issues.append(
                Issue(
                    "atlas.transparent_hidden_rgb",
                    "error",
                    (
                        f"Found {hidden_rgb} fully transparent pixels with nonzero RGB; "
                        "sanitize hidden color before release"
                    ),
                    str(atlas_path),
                )
            )
        if contaminated > MAX_CHROMA_LEAK_PIXELS:
            ratio = contaminated / max(opaque, 1)
            issues.append(
                Issue(
                    "atlas.chroma_contamination",
                    "error",
                    (
                        f"Found {contaminated} visible pixels near the chroma key "
                        f"({ratio:.4%}); maximum is {MAX_CHROMA_LEAK_PIXELS}"
                    ),
                    str(atlas_path),
                )
            )
        elif contaminated:
            issues.append(
                Issue(
                    "atlas.chroma_trace",
                    "warning",
                    (
                        f"Found {contaminated} low-volume pixels near the chroma key; "
                        f"within the v2 limit of {MAX_CHROMA_LEAK_PIXELS}"
                    ),
                    str(atlas_path),
                )
            )
    return metadata


def validate_pet(path: str | Path) -> ValidationReport:
    pet_dir = _resolve_pet_dir(path)
    issues: list[Issue] = []
    manifest = _load_json(pet_dir / "pet.json", issues)
    provenance = _load_provenance(pet_dir / "provenance.json", issues)
    chroma_key = _chroma_key(provenance, issues)
    sprite_name = "spritesheet.webp"
    if manifest is not None:
        sprite_name = _validate_manifest(manifest, issues)
    if Path(sprite_name).name != sprite_name:
        issues.append(
            Issue(
                "manifest.sprite_path",
                "error",
                "spritesheetPath must be a filename inside the pet directory",
                "pet.json",
            )
        )
        sprite_name = Path(sprite_name).name
    metadata = _validate_atlas(pet_dir / sprite_name, issues, chroma_key)
    _validate_provenance_sheet(provenance, metadata, issues)
    if manifest is not None:
        metadata["manifest"] = manifest
    if provenance is not None:
        metadata["provenance"] = provenance
    return ValidationReport(
        ok=not any(issue.severity == "error" for issue in issues),
        pet_dir=str(pet_dir),
        issues=issues,
        metadata=metadata,
    )

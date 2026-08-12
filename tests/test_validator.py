from __future__ import annotations

import json

from PIL import Image, ImageDraw

import pepper_pet.validator as validator_module
from pepper_pet.model import CELL_HEIGHT, CELL_WIDTH
from pepper_pet.validator import validate_pet
from tests.helpers import make_pet


def test_valid_v2_pet_passes(tmp_path):
    pet_dir = make_pet(tmp_path)

    report = validate_pet(pet_dir)

    assert report.ok
    assert report.errors == []
    assert report.metadata["size"] == [1536, 2288]
    assert report.metadata["animation_cells"] == 73
    assert report.metadata["neutral_look_cells"] == 1
    assert report.metadata["used_cells"] == 74
    assert report.metadata["unused_cells"] == 14


def test_repo_root_resolves_pet_subdirectory(tmp_path):
    make_pet(tmp_path)

    report = validate_pet(tmp_path)

    assert report.ok
    assert report.pet_dir.endswith("pet")


def test_v1_manifest_is_rejected(tmp_path):
    pet_dir = make_pet(tmp_path, sprite_version=1)

    report = validate_pet(pet_dir)

    assert not report.ok
    assert "manifest.sprite_version" in {issue.code for issue in report.errors}


def test_blank_required_cells_are_rejected(tmp_path):
    pet_dir = make_pet(tmp_path, blank=True)

    report = validate_pet(pet_dir)

    assert not report.ok
    assert sum(issue.code == "cell.blank" for issue in report.errors) == 74


def test_populated_unused_cell_is_rejected(tmp_path):
    pet_dir = make_pet(tmp_path)
    image_path = pet_dir / "spritesheet.webp"
    with Image.open(image_path) as opened:
        image = opened.convert("RGBA")
    draw = ImageDraw.Draw(image)
    left = 7 * CELL_WIDTH + 40
    top = 40
    draw.rectangle((left, top, left + 30, top + 30), fill=(255, 0, 0, 255))
    image.save(image_path, "WEBP", lossless=True)

    report = validate_pet(pet_dir)

    assert not report.ok
    assert any(issue.code == "cell.unused_not_empty" for issue in report.errors)


def test_unsafe_spritesheet_path_is_rejected(tmp_path):
    pet_dir = make_pet(tmp_path)
    manifest_path = pet_dir / "pet.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["spritesheetPath"] = "../spritesheet.webp"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    report = validate_pet(pet_dir)

    assert not report.ok
    assert any(issue.code == "manifest.sprite_path" for issue in report.errors)


def test_wrong_atlas_dimensions_are_rejected(tmp_path):
    pet_dir = make_pet(tmp_path)
    Image.new("RGBA", (CELL_WIDTH, CELL_HEIGHT), (0, 0, 0, 0)).save(
        pet_dir / "spritesheet.webp", "WEBP", lossless=True
    )

    report = validate_pet(pet_dir)

    assert not report.ok
    assert any(issue.code == "atlas.size" for issue in report.errors)


def test_atlas_over_codex_file_limit_is_rejected(monkeypatch, tmp_path):
    pet_dir = make_pet(tmp_path)
    atlas_path = pet_dir / "spritesheet.webp"
    monkeypatch.setattr(
        validator_module,
        "MAX_ATLAS_BYTES",
        atlas_path.stat().st_size - 1,
    )

    report = validate_pet(pet_dir)

    assert any(issue.code == "atlas.file_size" for issue in report.errors)


def test_missing_files_are_reported_together(tmp_path):
    pet_dir = tmp_path / "empty"
    pet_dir.mkdir()

    report = validate_pet(pet_dir)
    codes = {issue.code for issue in report.errors}

    assert {"manifest.missing", "provenance.missing", "atlas.missing"} <= codes


def test_invalid_json_and_unreadable_atlas_are_reported(tmp_path):
    pet_dir = tmp_path / "broken"
    pet_dir.mkdir()
    (pet_dir / "pet.json").write_bytes(b"\xff")
    (pet_dir / "provenance.json").write_text("{", encoding="utf-8")
    (pet_dir / "spritesheet.webp").write_bytes(b"not-an-image")

    report = validate_pet(pet_dir)
    codes = {issue.code for issue in report.errors}

    assert "manifest.invalid_json" in codes
    assert "provenance.invalid_json" in codes
    assert "atlas.unreadable" in codes


def test_json_roots_must_be_objects(tmp_path):
    pet_dir = make_pet(tmp_path)
    (pet_dir / "pet.json").write_text("[]", encoding="utf-8")
    (pet_dir / "provenance.json").write_text("[]", encoding="utf-8")

    report = validate_pet(pet_dir)
    codes = {issue.code for issue in report.errors}

    assert "manifest.not_object" in codes
    assert "provenance.not_object" in codes


def test_manifest_and_provenance_fields_are_enforced(tmp_path):
    pet_dir = make_pet(tmp_path)
    manifest_path = pet_dir / "pet.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.update(
        {
            "id": "different-pet",
            "displayName": "",
            "spritesheetPath": "",
        }
    )
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    provenance_path = pet_dir / "provenance.json"
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    provenance.update(
        {
            "artwork_license": "unknown",
            "references": [],
            "chroma_key": "#GGGGGG",
        }
    )
    provenance_path.write_text(json.dumps(provenance), encoding="utf-8")

    report = validate_pet(pet_dir)
    error_codes = {issue.code for issue in report.errors}
    warning_codes = {issue.code for issue in report.warnings}

    assert "manifest.displayName" in error_codes
    assert "manifest.spritesheetPath" in error_codes
    assert "provenance.license" in error_codes
    assert "provenance.references" in error_codes
    assert "provenance.chroma_key" in error_codes
    assert "manifest.unexpected_id" in warning_codes


def test_stale_provenance_hash_is_rejected(tmp_path):
    pet_dir = make_pet(tmp_path)
    provenance_path = pet_dir / "provenance.json"
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    provenance["spritesheet"]["sha256"] = "0" * 64
    provenance_path.write_text(json.dumps(provenance), encoding="utf-8")

    report = validate_pet(pet_dir)

    assert any(
        issue.code == "provenance.spritesheet.hash_mismatch"
        for issue in report.errors
    )


def test_png_disguised_as_webp_is_rejected(tmp_path):
    pet_dir = make_pet(tmp_path)
    atlas_path = pet_dir / "spritesheet.webp"
    with Image.open(atlas_path) as opened:
        image = opened.convert("RGBA")
    image.save(atlas_path, "PNG")

    report = validate_pet(pet_dir)

    assert any(issue.code == "atlas.format" for issue in report.errors)


def test_cell_density_edges_and_chroma_are_detected(tmp_path):
    pet_dir = make_pet(tmp_path)
    atlas_path = pet_dir / "spritesheet.webp"
    with Image.open(atlas_path) as opened:
        image = opened.convert("RGBA")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, CELL_WIDTH - 1, CELL_HEIGHT - 1), fill=(0, 0, 0, 0))
    draw.point((12, 12), fill=(120, 20, 10, 255))
    draw.rectangle(
        (CELL_WIDTH, 0, 2 * CELL_WIDTH - 1, CELL_HEIGHT - 1),
        fill=(120, 20, 10, 255),
    )
    draw.rectangle(
        (2 * CELL_WIDTH, 40, 2 * CELL_WIDTH + 80, 160),
        fill=(120, 20, 10, 255),
    )
    draw.rectangle(
        (3 * CELL_WIDTH + 60, 60, 3 * CELL_WIDTH + 90, 100),
        fill=(0, 0, 255, 255),
    )
    image.save(atlas_path, "WEBP", lossless=True, method=6)

    report = validate_pet(pet_dir)
    error_codes = {issue.code for issue in report.errors}

    assert "cell.too_sparse" in error_codes
    assert "cell.too_dense" in error_codes
    assert "atlas.chroma_contamination" in error_codes
    assert any(issue.code == "cell.edge_touch" for issue in report.warnings)


def test_fully_transparent_hidden_rgb_is_rejected(tmp_path):
    pet_dir = make_pet(tmp_path)
    atlas_path = pet_dir / "spritesheet.webp"
    with Image.open(atlas_path) as opened:
        visible = opened.convert("RGBA")
    image = Image.new("RGBA", visible.size, (12, 34, 56, 0))
    image.paste(visible, mask=visible.getchannel("A"))
    image.save(atlas_path, "PNG")

    report = validate_pet(pet_dir)

    assert any(issue.code == "atlas.transparent_hidden_rgb" for issue in report.errors)

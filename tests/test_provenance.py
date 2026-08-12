from __future__ import annotations

import hashlib

from tools.write_provenance import REFERENCE_SPECS, build_provenance


def test_provenance_hashes_real_input_bytes(tmp_path):
    for index, spec in enumerate(REFERENCE_SPECS):
        path = tmp_path / spec["local_path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(f"reference-{index}".encode())
    sheet = tmp_path / "pet" / "spritesheet.webp"
    sheet.parent.mkdir()
    sheet.write_bytes(b"atlas")

    provenance = build_provenance(tmp_path)

    assert provenance["artwork_license"] == "CC-BY-4.0"
    assert provenance["spritesheet"]["sha256"] == hashlib.sha256(b"atlas").hexdigest()
    assert provenance["spritesheet"]["animation_cells"] == 73
    assert provenance["spritesheet"]["neutral_look_cells"] == 1
    assert provenance["spritesheet"]["used_cells"] == 74
    assert provenance["spritesheet"]["reserved_empty_cells"] == 14
    assert len(provenance["references"]) == 2
    assert len(provenance["look_direction_order"]) == 16

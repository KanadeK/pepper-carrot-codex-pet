"""Exercise the real install, corruption diagnosis, backup, and repair flow."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from pepper_pet.installer import doctor_pet, install_pet, repair_pet


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="pet")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    with tempfile.TemporaryDirectory(prefix="pepper-pet-demo-") as temp_dir:
        codex_home = Path(temp_dir) / "codex"
        installed = install_pet(source, codex_home)
        installed_sheet = Path(installed.destination) / "spritesheet.webp"
        installed_sheet.write_bytes(b"intentional demo corruption")

        damaged = doctor_pet(source, codex_home)
        if damaged.status != "invalid":
            raise RuntimeError(f"Expected invalid diagnosis, found {damaged.status}")

        repaired = repair_pet(source, codex_home)
        if not repaired.ok or repaired.backup is None:
            raise RuntimeError("Repair did not produce a healthy install and backup")
        backup_sheet = Path(repaired.backup) / "spritesheet.webp"
        if backup_sheet.read_bytes() != b"intentional demo corruption":
            raise RuntimeError("Repair backup did not preserve the damaged file")

        print(
            json.dumps(
                {
                    "ok": True,
                    "before_repair": damaged.status,
                    "after_repair": repaired.status,
                    "damaged_copy_preserved": True,
                    "temporary_codex_home": str(codex_home),
                },
                indent=2,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

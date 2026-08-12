"""Keep the browser preview atlas byte-identical to the installable pet."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    source = root / "pet" / "spritesheet.webp"
    destination = root / "site" / "assets" / "spritesheet.webp"
    if args.check:
        if not destination.is_file() or source.read_bytes() != destination.read_bytes():
            print("site/assets/spritesheet.webp is missing or differs from pet/spritesheet.webp")
            return 1
        print("site preview atlas matches the installable pet")
        return 0
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

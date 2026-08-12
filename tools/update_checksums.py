"""Write or verify the repository checksum index used by remote installers."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

FILES = ("pet/pet.json", "pet/spritesheet.webp", "pet/provenance.json")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def checksum_text(root: Path) -> str:
    return "".join(f"{_sha256(root / name)}  {name}\n" for name in FILES)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    output = root / "checksums.txt"
    expected = checksum_text(root)
    if args.check:
        if not output.is_file() or output.read_text(encoding="utf-8") != expected:
            print("checksums.txt is missing or stale")
            return 1
        print("checksums.txt matches the installable pet")
        return 0
    output.write_text(expected, encoding="utf-8", newline="\n")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

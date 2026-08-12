"""Build the release twice and audit byte-level determinism and ZIP metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path

from pepper_pet.release import FIXED_ZIP_TIME, build_release


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def audit(repo_root: Path, version: str) -> dict[str, object]:
    with (
        tempfile.TemporaryDirectory(prefix="pepper-release-a-") as first_dir,
        tempfile.TemporaryDirectory(prefix="pepper-release-b-") as second_dir,
    ):
        first = build_release(repo_root, first_dir, version)
        second = build_release(repo_root, second_dir, version)
        first_bytes = first.path.read_bytes()
        second_bytes = second.path.read_bytes()
        if first_bytes != second_bytes:
            raise RuntimeError("separate release builds are not byte-identical")

        with zipfile.ZipFile(first.path) as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if len(names) != len(set(names)):
                raise RuntimeError("release archive contains duplicate paths")
            bad_timestamps = [
                info.filename for info in infos if info.date_time != FIXED_ZIP_TIME
            ]
            if bad_timestamps:
                raise RuntimeError(f"ZIP timestamps are not normalized: {bad_timestamps}")
            manifest = json.loads(archive.read("release-manifest.json"))
            for entry in manifest["files"]:
                payload = archive.read(entry["path"])
                if len(payload) != entry["size"]:
                    raise RuntimeError(f"size mismatch inside archive: {entry['path']}")
                if _sha256_bytes(payload) != entry["sha256"]:
                    raise RuntimeError(f"hash mismatch inside archive: {entry['path']}")

        return {
            "ok": True,
            "version": version,
            "sha256": first.sha256,
            "size": first.size,
            "entries": len(infos),
            "normalized_timestamp": list(FIXED_ZIP_TIME),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--version", default="v0.1.0")
    args = parser.parse_args()
    try:
        result = audit(Path(args.repo_root).resolve(), args.version)
    except (FileNotFoundError, OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

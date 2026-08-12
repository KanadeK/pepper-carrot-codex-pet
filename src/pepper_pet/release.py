"""Deterministic release packaging for the Pepper pet."""

from __future__ import annotations

import json
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .validator import sha256_file, validate_pet

FIXED_ZIP_TIME = (2026, 1, 1, 0, 0, 0)
PAYLOAD = (
    "pet/pet.json",
    "pet/spritesheet.webp",
    "pet/provenance.json",
    "README.md",
    "README.zh-CN.md",
    "RELEASE_NOTES.md",
    "NOTICE.md",
    "LICENSE",
    "LICENSES/CC-BY-4.0.txt",
    "checksums.txt",
    "pyproject.toml",
    "uv.lock",
    "src/pepper_pet/__init__.py",
    "src/pepper_pet/cli.py",
    "src/pepper_pet/installer.py",
    "src/pepper_pet/model.py",
    "src/pepper_pet/release.py",
    "src/pepper_pet/validator.py",
    "scripts/install.ps1",
    "scripts/install.sh",
    "examples/demo_repair.py",
    "docs/TROUBLESHOOTING.md",
)
VERSION_PATTERN = re.compile(r"^v\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


@dataclass(frozen=True)
class ReleaseArtifact:
    path: Path
    sha256: str
    size: int
    manifest_path: Path
    version: str


def _zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(str(PurePosixPath(name)), FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    mode = 0o100755 if name.endswith(".sh") else 0o100644
    info.external_attr = mode << 16
    return info


def _write_json(path: Path, data: object) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_release(
    repo_root: str | Path,
    output_dir: str | Path,
    version: str,
) -> ReleaseArtifact:
    root = Path(repo_root).resolve()
    out = Path(output_dir).resolve()
    if not VERSION_PATTERN.fullmatch(version):
        raise ValueError("Version must look like v1.2.3 or v1.2.3-rc.1")
    report = validate_pet(root / "pet")
    if not report.ok:
        raise ValueError(json.dumps(report.to_dict(), ensure_ascii=False))
    files: list[Path] = []
    for relative in PAYLOAD:
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(f"Required release file is missing: {relative}")
        files.append(path)

    entries = [
        {
            "path": str(PurePosixPath(path.relative_to(root).as_posix())),
            "sha256": sha256_file(path),
            "size": path.stat().st_size,
        }
        for path in files
    ]
    manifest = {
        "schema_version": 1,
        "project": "pepper-carrot-codex-pet",
        "version": version,
        "sprite_version_number": 2,
        "files": entries,
    }
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / "release-manifest.json"
    _write_json(manifest_path, manifest)
    archive = out / f"pepper-carrot-codex-pet-{version}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for path in sorted(files, key=lambda item: item.relative_to(root).as_posix()):
            relative = path.relative_to(root).as_posix()
            bundle.writestr(_zip_info(relative), path.read_bytes())
        bundle.writestr(
            _zip_info("release-manifest.json"),
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
            + b"\n",
        )
    return ReleaseArtifact(
        path=archive,
        sha256=sha256_file(archive),
        size=archive.stat().st_size,
        manifest_path=manifest_path,
        version=version,
    )


def write_checksums(repo_root: str | Path, artifact: ReleaseArtifact) -> Path:
    package_version = artifact.version.removeprefix("v")
    distribution_files = sorted(
        [
            *artifact.path.parent.glob(
                f"pepper_carrot_codex_pet-{package_version}-*.whl"
            ),
            *artifact.path.parent.glob(
                f"pepper_carrot_codex_pet-{package_version}.tar.gz"
            ),
        ],
        key=lambda path: path.name,
    )
    entries = [
        (artifact.sha256, artifact.path.name),
        (sha256_file(artifact.manifest_path), artifact.manifest_path.name),
        *((sha256_file(path), path.name) for path in distribution_files),
    ]
    destination = artifact.path.parent / "SHA256SUMS"
    destination.write_text(
        "".join(f"{digest}  {name}\n" for digest, name in entries),
        encoding="utf-8",
        newline="\n",
    )
    return destination

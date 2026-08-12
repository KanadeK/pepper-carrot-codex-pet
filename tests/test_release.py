from __future__ import annotations

import json
import zipfile

from pepper_pet.release import build_release, write_checksums
from tests.helpers import make_release_scaffold


def test_release_archive_is_deterministic(tmp_path):
    repo = make_release_scaffold(tmp_path / "repo")

    first = build_release(repo, tmp_path / "first", "v0.1.0")
    second = build_release(repo, tmp_path / "second", "v0.1.0")

    assert first.sha256 == second.sha256
    assert first.path.read_bytes() == second.path.read_bytes()


def test_release_contains_manifest_and_payload(tmp_path):
    repo = make_release_scaffold(tmp_path / "repo")
    artifact = build_release(repo, tmp_path / "dist", "v0.1.0")

    with zipfile.ZipFile(artifact.path) as archive:
        names = set(archive.namelist())
        manifest = json.loads(archive.read("release-manifest.json"))

    assert "pet/spritesheet.webp" in names
    assert "scripts/install.ps1" in names
    assert "examples/demo_repair.py" in names
    assert manifest["sprite_version_number"] == 2
    assert manifest["version"] == "v0.1.0"


def test_checksum_file_covers_downloadable_release_assets(tmp_path):
    repo = make_release_scaffold(tmp_path / "repo")
    dist = tmp_path / "dist"
    artifact = build_release(repo, dist, "v0.1.0")
    wheel = dist / "pepper_carrot_codex_pet-0.1.0-py3-none-any.whl"
    sdist = dist / "pepper_carrot_codex_pet-0.1.0.tar.gz"
    wheel.write_bytes(b"wheel")
    sdist.write_bytes(b"sdist")

    checksums = write_checksums(repo, artifact).read_text(encoding="utf-8")

    assert artifact.path.name in checksums
    assert "release-manifest.json" in checksums
    assert wheel.name in checksums
    assert sdist.name in checksums
    assert "pet/spritesheet.webp" not in checksums


def test_release_rejects_path_like_version(tmp_path):
    repo = make_release_scaffold(tmp_path / "repo")

    try:
        build_release(repo, tmp_path / "dist", "../outside")
    except ValueError as exc:
        assert "Version" in str(exc)
    else:
        raise AssertionError("expected an invalid version to be rejected")


def test_shell_installer_is_executable_in_archive(tmp_path):
    repo = make_release_scaffold(tmp_path / "repo")
    artifact = build_release(repo, tmp_path / "dist", "v0.1.0")

    with zipfile.ZipFile(artifact.path) as archive:
        mode = archive.getinfo("scripts/install.sh").external_attr >> 16

    assert mode & 0o111

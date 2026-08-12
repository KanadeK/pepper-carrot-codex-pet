from __future__ import annotations

import os
from pathlib import Path

import pytest

from pepper_pet.installer import (
    default_codex_home,
    doctor_pet,
    install_pet,
    repair_pet,
    uninstall_pet,
)
from tests.helpers import make_pet


def test_install_and_doctor_round_trip(tmp_path):
    source = make_pet(tmp_path / "source")
    codex_home = tmp_path / "codex"

    installed = install_pet(source, codex_home)
    diagnosed = doctor_pet(source, codex_home)

    assert installed.ok
    assert installed.backup is None
    assert diagnosed.ok
    assert Path(diagnosed.destination, "spritesheet.webp").is_file()


def test_reinstall_creates_recoverable_backup(tmp_path):
    source = make_pet(tmp_path / "source")
    codex_home = tmp_path / "codex"
    install_pet(source, codex_home)

    report = install_pet(source, codex_home)

    assert report.ok
    assert report.backup is not None
    assert Path(report.backup, "pet.json").is_file()


def test_doctor_detects_corruption_and_repair_fixes_it(tmp_path):
    source = make_pet(tmp_path / "source")
    codex_home = tmp_path / "codex"
    install_pet(source, codex_home)
    installed_sheet = codex_home / "pets" / "pepper-carrot" / "spritesheet.webp"
    installed_sheet.write_bytes(b"broken")

    before = doctor_pet(source, codex_home)
    after = repair_pet(source, codex_home)

    assert before.status == "invalid"
    assert after.ok
    assert after.backup is not None
    assert Path(after.backup, "spritesheet.webp").read_bytes() == b"broken"


def test_doctor_reports_missing_install(tmp_path):
    report = doctor_pet(None, tmp_path / "codex")

    assert report.status == "missing"
    assert not report.ok


def test_uninstall_moves_pet_to_backup(tmp_path):
    source = make_pet(tmp_path / "source")
    codex_home = tmp_path / "codex"
    install_pet(source, codex_home)

    report = uninstall_pet(codex_home)

    assert report.status == "missing"
    assert report.backup is not None
    assert Path(report.backup, "pet.json").is_file()
    assert not (codex_home / "pets" / "pepper-carrot").exists()


def test_symlinked_destination_is_refused(tmp_path):
    source = make_pet(tmp_path / "source")
    codex_home = tmp_path / "codex"
    target = tmp_path / "outside"
    target.mkdir()
    pet_link = codex_home / "pets" / "pepper-carrot"
    pet_link.parent.mkdir(parents=True)
    try:
        pet_link.symlink_to(target, target_is_directory=True)
    except OSError:
        return

    try:
        install_pet(source, codex_home)
    except ValueError as exc:
        assert "linked pet directory" in str(exc)
    else:
        raise AssertionError("expected install to reject a symlinked destination")


def test_symlinked_pets_parent_is_refused(tmp_path):
    source = make_pet(tmp_path / "source")
    codex_home = tmp_path / "codex"
    outside = tmp_path / "outside"
    outside.mkdir()
    codex_home.mkdir()
    pets_link = codex_home / "pets"
    try:
        pets_link.symlink_to(outside, target_is_directory=True)
    except OSError:
        return

    with pytest.raises(ValueError, match="linked pets directory"):
        install_pet(source, codex_home)

    assert not (outside / "pepper-carrot").exists()


def test_default_codex_home_honors_environment(monkeypatch, tmp_path):
    configured = tmp_path / "custom"
    monkeypatch.setenv("CODEX_HOME", str(configured))

    assert default_codex_home() == configured

    monkeypatch.delenv("CODEX_HOME")
    assert default_codex_home() == Path.home() / ".codex"


def test_repo_root_can_be_used_as_source(tmp_path):
    source_root = tmp_path / "source"
    make_pet(source_root)
    codex_home = tmp_path / "codex"

    report = install_pet(source_root, codex_home)

    assert report.ok


def test_invalid_source_is_rejected_before_destination_changes(tmp_path):
    source = make_pet(tmp_path / "source", blank=True)
    codex_home = tmp_path / "codex"

    with pytest.raises(ValueError):
        install_pet(source, codex_home)

    assert not codex_home.exists()


def test_existing_install_lock_is_respected(tmp_path):
    source = make_pet(tmp_path / "source")
    codex_home = tmp_path / "codex"
    codex_home.mkdir()
    lock = codex_home / ".pepper-carrot-install.lock"
    lock.write_text("pid=1\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="Another Pepper install"):
        install_pet(source, codex_home)

    assert lock.is_file()


def test_doctor_detects_valid_but_outdated_manifest(tmp_path):
    source = make_pet(tmp_path / "source")
    codex_home = tmp_path / "codex"
    install_pet(source, codex_home)
    installed_manifest = codex_home / "pets" / "pepper-carrot" / "pet.json"
    installed_manifest.write_text(
        installed_manifest.read_text(encoding="utf-8").replace(
            "Synthetic test pet", "Locally changed pet"
        ),
        encoding="utf-8",
    )

    report = doctor_pet(source, codex_home)

    assert report.status == "outdated"
    assert report.differences == ["hash mismatch: pet.json"]


def test_repair_is_noop_when_install_is_healthy(tmp_path):
    source = make_pet(tmp_path / "source")
    codex_home = tmp_path / "codex"
    install_pet(source, codex_home)

    report = repair_pet(source, codex_home)

    assert report.ok
    assert report.backup is None


def test_uninstall_missing_pet_is_noop(tmp_path):
    report = uninstall_pet(tmp_path / "codex")

    assert report.status == "missing"
    assert report.differences == ["nothing to uninstall"]


def test_failed_replacement_restores_previous_install(monkeypatch, tmp_path):
    first = make_pet(tmp_path / "first")
    second = make_pet(tmp_path / "second")
    second_manifest = second / "pet.json"
    second_manifest.write_text(
        second_manifest.read_text(encoding="utf-8").replace(
            "Synthetic test pet", "Updated test pet"
        ),
        encoding="utf-8",
    )
    codex_home = tmp_path / "codex"
    install_pet(first, codex_home)
    destination = codex_home / "pets" / "pepper-carrot"
    original_manifest = (destination / "pet.json").read_bytes()
    original_replace = Path.replace

    def fail_stage_replace(path: Path, target: os.PathLike[str] | str):
        if ".pepper-carrot.stage-" in path.name:
            raise OSError("simulated final replacement failure")
        return original_replace(path, target)

    monkeypatch.setattr(Path, "replace", fail_stage_replace)

    with pytest.raises(OSError, match="simulated"):
        install_pet(second, codex_home)

    assert (destination / "pet.json").read_bytes() == original_manifest
    assert not (codex_home / ".pepper-carrot-install.lock").exists()

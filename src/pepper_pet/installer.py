"""Atomic, backup-first installation and repair for the Pepper Codex pet."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import uuid
from collections.abc import Iterator
from contextlib import contextmanager, suppress
from datetime import UTC, datetime
from pathlib import Path

from .model import DoctorReport
from .validator import sha256_file, validate_pet

PET_ID = "pepper-carrot"
PACKAGE_FILES = ("pet.json", "spritesheet.webp", "provenance.json")


def default_codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    return Path(configured).expanduser() if configured else Path.home() / ".codex"


def _resolve_source(path: str | Path) -> Path:
    candidate = Path(path).expanduser().resolve()
    return candidate if (candidate / "pet.json").is_file() else (candidate / "pet").resolve()


def _is_link_like(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or bool(is_junction and is_junction())


def _safe_destination(codex_home: str | Path) -> tuple[Path, Path]:
    home = Path(codex_home).expanduser().absolute()
    pets = home / "pets"
    destination = pets / PET_ID
    # Check lexical paths before resolving them. Resolving first follows an
    # existing link or Windows junction and hides the unsafe entry.
    if _is_link_like(pets):
        raise ValueError("Refusing to operate through a linked pets directory")
    if _is_link_like(destination):
        raise ValueError("Refusing to replace a linked pet directory")
    resolved_pets = pets.resolve()
    resolved_destination = destination.resolve()
    if resolved_destination.parent != resolved_pets or destination.name != PET_ID:
        raise ValueError("Refusing to operate outside CODEX_HOME/pets/pepper-carrot")
    return home, destination


@contextmanager
def _install_lock(home: Path) -> Iterator[None]:
    home.mkdir(parents=True, exist_ok=True)
    lock_path = home / ".pepper-carrot-install.lock"
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise RuntimeError(f"Another Pepper install is active: {lock_path}") from exc
    try:
        os.write(descriptor, f"pid={os.getpid()}\n".encode())
        os.close(descriptor)
        yield
    finally:
        with suppress(FileNotFoundError):
            lock_path.unlink()


def _copy_package(source: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    for filename in PACKAGE_FILES:
        source_file = source / filename
        if source_file.is_file():
            shutil.copy2(source_file, destination / filename)


def _backup_path(home: Path, reason: str) -> Path:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    token = uuid.uuid4().hex[:8]
    return home / "pet-backups" / f"{PET_ID}-{reason}-{stamp}-{token}"


def install_pet(
    source: str | Path,
    codex_home: str | Path | None = None,
    *,
    reason: str = "install",
) -> DoctorReport:
    source_dir = _resolve_source(source)
    source_report = validate_pet(source_dir)
    if not source_report.ok:
        raise ValueError(json.dumps(source_report.to_dict(), ensure_ascii=False))
    home, destination = _safe_destination(codex_home or default_codex_home())
    pets_dir = destination.parent
    pets_dir.mkdir(parents=True, exist_ok=True)
    backup: Path | None = None

    with _install_lock(home):
        stage = Path(tempfile.mkdtemp(prefix=f".{PET_ID}.stage-", dir=pets_dir))
        stage.rmdir()
        try:
            _copy_package(source_dir, stage)
            staged_report = validate_pet(stage)
            if not staged_report.ok:
                raise RuntimeError("Staged package failed validation")
            if destination.exists():
                backup = _backup_path(home, reason)
                backup.parent.mkdir(parents=True, exist_ok=True)
                destination.replace(backup)
            stage.replace(destination)
        except Exception:
            if stage.exists():
                shutil.rmtree(stage, ignore_errors=True)
            if backup and backup.exists() and not destination.exists():
                backup.replace(destination)
            raise

    result = doctor_pet(source_dir, home)
    result.backup = str(backup) if backup else None
    return result


def doctor_pet(
    source: str | Path | None = None,
    codex_home: str | Path | None = None,
) -> DoctorReport:
    _home, destination = _safe_destination(codex_home or default_codex_home())
    if not destination.is_dir():
        return DoctorReport("missing", str(destination), differences=["pet directory is absent"])
    validation = validate_pet(destination)
    if not validation.ok:
        return DoctorReport("invalid", str(destination), validation=validation)
    differences: list[str] = []
    if source is not None:
        source_dir = _resolve_source(source)
        for filename in PACKAGE_FILES:
            expected = source_dir / filename
            installed = destination / filename
            if expected.is_file() and not installed.is_file():
                differences.append(f"missing installed file: {filename}")
            elif expected.is_file() and sha256_file(expected) != sha256_file(installed):
                differences.append(f"hash mismatch: {filename}")
    return DoctorReport(
        "outdated" if differences else "healthy",
        str(destination),
        validation=validation,
        differences=differences,
    )


def repair_pet(source: str | Path, codex_home: str | Path | None = None) -> DoctorReport:
    report = doctor_pet(source, codex_home)
    if report.ok:
        return report
    return install_pet(source, codex_home, reason="repair")


def uninstall_pet(codex_home: str | Path | None = None) -> DoctorReport:
    home, destination = _safe_destination(codex_home or default_codex_home())
    if not destination.exists():
        return DoctorReport("missing", str(destination), differences=["nothing to uninstall"])
    with _install_lock(home):
        backup = _backup_path(home, "uninstall")
        backup.parent.mkdir(parents=True, exist_ok=True)
        destination.replace(backup)
    return DoctorReport("missing", str(destination), backup=str(backup))

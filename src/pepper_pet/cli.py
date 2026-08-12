"""Command-line interface for validation, installation, repair, and packaging."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .installer import doctor_pet, install_pet, repair_pet, uninstall_pet
from .release import build_release, write_checksums
from .validator import validate_pet


def _emit(data: object, as_json: bool) -> None:
    if hasattr(data, "to_dict"):
        payload = data.to_dict()  # type: ignore[union-attr]
    elif isinstance(data, dict):
        payload = data
    else:
        payload = data.__dict__  # type: ignore[union-attr]
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    else:
        print(json.dumps(payload, ensure_ascii=False, default=str))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pepper-pet",
        description="Validate, install, diagnose, repair, and package the Pepper Codex v2 pet.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    subcommands = parser.add_subparsers(dest="command", required=True)

    validate = subcommands.add_parser(
        "validate", help="Validate a source or installed pet directory"
    )
    validate.add_argument("path", nargs="?", default="pet")
    validate.add_argument("--json", action="store_true")

    doctor = subcommands.add_parser("doctor", help="Diagnose the installed Pepper pet")
    doctor.add_argument("--source", default=None)
    doctor.add_argument("--codex-home", default=None)
    doctor.add_argument("--json", action="store_true")

    install = subcommands.add_parser(
        "install", help="Install with validation and backup-first replacement"
    )
    install.add_argument("--source", default="pet")
    install.add_argument("--codex-home", default=None)
    install.add_argument("--json", action="store_true")

    repair = subcommands.add_parser(
        "repair", help="Repair a missing, corrupt, or outdated installation"
    )
    repair.add_argument("--source", default="pet")
    repair.add_argument("--codex-home", default=None)
    repair.add_argument("--json", action="store_true")

    uninstall = subcommands.add_parser(
        "uninstall", help="Move the installed pet into a recoverable backup"
    )
    uninstall.add_argument("--codex-home", default=None)
    uninstall.add_argument("--json", action="store_true")

    package = subcommands.add_parser("package", help="Build a deterministic release archive")
    package.add_argument("--repo-root", default=".")
    package.add_argument("--out-dir", default="dist")
    package.add_argument("--version", default=f"v{__version__}")
    package.add_argument("--json", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "validate":
            report = validate_pet(args.path)
            _emit(report, args.json)
            return 0 if report.ok else 1
        if args.command == "doctor":
            report = doctor_pet(args.source, args.codex_home)
            _emit(report, args.json)
            return {"healthy": 0, "missing": 2, "invalid": 3, "outdated": 4}[report.status]
        if args.command == "install":
            report = install_pet(args.source, args.codex_home)
            _emit(report, args.json)
            return 0
        if args.command == "repair":
            report = repair_pet(args.source, args.codex_home)
            _emit(report, args.json)
            return 0 if report.ok else 1
        if args.command == "uninstall":
            report = uninstall_pet(args.codex_home)
            _emit(report, args.json)
            return 0
        if args.command == "package":
            root = Path(args.repo_root)
            artifact = build_release(root, args.out_dir, args.version)
            checksums = write_checksums(root, artifact)
            _emit(
                {
                    "ok": True,
                    "artifact": str(artifact.path),
                    "sha256": artifact.sha256,
                    "size": artifact.size,
                    "manifest": str(artifact.manifest_path),
                    "checksums": str(checksums),
                },
                args.json,
            )
            return 0
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"pepper-pet: {exc}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

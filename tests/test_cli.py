from __future__ import annotations

import json

from pepper_pet.cli import main
from tests.helpers import make_pet, make_release_scaffold


def test_validate_command_emits_json(tmp_path, capsys):
    pet_dir = make_pet(tmp_path)

    exit_code = main(["validate", str(pet_dir), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["ok"] is True


def test_doctor_uses_distinct_missing_exit_code(tmp_path, capsys):
    exit_code = main(["doctor", "--codex-home", str(tmp_path / "codex"), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert payload["status"] == "missing"


def test_install_repair_uninstall_commands(tmp_path, capsys):
    pet_dir = make_pet(tmp_path / "source")
    codex_home = tmp_path / "codex"

    assert main(["install", "--source", str(pet_dir), "--codex-home", str(codex_home)]) == 0
    capsys.readouterr()
    assert main(["repair", "--source", str(pet_dir), "--codex-home", str(codex_home)]) == 0
    capsys.readouterr()
    assert main(["uninstall", "--codex-home", str(codex_home)]) == 0


def test_package_command_writes_artifact(tmp_path, capsys):
    repo = make_release_scaffold(tmp_path / "repo")
    out = tmp_path / "dist"

    exit_code = main(
        [
            "package",
            "--repo-root",
            str(repo),
            "--out-dir",
            str(out),
            "--version",
            "v0.1.0",
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["ok"] is True
    assert out.joinpath("pepper-carrot-codex-pet-v0.1.0.zip").is_file()


def test_validate_failure_and_package_error_use_nonzero_exit(tmp_path, capsys):
    missing_exit = main(["validate", str(tmp_path / "missing"), "--json"])
    missing_payload = json.loads(capsys.readouterr().out)

    package_exit = main(
        [
            "package",
            "--repo-root",
            str(tmp_path),
            "--version",
            "../unsafe",
        ]
    )
    error = capsys.readouterr().err

    assert missing_exit == 1
    assert missing_payload["ok"] is False
    assert package_exit == 1
    assert "Version" in error

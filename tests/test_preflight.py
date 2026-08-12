from __future__ import annotations

from tools.preflight import _version_problems


def _write_version_files(root, version: str = "0.1.0") -> None:
    (root / "src" / "pepper_pet").mkdir(parents=True)
    (root / "pyproject.toml").write_text(
        f'[project]\nname = "pepper"\nversion = "{version}"\n',
        encoding="utf-8",
    )
    (root / "src" / "pepper_pet" / "__init__.py").write_text(
        f'__version__ = "{version}"\n',
        encoding="utf-8",
    )
    (root / "CHANGELOG.md").write_text(
        f"# Changelog\n\n## {version} - 2026-07-30\n",
        encoding="utf-8",
    )
    (root / "RELEASE_NOTES.md").write_text(
        f"# Pepper v{version}\n",
        encoding="utf-8",
    )


def test_version_preflight_accepts_consistent_release(tmp_path):
    _write_version_files(tmp_path)

    assert _version_problems(tmp_path, "v0.1.0") == []


def test_version_preflight_reports_tag_package_and_changelog_drift(tmp_path):
    _write_version_files(tmp_path)
    (tmp_path / "src" / "pepper_pet" / "__init__.py").write_text(
        '__version__ = "9.9.9"\n',
        encoding="utf-8",
    )
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
    (tmp_path / "RELEASE_NOTES.md").write_text(
        "# Pepper v9.9.9\n",
        encoding="utf-8",
    )

    problems = _version_problems(tmp_path, "v0.2.0")

    assert len(problems) == 4
    assert any("package version" in problem for problem in problems)
    assert any("release version" in problem for problem in problems)
    assert any("CHANGELOG" in problem for problem in problems)
    assert any("RELEASE_NOTES" in problem for problem in problems)

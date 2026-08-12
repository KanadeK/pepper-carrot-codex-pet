"""Shared data contracts for the Pepper pet toolchain."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

CELL_WIDTH = 192
CELL_HEIGHT = 208
COLUMNS = 8
ROWS = 11
ATLAS_SIZE = (COLUMNS * CELL_WIDTH, ROWS * CELL_HEIGHT)


@dataclass(frozen=True)
class RowSpec:
    state: str
    frames: int
    row: int


ROW_SPECS = (
    RowSpec("idle", 6, 0),
    RowSpec("running-right", 8, 1),
    RowSpec("running-left", 8, 2),
    RowSpec("waving", 4, 3),
    RowSpec("jumping", 5, 4),
    RowSpec("failed", 8, 5),
    RowSpec("waiting", 6, 6),
    RowSpec("running", 6, 7),
    RowSpec("review", 6, 8),
    RowSpec("look-row-9", 8, 9),
    RowSpec("look-row-10", 8, 10),
)

ANIMATION_CELL_COUNT = sum(spec.frames for spec in ROW_SPECS)
NEUTRAL_LOOK_FRAME = (0, 6)
NEUTRAL_LOOK_CELL_COUNT = 1
USED_CELL_COUNT = ANIMATION_CELL_COUNT + NEUTRAL_LOOK_CELL_COUNT
RESERVED_EMPTY_CELL_COUNT = COLUMNS * ROWS - USED_CELL_COUNT


@dataclass(frozen=True)
class Issue:
    code: str
    severity: Literal["error", "warning"]
    message: str
    location: str | None = None


@dataclass
class ValidationReport:
    ok: bool
    pet_dir: str
    issues: list[Issue] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def errors(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "pet_dir": self.pet_dir,
            "issues": [asdict(issue) for issue in self.issues],
            "metadata": self.metadata,
        }


@dataclass
class DoctorReport:
    status: Literal["healthy", "missing", "invalid", "outdated"]
    destination: str
    validation: ValidationReport | None = None
    differences: list[str] = field(default_factory=list)
    backup: str | None = None

    @property
    def ok(self) -> bool:
        return self.status == "healthy"

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "status": self.status,
            "destination": self.destination,
            "validation": self.validation.to_dict() if self.validation else None,
            "differences": self.differences,
            "backup": self.backup,
        }

from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path

from pepper_pet.model import ATLAS_SIZE, CELL_HEIGHT, CELL_WIDTH, ROW_SPECS

ROOT = Path(__file__).resolve().parents[1]


class OutlineParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.headings: list[str] = []
        self._heading: str | None = None
        self._parts: list[str] = []
        self.local_assets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag in {"h1", "h2"}:
            self._heading = tag
            self._parts = []
        if tag in {"img", "script"} and values.get("src"):
            self.local_assets.append(values["src"])
        if tag == "link" and values.get("rel") == "stylesheet" and values.get("href"):
            self.local_assets.append(values["href"])

    def handle_data(self, data: str) -> None:
        if self._heading:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == self._heading:
            self.headings.append(" ".join("".join(self._parts).split()))
            self._heading = None
            self._parts = []


def test_browser_state_data_matches_python_contract():
    data = json.loads((ROOT / "site" / "states.json").read_text(encoding="utf-8"))

    assert (data["atlas"]["width"], data["atlas"]["height"]) == ATLAS_SIZE
    assert data["cell"] == {"width": CELL_WIDTH, "height": CELL_HEIGHT}
    assert data["atlas"]["columns"] == 8
    assert data["atlas"]["rows"] == 11
    for expected, browser_state in zip(ROW_SPECS[:9], data["states"][:9], strict=True):
        assert browser_state["id"] == expected.state
        assert browser_state["row"] == expected.row
        assert browser_state["frames"] == expected.frames
    assert data["states"][9]["rows"] == [9, 10]
    assert data["states"][9]["frames"] == 16
    assert sum(spec.frames for spec in ROW_SPECS) == 73


def test_page_outline_and_local_assets_are_complete():
    parser = OutlineParser()
    parser.feed((ROOT / "site" / "index.html").read_text(encoding="utf-8"))

    assert parser.headings[0] == "Pepper joins Codex."
    assert len(parser.headings) == 6
    for relative in parser.local_assets:
        assert (ROOT / "site" / relative).is_file(), relative


def test_public_source_avoids_placeholder_and_scroll_handler_patterns():
    sources = [
        (ROOT / "site" / name).read_text(encoding="utf-8")
        for name in ("index.html", "styles.css", "app.js")
    ]
    combined = "\n".join(sources)

    assert "\u2014" not in combined
    assert "\u2013" not in combined
    assert "lorem ipsum" not in combined.casefold()
    assert "javascript:void" not in combined.casefold()
    assert 'addEventListener("scroll"' not in combined
    assert 'fetch("states.json")' in combined
    assert 'const atlasUrl = "assets/spritesheet.webp"' in combined

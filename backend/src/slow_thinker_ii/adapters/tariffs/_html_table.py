"""Bounded HTML table extraction preserves merged pricing cells without executing page content."""

import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import override


@dataclass
class Cell:
    rows: int
    columns: int
    text: list[str] = field(default_factory=list[str])


class PricingTable(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[Cell]] = []
        self.text: list[str] = []
        self.cell: Cell | None = None
        self.tables = self.depth = self.nodes = 0

    @override
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.nodes += 1
        if self.nodes > 10_000:
            raise ValueError("Pricing HTML exceeds its structural bound")
        if tag == "table":
            self.tables += 1
            self.depth += 1
            if self.tables != 1 or self.depth != 1:
                raise ValueError("Unsupported pricing table structure")
        if self.depth and tag == "tr":
            self.rows.append([])
        if self.depth and tag in ("td", "th"):
            if self.cell is not None or not self.rows:
                raise ValueError("Malformed pricing table cell")
            properties = dict(attrs)
            self.cell = Cell(span(properties.get("rowspan")), span(properties.get("colspan")))
            self.rows[-1].append(self.cell)
        if tag == "br":
            self.handle_data(" ")

    @override
    def handle_endtag(self, tag: str) -> None:
        if tag in ("td", "th"):
            self.cell = None
        if tag == "table":
            self.depth -= 1

    @override
    def handle_data(self, data: str) -> None:
        self.text.append(data)
        if self.cell is not None:
            self.cell.text.append(data)

    def grid(self) -> list[list[str]]:
        if self.depth or self.cell is not None or not 1 <= len(self.rows) <= 64:
            raise ValueError("Incomplete or excessive pricing table")
        cells: dict[tuple[int, int], str] = {}
        for row, values in enumerate(self.rows):
            column = 0
            for cell in values:
                while (row, column) in cells:
                    column += 1
                place(cells, row, column, cell)
                column += cell.columns
        width = max(column for _, column in cells) + 1
        if width != 5 or any(row >= len(self.rows) for row, _ in cells):
            raise ValueError("Unsupported pricing table dimensions")
        if any((r, c) not in cells for r in range(len(self.rows)) for c in range(width)):
            raise ValueError("Incomplete pricing grid")
        return [[cells[(row, column)] for column in range(width)] for row in range(len(self.rows))]


def span(value: str | None) -> int:
    if value is None:
        return 1
    if not value.isascii() or not value.isdigit() or not 1 <= int(value) <= 64:
        raise ValueError("Unsupported pricing cell span")
    return int(value)


def text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"\(\d+\)", "", value)).strip()


def place(cells: dict[tuple[int, int], str], row: int, column: int, cell: Cell) -> None:
    if row + cell.rows > 64 or column + cell.columns > 5:
        raise ValueError("Pricing grid exceeds its bound")
    for r in range(row, row + cell.rows):
        for c in range(column, column + cell.columns):
            if (r, c) in cells:
                raise ValueError("Overlapping pricing cells")
            cells[(r, c)] = text("".join(cell.text))

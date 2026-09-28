"""Require independent line and branch coverage, including uncovered modules."""

import json
from pathlib import Path

from tooling.quality.json_shapes import json_object


def require_coverage(path: Path) -> None:
    report: object = json.loads(path.read_text())
    if not json_object(report):
        raise ValueError("Invalid coverage report")
    totals: object = report.get("totals")
    if not json_object(totals):
        raise ValueError("Missing coverage totals")
    for covered, total in (
        ("covered_lines", "num_statements"),
        ("covered_branches", "num_branches"),
    ):
        count, possible = totals.get(covered), totals.get(total)
        if not isinstance(count, int) or not isinstance(possible, int) or possible <= 0:
            raise ValueError(f"Missing measurable coverage: {total}")
        if count * 100 < possible * 90:
            raise ValueError(f"{covered} must reach 90% independently")

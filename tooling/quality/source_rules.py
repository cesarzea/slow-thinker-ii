"""Check physical unit sizes and source placement."""

import ast
from pathlib import Path

from tooling.quality.inventory import Locations, approved_path, source_files


def python_sizes(path: str, text: str) -> list[str]:
    issues: list[str] = []
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            end = node.end_lineno or node.lineno
            if end - node.lineno + 1 > 30:
                issues.append(f"{path}:{node.lineno}: function exceeds 30 physical lines")
    return issues


def check_source(root: Path, locations: Locations) -> list[str]:
    issues: list[str] = []
    for file in source_files(root, locations):
        path = file.relative_to(root).as_posix()
        if not approved_path(path, locations):
            issues.append(f"{path}: source outside declared capabilities")
        content = file.read_text()
        if len(content.splitlines()) > 150:
            issues.append(f"{path}: file exceeds 150 physical lines")
        if file.suffix == ".py":
            issues.extend(python_sizes(path, content))
    return issues

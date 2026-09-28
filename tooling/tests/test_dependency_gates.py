"""Production dependency rules must reject deliberate violations, not just valid code."""

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def dependency_workspace(tmp_path: Path) -> Path:
    (tmp_path / "frontend/src/features/example").mkdir(parents=True)
    (tmp_path / "node_modules").symlink_to(ROOT / "node_modules", target_is_directory=True)
    for name in (".dependency-cruiser.cjs", "package.json", "tsconfig.json", "vitest.config.ts"):
        shutil.copy(ROOT / name, tmp_path / name)
    for name in ("tsconfig.json", "package.json"):
        shutil.copy(ROOT / "frontend" / name, tmp_path / "frontend" / name)
    return tmp_path


@pytest.mark.parametrize(
    "source, diagnostic",
    [
        (
            "import {value} from './features/example/private.ts'; export {value};",
            "public-entries-only",
        ),
        ("import {test} from 'vitest'; export {test};", "no-dev-in-production"),
        ("import {value} from 'missing-package'; export {value};", "no-unresolved-imports"),
        ("import {value} from './b.ts'; export const a = value;", "no-cycles"),
    ],
)
def test_dependency_violations(dependency_workspace: Path, source: str, diagnostic: str) -> None:
    directory = dependency_workspace / "frontend/src"
    (directory / "a.ts").write_text(source)
    (directory / "b.ts").write_text("import {a} from './a.ts'; export const value = a;")
    (directory / "features/example/private.ts").write_text("export const value = 1;")
    result = subprocess.run(
        [
            str(ROOT / "node_modules/.bin/depcruise"),
            "frontend/src",
            "--config",
            ".dependency-cruiser.cjs",
        ],
        cwd=dependency_workspace,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert diagnostic in result.stdout


def test_knip_reports_unused_source(dependency_workspace: Path) -> None:
    shutil.copy(ROOT / "knip.json", dependency_workspace / "knip.json")
    (dependency_workspace / "frontend/src/orphan.ts").write_text("export const unused = 1;")
    result = subprocess.run(
        [str(ROOT / "node_modules/.bin/knip"), "--include", "files", "--no-progress"],
        cwd=dependency_workspace,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "frontend/src/orphan.ts" in result.stdout

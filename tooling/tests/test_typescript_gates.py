"""Verify strict TypeScript and linting with the repository configuration."""

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    (tmp_path / "frontend/src").mkdir(parents=True)
    (tmp_path / "node_modules").symlink_to(ROOT / "node_modules", target_is_directory=True)
    for name in ("eslint.config.js", "package.json"):
        shutil.copy(ROOT / name, tmp_path / name)
    shutil.copy(ROOT / "frontend/tsconfig.json", tmp_path / "frontend/tsconfig.json")
    return tmp_path


@pytest.mark.parametrize(
    "source, diagnostic",
    [
        ("export const value: any = 1;\n", "no-explicit-any"),
        ("export default 1;\n", "Use named exports"),
        (
            "export function long(): number {\n" + "\n" * 30 + "return 1;\n}\n",
            "max-lines-per-function",
        ),
    ],
)
def test_eslint_rejects(workspace: Path, source: str, diagnostic: str) -> None:
    fixture = workspace / "frontend/src/violation.ts"
    fixture.write_text(source)
    result = subprocess.run(
        [str(ROOT / "node_modules/.bin/eslint"), "--max-warnings", "0", str(fixture)],
        cwd=workspace,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert diagnostic in result.stdout


def test_typescript_rejects_wrong_type(workspace: Path) -> None:
    (workspace / "frontend/src/violation.ts").write_text("export const value: number = 'invalid';")
    result = subprocess.run(
        [str(ROOT / "node_modules/.bin/tsc"), "--noEmit", "-p", "frontend/tsconfig.json"],
        cwd=workspace,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "TS2322" in result.stdout


def test_prettier_rejects_unformatted_source(workspace: Path) -> None:
    shutil.copy(ROOT / ".prettierrc.json", workspace / ".prettierrc.json")
    (workspace / "frontend/src/violation.ts").write_text("export const value=1;")
    result = subprocess.run(
        [str(ROOT / "node_modules/.bin/prettier"), "--check", "frontend/src/violation.ts"],
        cwd=workspace,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "violation.ts" in result.stderr

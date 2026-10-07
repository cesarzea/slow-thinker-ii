"""The standalone inspection, run in this process against unpacked distributions.

The adapter runs the script with each environment's interpreter; running the same file here,
under its package's name, measures it with this process's coverage.
"""

import json
import runpy
import sys
from pathlib import Path
from zipfile import ZipFile

import pytest
from slow_thinker_ii.adapters import installations

from .catalogs import sample_wheel
from .wheels import ROUTER_DECLARATION, component_files

INSPECTION = Path(str(installations.__file__)).with_name("_inspect.py")
NAME = "slow_thinker_ii.adapters.installations._inspect"


def unpacked(directory: Path, files: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
    """`sample-agent` 1.0 unpacked into a directory placed first on the module path."""
    site = directory / "site"
    with ZipFile(sample_wheel(directory, files)) as archive:
        archive.extractall(site)
    monkeypatch.setattr(sys, "path", [str(site), *sys.path])


def inspect(
    monkeypatch: pytest.MonkeyPatch, version: str = "1.0", module: str = "sample_agent"
) -> None:
    monkeypatch.setattr(sys, "argv", ["_inspect.py", "sample-agent", version, module])
    runpy.run_path(str(INSPECTION), run_name=NAME)


def test_the_inspection_reports_the_shipped_declaration_without_importing_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    files = component_files("sample_agent")
    files["sample_agent/__init__.py"] = "raise RuntimeError('component code ran')\n"
    unpacked(tmp_path, files, monkeypatch)
    inspect(monkeypatch)
    report = json.loads(capsys.readouterr().out)
    assert report["declaration"] == ROUTER_DECLARATION
    assert report["packages"]["sample-agent"] == "1.0"
    assert report["python"] == sys.version and isinstance(report["platform"], str)
    assert "sample_agent" not in sys.modules


@pytest.mark.parametrize(
    "version,module,missing,diagnostic",
    [
        ("2.0", "sample_agent", None, "version differs from registration"),
        ("1.0", "other_module", None, "has no __main__"),
        ("1.0", "sample_agent", "sample_agent/__main__.py", "has no __main__"),
        ("1.0", "sample_agent", "sample_agent/component.json", "ships no component.json"),
    ],
)
def test_the_inspection_refuses_a_false_registration(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    version: str,
    module: str,
    missing: str | None,
    diagnostic: str,
) -> None:
    files = component_files("sample_agent")
    if missing is not None:
        del files[missing]
    unpacked(tmp_path, files, monkeypatch)
    with pytest.raises(ValueError, match=diagnostic):
        inspect(monkeypatch, version, module)

"""Exercise the standalone inspection program against actual installed distributions."""

import json
import runpy
import sys
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.installations import ComponentRegistration
from support.installations import new_catalog
from support.wheels import lockfile, wheel

SCRIPT = (
    Path(__file__).resolve().parents[2] / "src/slow_thinker_ii/adapters/installations/_inspect.py"
)


@pytest.fixture
def inspection_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    base = wheel(tmp_path, "probe-base", "1.0", "class Base: pass\nclass Other: pass\n")
    child = wheel(
        tmp_path,
        "probe-child",
        "1.0",
        "from probe_base import Base\nclass Child(Base): pass\nForeign=Base\nVALUE=7\n",
        ("probe-base==1.0",),
    )
    catalog = new_catalog(tmp_path)
    registration = ComponentRegistration(
        type_id="probe.child",
        type_version="1",
        distribution="probe-child",
        version="1.0",
        entry_point="probe_child:Child",
    )
    record = catalog.prepare(lockfile(tmp_path, (base, child)), tmp_path, registration)
    site = next(
        catalog.interpreter(record.identity).parent.parent.glob("lib/python*/site-packages")
    )
    monkeypatch.setattr(sys, "path", [str(site), *sys.path])
    monkeypatch.setattr(sys, "dont_write_bytecode", True)


def probe(monkeypatch: pytest.MonkeyPatch, version: str, entry: str, base: str) -> None:
    arguments = ["inspect", "probe-child", version, entry, "probe-base", "1.0", base]
    monkeypatch.setattr(sys, "argv", arguments)
    try:
        runpy.run_path(str(SCRIPT), run_name="__main__")
    finally:
        sys.modules.pop("probe_child", None)
        sys.modules.pop("probe_base", None)


def test_probe_accepts_owned_class_and_real_ancestry(
    inspection_path: None,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    del inspection_path
    probe(monkeypatch, "1.0", "probe_child:Child", "probe_base:Base")
    result: object = json.loads(capsys.readouterr().out)
    assert isinstance(result, dict) and result["base_entry_point"] == "probe_base:Base"


@pytest.mark.parametrize(
    "version,entry,base,diagnostic",
    [
        ("2.0", "probe_child:Child", "probe_base:Base", "version differs"),
        ("1.0", "probe_child:VALUE", "probe_base:Base", "public class"),
        ("1.0", "probe_child:Foreign", "probe_base:Base", "does not belong"),
        ("1.0", "probe_child:Child", "probe_base:Other", "does not inherit"),
    ],
)
def test_probe_rejects_false_registration(
    inspection_path: None,
    monkeypatch: pytest.MonkeyPatch,
    version: str,
    entry: str,
    base: str,
    diagnostic: str,
) -> None:
    del inspection_path
    with pytest.raises(ValueError, match=diagnostic):
        probe(monkeypatch, version, entry, base)

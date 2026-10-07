"""Installer options, URLs, ranges and ambiguous lock entries never reach uv."""

import sys
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.installations import InstallationCatalog

from .catalogs import REGISTRATION

HASH = "a" * 64


@pytest.mark.parametrize(
    "text",
    [
        "",
        "# empty",
        "sample-agent==1.0",
        "sample-agent>=1.0 --hash=sha256:" + HASH,
        "sample-agent==1.* --hash=sha256:" + HASH,
        "--index-url=https://example.org",
        "sample-agent @ https://example.org/code.whl",
        "sample-agent[extra]==1.0",
        "sample-agent==1.0 --hash=sha512:" + HASH,
        "sample-agent==1.0;python_version>'3'",
        f"sample-agent==1.0 --hash=sha256:{HASH}\nSample_Agent==1.0 --hash=sha256:{HASH}",
    ],
)
def test_non_exact_or_ambiguous_locks_are_refused_before_installing(
    tmp_path: Path, text: str
) -> None:
    lock = tmp_path / "requirements.txt"
    lock.write_text(text)
    never_run = Path(sys.executable)  # the lock is refused before any tool runs
    catalog = InstallationCatalog(tmp_path / "installations", never_run, never_run)
    with pytest.raises(ValueError):
        catalog.prepare(lock, tmp_path, REGISTRATION)
    assert not (tmp_path / "installations").exists()


def test_a_lock_without_compatible_wheels_is_refused_before_installing(tmp_path: Path) -> None:
    lock = tmp_path / "requirements.txt"
    lock.write_text(f"# generated\nsample_agent==1.0 \\\n    --hash=sha256:{HASH}\n")
    never_run = Path(sys.executable)
    catalog = InstallationCatalog(tmp_path / "installations", never_run, never_run)
    with pytest.raises(ValueError, match="one compatible regular wheel for sample-agent"):
        catalog.prepare(lock, tmp_path, REGISTRATION)

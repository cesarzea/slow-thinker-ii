"""Installer options, URLs, ranges and ambiguous lock entries cannot reach uv."""

import pytest
from slow_thinker_ii.adapters.installations import read_lock

HASH = "a" * 64


@pytest.mark.parametrize(
    "text",
    [
        "",
        "# empty",
        "package==1",
        "package>=1 --hash=sha256:" + HASH,
        "package==1.* --hash=sha256:" + HASH,
        "--index-url=https://example.org",
        "package @ https://example.org/code.whl",
        "package[extra]==1",
        "package==1 --hash=sha512:" + HASH,
        "package==1;python_version>'3'",
        f"package==1 --hash=sha256:{HASH}\nPackage==1 --hash=sha256:{HASH}",
    ],
)
def test_non_exact_or_ambiguous_locks_are_rejected(text: str) -> None:
    with pytest.raises(ValueError):
        read_lock(text)


def test_uv_generated_multiline_lock_preserves_exact_hashes() -> None:
    packages = read_lock(f"# generated\nsample_agent==1.1 \\\n    --hash=sha256:{HASH}\n")
    assert packages[0].name == "sample-agent"
    assert packages[0].version == "1.1"
    assert packages[0].hashes == {HASH}

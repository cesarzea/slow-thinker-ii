"""Deliberate violations establish that the documentation gate rejects them."""

from pathlib import Path

from tooling.quality.documentation import check_documentation, maintained_documents


def write(root: Path, path: str, text: str) -> None:
    file = root / path
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(text)


def indexed_repository(root: Path) -> None:
    write(root, "docs/README.md", "[Guide](guide.md) · [Module](../src/readme.md#use)\n")
    write(root, "docs/guide.md", "See the [index](README.md) and [site](https://example.com).\n")
    write(root, "src/readme.md", "Back to the [guide](../docs/guide.md).\n")


def test_accepts_an_indexed_repository(tmp_path: Path) -> None:
    indexed_repository(tmp_path)
    assert check_documentation(tmp_path) == []


def test_rejects_a_document_missing_from_the_index(tmp_path: Path) -> None:
    indexed_repository(tmp_path)
    write(tmp_path, "docs/orphan.md", "Nobody links here.\n")
    assert check_documentation(tmp_path) == ["docs/orphan.md: missing from docs/README.md"]


def test_rejects_a_broken_link(tmp_path: Path) -> None:
    indexed_repository(tmp_path)
    write(tmp_path, "docs/guide.md", "See [gone](missing.md#part).\n")
    assert check_documentation(tmp_path) == ["docs/guide.md: broken link missing.md#part"]


def test_requires_the_index(tmp_path: Path) -> None:
    write(tmp_path, "docs/guide.md", "Text.\n")
    assert check_documentation(tmp_path)[0] == "docs/README.md: documentation index is missing"


def test_ignores_archives_and_generated_directories(tmp_path: Path) -> None:
    indexed_repository(tmp_path)
    for path in ("docs/archive/old.md", "node_modules/x/readme.md", ".pytest_cache/README.md"):
        write(tmp_path, path, "[broken](nowhere.md)\n")
    write(tmp_path, ".github/template.md", "Text.\n")
    names = [path.relative_to(tmp_path).as_posix() for path in maintained_documents(tmp_path)]
    assert names == [".github/template.md", "docs/README.md", "docs/guide.md", "src/readme.md"]

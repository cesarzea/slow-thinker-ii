"""Check that the documentation index lists every maintained document and links resolve."""

import re
from collections.abc import Iterator
from pathlib import Path

INDEX = "docs/README.md"
SKIPPED = frozenset(
    {"archive", "coverage", "dist", "mutants", "node_modules", "playwright-report", "test-results"}
)
LINK = re.compile(r"\]\(([^)\s]+)\)")


def skipped(directories: tuple[str, ...]) -> bool:
    hidden = any(name.startswith(".") and name != ".github" for name in directories)
    return hidden or bool(SKIPPED.intersection(directories))


def maintained_documents(root: Path) -> list[Path]:
    """Markdown documents outside archives, hidden, dependency and generated directories."""
    return sorted(
        path for path in root.rglob("*.md") if not skipped(path.relative_to(root).parts[:-1])
    )


def local_targets(document: Path) -> Iterator[tuple[str, Path]]:
    """Each relative link of a document and the file it points to."""
    for link in LINK.findall(document.read_text()):
        target = link.split("#", 1)[0]
        if not target or ":" in target or target.startswith("/"):
            continue
        yield link, (document.parent / target).resolve()


def broken_links(root: Path, documents: list[Path]) -> list[str]:
    issues: list[str] = []
    for document in documents:
        for link, target in local_targets(document):
            if not target.exists():
                path = document.relative_to(root).as_posix()
                issues.append(f"{path}: broken link {link}")
    return issues


def unindexed(root: Path, documents: list[Path]) -> list[str]:
    index = root / INDEX
    if not index.exists():
        return [f"{INDEX}: documentation index is missing"]
    listed = {target for _, target in local_targets(index)}
    return [
        f"{document.relative_to(root).as_posix()}: missing from {INDEX}"
        for document in documents
        if document != index and document.resolve() not in listed
    ]


def check_documentation(root: Path) -> list[str]:
    documents = maintained_documents(root)
    return unindexed(root, documents) + broken_links(root, documents)

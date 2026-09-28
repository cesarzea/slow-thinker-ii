"""Accept complete, hash-pinned requirements without installer directives or URLs."""

import re
from dataclasses import dataclass

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name


@dataclass(frozen=True)
class LockedPackage:
    name: str
    version: str
    hashes: frozenset[str]


def _package(line: str) -> LockedPackage:
    identity, *tokens = line.split()
    requirement = Requirement(identity)
    versions = tuple(requirement.specifier)
    if requirement.url or requirement.extras or requirement.marker or len(versions) != 1:
        raise ValueError("Only exact package requirements are supported")
    version = versions[0]
    if version.operator != "==" or "*" in version.version:
        raise ValueError("A package version must be exact")
    if not tokens or any(not re.fullmatch(r"--hash=sha256:[a-f0-9]{64}", t) for t in tokens):
        raise ValueError("Every package requires SHA-256 wheel hashes")
    return LockedPackage(
        canonicalize_name(requirement.name),
        version.version,
        frozenset(token.removeprefix("--hash=sha256:") for token in tokens),
    )


def read_lock(text: str) -> tuple[LockedPackage, ...]:
    lines = (line.split("#", 1)[0].strip() for line in text.replace("\\\n", " ").splitlines())
    packages = tuple(_package(line) for line in lines if line)
    if not packages or len({package.name for package in packages}) != len(packages):
        raise ValueError("A lock requires uniquely named packages")
    return packages

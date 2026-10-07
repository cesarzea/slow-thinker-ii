"""Keep dependencies, generated output and private material out of snapshots."""

from fnmatch import fnmatchcase
from pathlib import PurePosixPath

EXCLUDED_DIRECTORIES = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".cache",
        ".local",
        ".venv",
        "venv",
        "env",
        "node_modules",
        "site-packages",
        "vendor",
        "bower_components",
        "packages",
        "__pycache__",
        "dist",
        "build",
        "coverage",
        "mutants",
        "bin",
        "obj",
        "target",
        ".idea",
        ".vscode",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        ".import_linter_cache",
        ".jbeval",
        ".aws",
        ".ssh",
        ".gnupg",
        "private",
        "secrets",
        "credentials",
        "ext",
        "extjs",
        "sencha",
    }
)
SECRET_NAMES = frozenset(
    {
        ".envrc",
        ".npmrc",
        ".netrc",
        ".pypirc",
        ".git-credentials",
        "id_rsa",
        "id_dsa",
        "id_ecdsa",
        "id_ed25519",
        "credentials.json",
        "credentials.yaml",
        "credentials.yml",
    }
)
EXCLUDED_PATTERNS = (
    ".env",
    ".env.*",
    "*.env",
    "*.keys.json",
    "*.credentials.json",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "*.jks",
    "*.keystore",
    "*.min.js",
    "*.sarif",
    "*.bqrs",
    "jquery*",
    "bootstrap*.js",
    "bootstrap*.css",
    "bootstrap*.map",
)


def excluded(path: PurePosixPath) -> bool:
    if any(_excluded_directory(part.lower()) for part in path.parts[:-1]):
        return True
    name = path.name.lower()
    return name in SECRET_NAMES or any(fnmatchcase(name, pattern) for pattern in EXCLUDED_PATTERNS)


EXCLUDED_DIRECTORY_PREFIXES = ("ext-", "jquery", "bootstrap-", "bootstrap.")


def _excluded_directory(name: str) -> bool:
    return name in EXCLUDED_DIRECTORIES or name.startswith(EXCLUDED_DIRECTORY_PREFIXES)

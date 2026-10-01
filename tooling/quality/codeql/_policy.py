"""Require the pinned executable and its bundled query suites."""

import json
from pathlib import Path

from ._commands import run_command
from ._shapes import object_value, read_object, text_value
from ._types import CodeQLFailure

LANGUAGES = frozenset({"python", "javascript"})


def read_policy() -> tuple[str, dict[str, str]]:
    policy = read_object(Path(__file__).with_name("policy.json"))
    version = text_value(policy.get("bundle_version"), "Policy bundle_version")
    raw = object_value(policy.get("packs"), "Policy packs")
    if frozenset(raw) != LANGUAGES:
        raise CodeQLFailure("Policy must pin exactly the Python and JavaScript query packs")
    packs = {language: text_value(raw[language], "Query pack version") for language in LANGUAGES}
    return version, packs


def validate_languages(languages: tuple[str, ...]) -> None:
    if not languages or any(language not in LANGUAGES for language in languages):
        raise CodeQLFailure("Request Python and/or JavaScript analysis")
    if len(set(languages)) != len(languages):
        raise CodeQLFailure("CodeQL languages must not be duplicated")


def bundled_suites(
    executable: Path, languages: tuple[str, ...], root: Path, output: Path
) -> tuple[str, dict[str, Path]]:
    version, packs = read_policy()
    raw: object = json.loads(
        run_command((str(executable), "version", "--format=json"), root, output / "version.log")
    )
    if object_value(raw, "CodeQL version").get("version") != version:
        raise CodeQLFailure(f"CodeQL CLI version must be {version}; log: {output / 'version.log'}")
    suites = {language: _suite(executable, language, packs[language]) for language in languages}
    return version, suites


def _suite(executable: Path, language: str, version: str) -> Path:
    pack = executable.parent / "qlpacks" / "codeql" / f"{language}-queries" / version
    suite = pack / "codeql-suites" / f"{language}-security-and-quality.qls"
    if not suite.is_file():
        raise CodeQLFailure(f"Missing bundled {language} query suite: {suite}")
    return suite

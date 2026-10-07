"""Every configuration error names its location and never repeats a configured value."""

from pathlib import Path

import pytest
from slow_thinker_ii.bootstrap import load_configuration
from slow_thinker_ii.contracts import JsonValue, format_pointer
from support.examples import changed

from .configurations import local, without, written

PROVIDERS = ("llm", "providers")
MODEL = ("llm", "models", 0)
CASES: list[tuple[tuple[str | int, ...], JsonValue, str]] = [
    (("unknown",), 1, "/unknown: Extra inputs are not permitted"),
    (
        ("runtime", "max_active_runs"),
        "4",
        "/runtime/max_active_runs: Input should be a valid integer",
    ),
    (("runtime", "max_active_runs"), 0, "/runtime/max_active_runs: Input should be greater than"),
    (
        ("runtime", "host_startup_seconds"),
        0,
        "/runtime/host_startup_seconds: Input should be greater",
    ),
    ((*PROVIDERS, "mistral"), {}, "/llm/providers/mistral: Extra inputs are not permitted"),
    (
        (*PROVIDERS, "openai", "credential_env"),
        "openai-key",
        "/credential_env: String should match",
    ),
    ((*PROVIDERS, "openai", "api_key"), "sk-live-secret", "/openai/api_key: Extra inputs are not"),
    ((*PROVIDERS, "openai", "timeout_seconds"), 0, "/timeout_seconds: Input should be greater"),
    ((*PROVIDERS, "simulated"), {"base_url": "x"}, "/simulated/base_url: Extra inputs are not"),
    ((*MODEL, "provider"), "anthropic", "/llm/models/0/provider: “anthropic” is not a configured"),
    (("llm", "models", 1, "id"), "openai/gpt-6-luna", "/llm/models/1/id: “openai/gpt-6-luna” is"),
    ((*MODEL, "id"), "GPT", "/llm/models/0/id: String should match pattern"),
    ((*MODEL, "label"), "", "/llm/models/0/label: String should have at least 1 character"),
    ((*MODEL, "default_output_tokens"), 200_000, "/default_output_tokens: must not exceed"),
    ((*MODEL, "tariff", "rates", "input"), "-1", "/llm/models/0/tariff: "),
    ((*MODEL, "replies"), ["Hello"], "/llm/models/0/replies: only models of the simulated"),
    ((*MODEL, "temperature"), "always", "/llm/models/0/temperature: Input should be"),
    (("llm", "models"), [], "/llm/models: Tuple should have at least 1 item"),
    (("budgets", "daily_usd"), "one dollar", "/budgets/daily_usd: A budget must be a decimal"),
    (("budgets", "monthly_usd"), 5, "/budgets/monthly_usd: Input should be a valid string"),
    (("server", "public_url"), "http://127.0.0.1:8000/app", "/server/public_url: it must be an"),
    (("server", "public_url"), "ftp://127.0.0.1:8000", "/server/public_url: it must be an origin"),
    (("server", "public_url"), "http://me:hunter2@127.0.0.1", "/server/public_url: it must be"),
    (("server", "allowed_hosts"), [], "/server/allowed_hosts: Tuple should have at least 1 item"),
    (("components", "resolutions"), "abc", "/components/resolutions: Input should be a valid"),
]


@pytest.mark.parametrize("path,value,message", CASES)
def test_invalid_values_are_located_without_repeating_them(
    tmp_path: Path, path: tuple[str | int, ...], value: JsonValue, message: str
) -> None:
    document = changed(local(tmp_path), path, value)
    with pytest.raises(ValueError) as raised:
        load_configuration(written(tmp_path, document))
    text = str(raised.value)
    assert text.startswith("Invalid server configuration: ") and message in text
    for secret in ("sk-live-secret", "hunter2", "one dollar", "openai-key"):
        assert secret not in text


@pytest.mark.parametrize("path", [("database",), ("llm", "models", 0, "tariff"), ("budgets",)])
def test_required_members_are_named_when_missing(
    tmp_path: Path, path: tuple[str | int, ...]
) -> None:
    document = without(local(tmp_path), path)
    with pytest.raises(ValueError, match=f"{format_pointer(path)}: Field required"):
        load_configuration(written(tmp_path, document))


@pytest.mark.parametrize(
    "content,message",
    [
        (b'{"database": "a", "database": "b"}', "not valid JSON: Duplicate JSON property"),
        (b"[]", "Invalid server configuration: /: Input should be an object"),
        (b"{", "not valid JSON"),
        (b"\xff", "not valid JSON"),
        (b" " * 1_048_577, "must not exceed 1 MiB"),
    ],
)
def test_invalid_documents_are_refused(tmp_path: Path, content: bytes, message: str) -> None:
    path = tmp_path / "configuration.json"
    path.write_bytes(content)
    with pytest.raises(ValueError, match=message):
        load_configuration(path)


def test_missing_files_are_named(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Cannot read the server configuration .*missing.json"):
        load_configuration(tmp_path / "missing.json")


def test_the_legacy_key_file_is_never_opened(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    keys = tmp_path / "slow-thinker.keys.json"
    keys.write_text("{}")
    alias = tmp_path / "configuration.json"
    alias.symlink_to(keys)

    def forbidden(*arguments: object, **options: object) -> None:
        del arguments, options
        pytest.fail("A key file must not be opened")

    monkeypatch.setattr(Path, "open", forbidden)
    for path in (keys, alias):
        with pytest.raises(ValueError, match="slow-thinker.keys.json cannot be used"):
            load_configuration(path)

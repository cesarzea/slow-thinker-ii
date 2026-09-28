"""Credential lookup and network endpoints require explicit backend registration."""

import pytest
from slow_thinker_ii.adapters.preparation import EnvironmentSecrets, ServiceEndpoints
from slow_thinker_ii.application import PreparationRejected


@pytest.mark.parametrize("reference", ["unknown", "registered"])
@pytest.mark.parametrize("value", [None, ""])
def test_missing_secret_is_not_inferred(
    monkeypatch: pytest.MonkeyPatch, reference: str, value: str | None
) -> None:
    name = "SLOW_THINKER_TEST_SYNTHETIC_SECRET"
    monkeypatch.delenv(name, raising=False)
    if value is not None:
        monkeypatch.setenv(name, value)
    with pytest.raises(PreparationRejected, match="credential_unavailable"):
        EnvironmentSecrets({"registered": name}).resolve(reference)


def test_environment_mapping_is_copied(monkeypatch: pytest.MonkeyPatch) -> None:
    name = "SLOW_THINKER_TEST_SYNTHETIC_SECRET"
    monkeypatch.setenv(name, "synthetic-key")
    references = {"provider": name}
    source = EnvironmentSecrets(references)
    references.clear()
    assert source.resolve("provider") == "synthetic-key"
    assert "synthetic-key" not in repr(source)


@pytest.mark.parametrize("references", [{"": "VALID"}, {"p": "lowercase"}, {"p": "A/B"}])
def test_invalid_environment_mapping(references: dict[str, str]) -> None:
    with pytest.raises(ValueError, match="environment variable"):
        EnvironmentSecrets(references)


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost:8000/v1",
        "https://example.com/v1",
        "http://127.0.0.1/v1",
        "http://127.0.0.1:0/v1",
        "http://127.0.0.1:8000/other",
        "http://user:password@127.0.0.1:8000/v1",
        "http://127.0.0.1:8000/v1?q=1",
        "http://127.0.0.1:8000/v1#fragment",
        "http://127.0.0.1:99999/v1",
    ],
)
def test_remote_and_ambiguous_gateway_endpoints_rejected(url: str) -> None:
    with pytest.raises(ValueError):
        ServiceEndpoints(url)


def test_official_provider_and_explicit_local_fixtures() -> None:
    assert ServiceEndpoints("http://[::1]:8000/v1").provider == "https://api.openai.com/v1"
    local = ServiceEndpoints("http://127.0.0.1:8000/v1", "http://127.0.0.1:9000/v1")
    assert local.provider.endswith(":9000/v1")
    with pytest.raises(ValueError):
        ServiceEndpoints(local.gateway, "https://unapproved.example/v1")

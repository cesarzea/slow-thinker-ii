"""Operator access: the token by default, or no authentication on loopback-only servers."""

from collections.abc import Iterator, Mapping
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from slow_thinker_ii.bootstrap import AppOverrides, create_app, load_configuration
from slow_thinker_ii.contracts import JsonValue
from support.examples import changed

from .configurations import DevelopmentTargets, local, package_declarations, simulated, written

ACCESS = ("server", "operator_authentication")
HOSTS = ("server", "allowed_hosts")
REFUSED = (
    'Invalid server configuration: /server/operator_authentication: "none" requires every '
    "allowed host to be a loopback address."
)


class WatchedEnvironment(Mapping[str, str]):
    """An environment that records the name of every variable read from it."""

    def __init__(self, values: Mapping[str, str]) -> None:
        self._values = dict(values)
        self.read: list[str] = []

    def __getitem__(self, key: str) -> str:
        self.read.append(key)
        return self._values[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)


def test_the_token_is_required_unless_configured_otherwise(tmp_path: Path) -> None:
    absent = load_configuration(written(tmp_path, local(tmp_path)))
    explicit = load_configuration(written(tmp_path, changed(local(tmp_path), ACCESS, "token")))
    assert absent.server.operator_authentication == "token"
    assert explicit.server == absent.server


@pytest.mark.parametrize(
    "hosts",
    [["127.0.0.1:8000", "localhost:8000", "[::1]:8000"], ["127.0.0.1", "localhost", "[::1]"]],
)
def test_no_authentication_is_accepted_for_loopback_hosts(tmp_path: Path, hosts: list[str]) -> None:
    document = changed(changed(local(tmp_path), ACCESS, "none"), HOSTS, list[JsonValue](hosts))
    configuration = load_configuration(written(tmp_path, document))
    assert configuration.server.operator_authentication == "none"
    assert configuration.server.allowed_hosts == tuple(hosts)


@pytest.mark.parametrize(
    "host",
    [
        "192.168.1.20:8000",
        "slow-thinker.example",
        "127.0.0.2:8000",
        "localhost.example:8000",
        "[::2]:8000",
        "localhost:",
        "LOCALHOST:8000",
        "0.0.0.0:8000",
    ],
)
def test_no_authentication_requires_every_host_to_be_loopback(tmp_path: Path, host: str) -> None:
    document = changed(local(tmp_path), ACCESS, "none")
    document = changed(document, HOSTS, ["127.0.0.1:8000", host])
    with pytest.raises(ValueError) as raised:
        load_configuration(written(tmp_path, document))
    assert str(raised.value) == REFUSED


def test_other_access_modes_are_refused(tmp_path: Path) -> None:
    document = changed(local(tmp_path), ACCESS, "basic")
    with pytest.raises(ValueError, match="/server/operator_authentication: Input should be"):
        load_configuration(written(tmp_path, document))


def test_without_authentication_the_token_is_never_read(tmp_path: Path) -> None:
    document = changed(simulated(local(tmp_path)), ACCESS, "none")
    configuration = load_configuration(written(tmp_path, document))
    environment = WatchedEnvironment({"SLOW_THINKER_OPERATOR_TOKEN": "not even valid"})
    overrides = AppOverrides(package_declarations(), DevelopmentTargets())
    app = create_app(configuration, environment, overrides)
    assert "SLOW_THINKER_OPERATOR_TOKEN" not in environment.read
    local_peer = ("127.0.0.1", 50000)  # without a token, only this machine is served
    with TestClient(app, base_url="http://127.0.0.1:8000", client=local_peer) as client:
        assert client.get("/api/v2/catalog").status_code == 200
        assert client.get("/api/v2/graphs").json() == {"graphs": []}

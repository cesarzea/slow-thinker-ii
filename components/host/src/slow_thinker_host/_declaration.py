"""A component's packaged declaration and the startup check of its bootstrap against it."""

from importlib import resources

from ._bootstrap import Bootstrap
from ._json import JsonObject, decode_json, json_object
from ._schemas import validate_value


def read_declaration(package: str) -> JsonObject:
    """The `component.json` shipped inside the importable `package`."""
    text = resources.files(package).joinpath("component.json").read_text(encoding="utf-8")
    return json_object(decode_json(text))


def check_bootstrap(bootstrap: Bootstrap, declaration: JsonObject) -> None:
    """Raise ValueError unless the bootstrap names this component, a placement it declares
    and a configuration valid against its configuration schema."""
    reference = f"{declaration.get('type')}@{declaration.get('version')}"
    if bootstrap.component != reference:
        raise ValueError(f"The bootstrap names {bootstrap.component}, not {reference}")
    placements = declaration.get("placements")
    if not isinstance(placements, list) or bootstrap.position not in placements:
        raise ValueError(f"{reference} cannot be placed at position {bootstrap.position}")
    schema = declaration.get("config_schema")
    if not isinstance(schema, dict):
        raise ValueError(f"{reference} declares no configuration schema")
    try:
        validate_value(bootstrap.config, schema)
    except ValueError as error:
        raise ValueError(f"The {reference} configuration is invalid: {error}") from error

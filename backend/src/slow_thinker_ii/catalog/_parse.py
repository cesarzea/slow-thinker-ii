"""Parsing of component declarations, including the platform's own."""

from collections.abc import Iterable
from importlib.resources import files

from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json, json_object

from ._declaration import ComponentDeclaration, ServiceUse
from ._refs import ComponentRef
from ._rules import declaration_issues
from ._schemas import instance_problems
from ._values import items, mapping, member, text

DECLARATION_SCHEMA = "component-declaration-1.schema.json"
PLATFORM_COMPONENTS = ("trigger", "output")


class DeclarationError(ValueError):
    """A declaration that cannot be used; each issue names the offending field."""

    def __init__(self, issues: Iterable[str]) -> None:
        self.issues = tuple(issues)
        super().__init__("Invalid component declaration: " + "; ".join(self.issues))


def parse_declaration(document: JsonValue) -> ComponentDeclaration:
    schema = json_object(_package_document(DECLARATION_SCHEMA))
    problems = instance_problems(schema, document)
    if problems:
        raise DeclarationError(f"{where or 'declaration'}: {what}" for where, what in problems)
    declaration = json_object(document)
    issues = declaration_issues(declaration)
    if issues:
        raise DeclarationError(issues)
    return _declaration(declaration)


def platform_declarations() -> tuple[ComponentDeclaration, ...]:
    documents = (_package_document(f"{name}.component.json") for name in PLATFORM_COMPONENTS)
    return tuple(parse_declaration(document) for document in documents)


def _package_document(name: str) -> JsonValue:
    resource = files("slow_thinker_ii.catalog").joinpath("_data", name)
    return decode_json(resource.read_text(encoding="utf-8"))


def _declaration(declaration: JsonObject) -> ComponentDeclaration:
    ports = mapping(declaration.get("ports"))
    outputs = ports.get("outputs")
    outputs_from = ports.get("outputs_from")
    uses = items(declaration.get("uses"))
    return ComponentDeclaration(
        ref=ComponentRef(text(declaration.get("type")), text(declaration.get("version"))),
        label=text(declaration.get("label")),
        placements=frozenset(text(item) for item in items(declaration.get("placements"))),
        stateful=declaration.get("state") == "stateful",
        inputs=_names(ports.get("inputs")),
        outputs=None if outputs is None else _names(outputs),
        outputs_from=None if outputs_from is None else text(outputs_from),
        uses=tuple(
            ServiceUse(text(member(u, "service")), text(member(u, "pointer"))) for u in uses
        ),
        config_schema=mapping(declaration.get("config_schema")),
        initial_config=mapping(declaration.get("initial_config")),
        document=declaration,
    )


def _names(value: JsonValue) -> tuple[str, ...]:
    return tuple(text(item) for item in items(value))

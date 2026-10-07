"""Declaration rules beyond the JSON Schema of the declaration format."""

from collections.abc import Iterator

from slow_thinker_ii.contracts import JsonObject, format_pointer, value_at_pointer

from ._schema_pointers import is_string_array, local_target, references, schema_at
from ._schemas import metaschema_problems
from ._values import items, mapping, member, text

DRAFT_2020_12 = "https://json-schema.org/draft/2020-12/schema"


def declaration_issues(declaration: JsonObject) -> list[str]:
    schema = mapping(declaration.get("config_schema"))
    return [
        *_schema_issues(schema),
        *_pointer_issues(declaration, schema),
        *_service_issues(declaration),
        *_port_issues(declaration, schema),
        *_section_issues(declaration),
        *_format_issues(declaration),
    ]


def interface_fields(declaration: JsonObject) -> Iterator[tuple[str, JsonObject]]:
    """(declaration pointer, field) for every field of every interface section."""
    sections = items(member(declaration.get("ui"), "sections"))
    for section_index, section in enumerate(sections):
        for field_index, field in enumerate(items(member(section, "fields"))):
            yield f"/ui/sections/{section_index}/fields/{field_index}", mapping(field)


def _schema_issues(schema: JsonObject) -> Iterator[str]:
    for pointer, message in metaschema_problems(schema):
        yield f"/config_schema{pointer}: {message}"
    if schema.get("$schema", DRAFT_2020_12) not in (DRAFT_2020_12, f"{DRAFT_2020_12}#"):
        yield f'/config_schema/$schema: must be "{DRAFT_2020_12}"'
    for location in references(schema):
        reference = text(value_at_pointer(schema, location))
        if local_target(schema, reference) is None:
            where = format_pointer(location)
            yield f'/config_schema{where}: "{reference}" is not a local reference that resolves'


def _pointer_issues(declaration: JsonObject, schema: JsonObject) -> Iterator[str]:
    for location, pointer in _declared_pointers(declaration):
        if schema_at(schema, pointer) is None:
            yield f'{location}: "{pointer}" does not resolve in config_schema'


def _declared_pointers(declaration: JsonObject) -> Iterator[tuple[str, str]]:
    for index, use in enumerate(items(declaration.get("uses"))):
        yield f"/uses/{index}/pointer", text(member(use, "pointer"))
    for index, pointer in enumerate(items(member(declaration.get("ui"), "card"))):
        yield f"/ui/card/{index}", text(pointer)
    for location, field in interface_fields(declaration):
        yield f"{location}/path", text(field.get("path"))
        if "when" in field:
            yield f"{location}/when/path", text(member(field["when"], "path"))


def _service_issues(declaration: JsonObject) -> Iterator[str]:
    uses = items(declaration.get("uses"))
    declared = {(text(member(use, "service")), text(member(use, "pointer"))) for use in uses}
    for location, field in interface_fields(declaration):
        selection = (text(field.get("service")), text(field.get("path")))
        if field.get("control") == "service" and selection not in declared:
            service, pointer = selection
            yield f'{location}: service "{service}" at "{pointer}" is not declared in uses'


def _port_issues(declaration: JsonObject, schema: JsonObject) -> Iterator[str]:
    ports = mapping(declaration.get("ports"))
    if "output" in items(declaration.get("placements")) and "outputs_from" not in ports:
        yield '/ports: placement "output" requires outputs_from'
    if "outputs_from" in ports:
        pointer = text(ports["outputs_from"])
        if not is_string_array(schema, schema_at(schema, pointer)):
            yield f'/ports/outputs_from: "{pointer}" must resolve to an array of strings'


def _section_issues(declaration: JsonObject) -> Iterator[str]:
    seen: set[str] = set()
    for index, section in enumerate(items(member(declaration.get("ui"), "sections"))):
        section_id = text(member(section, "id"))
        if section_id in seen:
            yield f'/ui/sections/{index}/id: "{section_id}" is already used by another section'
        seen.add(section_id)


def _format_issues(declaration: JsonObject) -> Iterator[str]:
    for location, field in interface_fields(declaration):
        control = text(field.get("control"))
        if "format" in field and control != "number":
            yield f'{location}/format: only number fields accept format, not "{control}" fields'

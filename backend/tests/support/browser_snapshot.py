"""Browser fixtures retain the exact selected saved definition and component roles."""

from slow_thinker_ii.application import StartIntent, library
from slow_thinker_ii.contracts import JsonObject, decode_json, encode_json, json_object

from .sequence_plans import EXAMPLES, MANIFESTS


def browser_snapshot(intent: StartIntent, definitions: library.DefinitionReader) -> str:
    definition = json_object(
        decode_json(definitions.definition(intent.graph_id, intent.graph_revision))
    )
    instances: JsonObject = {}
    for identity, value in json_object(definition["components"]).items():
        component = json_object(value)
        descriptor = decode_json((EXAMPLES / MANIFESTS[str(component["type_id"])]).read_text())
        instances[identity] = {"descriptor": descriptor, "config": component["config"]}
    return encode_json(
        {"definition": definition, "input": decode_json(intent.input_json), "instances": instances}
    )

"""Complete bounded JSON representations of immutable definition records."""

from fastapi import Response

from slow_thinker_ii.application import library
from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json, encode_json, json_object

from ._operator_errors import OperatorError


def definition_reply(value: JsonObject, limit: int, status: int = 200) -> Response:
    return definition_text_reply(encode_json(value), limit, status)


def definition_text_reply(content: str, limit: int, status: int = 200) -> Response:
    if len(content.encode("utf-8")) > limit:
        raise OperatorError("response_too_large", 413)
    return Response(
        content,
        status_code=status,
        media_type="application/json",
        headers={"cache-control": "no-store"},
    )


def reference_data(reference: library.GraphReference) -> JsonObject:
    return {"graph_id": reference.graph_id, "revision": reference.revision}


def page_data(page: library.LibraryPage) -> JsonObject:
    items: list[JsonValue] = [item_data(item) for item in page.items]
    return {"items": items, "next_cursor": page.next_cursor}


def item_data(item: library.LibraryItem) -> JsonObject:
    summary = item.summary
    nodes: list[JsonValue] = [
        {"id": node.node_id, "component": node.component_id} for node in summary.nodes
    ]
    return {
        "graph_id": summary.graph_id,
        "revision": summary.revision,
        "participants": summary.participant_count,
        "nodes": nodes,
        "input_schema": json_object(decode_json(summary.input_schema_json)),
        "origin": item.origin,
        "derived_from": None if item.parent is None else reference_data(item.parent),
    }

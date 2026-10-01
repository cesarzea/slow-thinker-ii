"""Expose frozen binding declarations and unambiguous earlier sequence outputs."""

import sqlite3

from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json, encode_json, json_object


def binding_payload(db: sqlite3.Connection, run: str, call: str) -> str | None:
    row = db.execute(
        "SELECT c.rowid AS position,c.context_json,r.snapshot_json FROM managed_calls c "
        "JOIN managed_runs r USING(run_id) WHERE c.run_id=? AND c.call_id=? "
        "AND c.parent_call_id IS NULL",
        (run, call),
    ).fetchone()
    if row is None:
        return None
    routed = db.execute(
        "SELECT payload_json FROM run_events WHERE run_id=? AND call_id=? "
        "AND event='activation.bound' ORDER BY sequence DESC LIMIT 1",
        (run, call),
    ).fetchone()
    if routed is not None:
        sources = json_object(decode_json(str(routed[0])))
        return encode_json(
            {"status": "present", "source": "recorded_activations", "inputs": sources}
        )
    return definition_bindings(db, run, row)


def definition_bindings(db: sqlite3.Connection, run: str, row: sqlite3.Row) -> str:
    context = json_object(decode_json(str(row["context_json"])))
    snapshot = json_object(decode_json(str(row["snapshot_json"])))
    execution = json_object(snapshot.get("execution", {}))
    definition = json_object(execution.get("definition", {}))
    nodes = json_object(definition.get("nodes", {}))
    node = nodes.get(str(context.get("node_id")))
    if not isinstance(node, dict):
        return encode_json({"status": "unavailable", "reason": "definition_not_recorded"})
    inputs = json_object(node.get("inputs", {}))
    values: JsonObject = {
        name: binding_reference(db, run, int(row["position"]), json_object(value))
        for name, value in inputs.items()
    }
    return encode_json({"status": "present", "source": "admitted_definition", "inputs": values})


def binding_reference(
    db: sqlite3.Connection, run: str, before: int, binding: JsonObject
) -> JsonObject:
    source = binding.get("source")
    reference: JsonObject = {"declaration": binding}
    if source == "run_input":
        reference.update({"status": "resolved", "payload_id": "run-input:" + run})
    elif source == "literal":
        reference.update({"status": "literal"})
    elif source == "node_output":
        reference.update(previous_output(db, run, before, binding.get("node")))
    else:
        reference.update({"status": "unavailable", "reason": "unsupported_binding"})
    return reference


def previous_output(db: sqlite3.Connection, run: str, before: int, node: JsonValue) -> JsonObject:
    rows = db.execute(
        "SELECT call_id,result_receipt_id FROM managed_calls WHERE run_id=? AND rowid<? "
        "AND parent_call_id IS NULL AND state='completed' "
        "AND json_extract(context_json,'$.node_id')=? LIMIT 2",
        (run, before, str(node)),
    ).fetchall()
    if len(rows) != 1 or rows[0]["result_receipt_id"] is None:
        return {"status": "unavailable", "reason": "source_not_unambiguous"}
    return {
        "status": "resolved",
        "call_id": str(rows[0]["call_id"]),
        "payload_id": "response:" + str(rows[0]["result_receipt_id"]),
    }


def run_input_payload(db: sqlite3.Connection, run: str) -> tuple[bool, str | None]:
    row = db.execute("SELECT snapshot_json FROM managed_runs WHERE run_id=?", (run,)).fetchone()
    if row is None:
        return False, None
    snapshot = json_object(decode_json(str(row[0])))
    intent = json_object(snapshot.get("intent", {}))
    return True, None if "input" not in intent else encode_json(intent["input"])

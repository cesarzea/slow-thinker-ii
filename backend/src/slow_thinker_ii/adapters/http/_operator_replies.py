"""Receipts and representations retain authoritative money and opaque cache versions."""

from hashlib import sha256

from fastapi import Request, Response

from slow_thinker_ii.application import CommandReceipt, CommandResult
from slow_thinker_ii.contracts import JsonObject, decode_json, encode_json, json_object

from ._operator_errors import OperatorError


def receipt_data(receipt: CommandReceipt) -> JsonObject:
    return {
        "schema_version": "0.1-draft",
        "command_id": receipt.command_id,
        "kind": receipt.kind,
        "disposition": receipt.disposition,
        "target_id": receipt.target_id,
        "reason": receipt.reason,
    }


def command_reply(result: CommandResult) -> Response:
    data = receipt_data(result.receipt)
    data["replayed"] = result.replayed
    disposition = result.receipt.disposition
    status = 202 if disposition == "accepted" else 200
    if disposition == "rejected":
        status = rejection_status(result.receipt.reason)
    return Response(
        encode_json(data),
        status_code=status,
        media_type="application/json",
        headers={"cache-control": "no-store"},
    )


def representation(request: Request, content: str | None, limit: int) -> Response:
    if content is None:
        raise OperatorError("object_not_found", 404)
    value = json_object(decode_json(content))
    token = sha256(content.encode()).hexdigest()
    value["view_token"] = token
    content = encode_json(value)
    if len(content.encode()) > limit:
        raise OperatorError("response_too_large", 413)
    etag = '"' + token + '"'
    headers = {"cache-control": "no-store", "etag": etag}
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers=headers)
    return Response(content, media_type="application/json", headers=headers)


def rejection_status(reason: str | None) -> int:
    if reason == "unknown_run":
        return 404
    if reason == "snapshot_limit":
        return 413
    if reason in (
        "invalid_graph_or_resource_configuration",
        "limits_profile_mismatch",
        "installation_selection_invalid",
        "host_adapter_unavailable",
        "model_resource_required",
        "provider_profile_unavailable",
        "tariff_model_mismatch",
    ):
        return 422
    if reason in (
        "credential_unavailable",
        "tariff_unavailable",
        "component_preparation_unavailable",
    ):
        return 503
    return 409

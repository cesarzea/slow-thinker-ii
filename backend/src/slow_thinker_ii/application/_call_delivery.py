"""One authorized transport call produces one receipt, including local failure evidence."""

import asyncio
import json
from uuid import uuid4

from slow_thinker_ii.access import AccessDenied, InvocationLease
from slow_thinker_ii.contracts import JsonObject, OperationResult

from ._dispatch_ports import ManagedResult, OperationPort, OperationReply
from ._receipts import CallReceipt
from ._run_admission import RunAdmission


def failed(code: str, detail: str | None = None) -> OperationReply:
    payload: JsonObject = {"error": {"code": code, "origin": "platform", "detail": detail}}
    return OperationReply(OperationResult(json.dumps(payload), True))


async def deliver(
    admission: RunAdmission,
    lease: InvocationLease,
    operation: OperationPort,
) -> ManagedResult:
    try:
        saved = admission.authorize(lease.token)
    except AccessDenied:
        admission.cancel(lease.context.call_id)
        raise
    try:
        async with asyncio.timeout_at(lease.context.deadline):
            reply = await operation.invoke(saved.request_json, lease.token, lease.context.deadline)
    except asyncio.CancelledError:
        admission.cancel(lease.context.call_id)
        record_reply(admission, lease, failed("cancelled"))
        raise
    except TimeoutError:
        reply = failed("call_deadline")
    except Exception as error:
        reply = failed("component_failure", type(error).__name__)
    return record_reply(admission, lease, reply)


def record_reply(
    admission: RunAdmission, lease: InvocationLease, reply: OperationReply
) -> ManagedResult:
    evidence = reply.charge
    receipt = CallReceipt(
        uuid4().hex,
        lease.context.call_id,
        reply.result.payload_json,
        not reply.result.is_error,
        None if evidence is None else evidence.usage_json,
        None if evidence is None else evidence.amount,
        None if evidence is None else evidence.source,
    )
    outcome = admission.receive(receipt)
    return ManagedResult(lease.context, reply.result, receipt.receipt_id, outcome)

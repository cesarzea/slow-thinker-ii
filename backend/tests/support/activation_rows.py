"""Retained invocation fixtures exercise paging separately from dispatch authorization."""

from dataclasses import replace

from slow_thinker_ii.access import OperationAddress
from slow_thinker_ii.application import PreparedCall

from .operator_http import HttpCase


def add_related_call(api: HttpCase, root: str, identity: str, *, child: bool = True) -> None:
    with api.case.runs.begin() as transaction:
        source = transaction.call(root).prepared.context
        context = replace(
            source,
            call_id=identity,
            attempt_id="attempt-" + identity,
            parent_call_id=root if child else None,
            caller=source.target.instance if child else None,
            target=OperationAddress("resource", "read") if child else source.target,
            depth=source.depth + 1 if child else source.depth,
        )
        transaction.record_call(PreparedCall(context, "{}", None))

"""Assign immutable causal identities; nested calls inherit their originating graph node."""

from uuid import uuid4

from ._values import CallContext, OperationAddress


def call_context(
    run: str,
    revision: str,
    target: OperationAddress,
    parent: CallContext | None,
    depth: int,
    deadline: float,
    activation: bool,
    node_id: str | None,
) -> CallContext:
    if node_id is not None and (not node_id or not activation):
        raise ValueError("Only graph activations can declare a nonempty node identity")
    return CallContext(
        run,
        revision,
        (uuid4().hex if activation else None) if parent is None else parent.activation_id,
        uuid4().hex,
        uuid4().hex,
        None if parent is None else parent.call_id,
        None if parent is None else parent.target.instance,
        target,
        depth,
        deadline,
        node_id if parent is None else parent.node_id,
    )

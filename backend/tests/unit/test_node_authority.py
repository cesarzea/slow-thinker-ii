"""Configured node identity follows an activation through nested managed calls."""

import pytest
from support.authority import PROPOSER, REVIEWER, Clock, alias, authority


def test_nested_calls_retain_originating_node_but_reuse_gets_a_new_activation() -> None:
    service = authority(Clock())
    draft = service.schedule(PROPOSER, node_id="draft")
    nested = service.invoke(draft.token, alias(service, draft.token, REVIEWER))
    assert nested.context.node_id == "draft"
    assert nested.context.activation_id == draft.context.activation_id
    service.finish(nested.context.call_id, succeeded=True)
    service.finish(draft.context.call_id, succeeded=True)
    revised = service.schedule(PROPOSER, node_id="revise")
    assert revised.context.node_id == "revise"
    assert revised.context.activation_id != draft.context.activation_id


@pytest.mark.parametrize("activation,node_id", [(True, ""), (False, "draft")])
def test_node_identity_requires_a_real_graph_activation(*, activation: bool, node_id: str) -> None:
    service = authority(Clock())
    with pytest.raises(ValueError, match="graph activations"):
        service.schedule(PROPOSER, activation=activation, node_id=node_id)
    assert service.schedule(PROPOSER).context.node_id is None

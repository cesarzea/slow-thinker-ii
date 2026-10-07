"""What a run executes: the plan of a version, or of a change of the working copy."""

from collections.abc import Callable

from slow_thinker_ii.catalog import Catalog
from slow_thinker_ii.graphs import RunPlan, compile_plan

from ._errors import ChangeNotFound, GraphNotFound, VersionNotFound
from ._ports import GraphStore


def run_plan(
    graphs: GraphStore,
    catalog: Callable[[], Catalog],
    graph_id: str,
    version: int | None,
    change: int | None,
) -> tuple[RunPlan, int]:
    """The plan and the change it comes from: a version's change, or the change itself."""
    if version is not None:
        record = graphs.version(graph_id, version)
        if record is None:
            _known(graphs, graph_id)
            raise VersionNotFound(graph_id, version)
        return compile_plan(record.document, catalog(), version), record.change
    if change is None:
        raise ValueError("A run starts from a version or a change.")
    draft = graphs.change(graph_id, change)
    if draft is None:
        _known(graphs, graph_id)
        raise ChangeNotFound(graph_id, change)
    return compile_plan(draft.document, catalog(), draft.version), change


def _known(graphs: GraphStore, graph_id: str) -> None:
    if graphs.graph(graph_id) is None:
        raise GraphNotFound(graph_id)

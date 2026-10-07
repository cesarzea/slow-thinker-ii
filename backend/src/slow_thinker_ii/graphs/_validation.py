"""Validation of graph documents: a pure function of the document and the catalog."""

from slow_thinker_ii.catalog import Catalog
from slow_thinker_ii.contracts import JsonValue, json_object

from ._configuration import configuration_diagnostics
from ._connections import connection_diagnostics
from ._diagnostics import Diagnostic, in_path_order
from ._document import document_diagnostics
from ._graph_rules import limit_diagnostics, trigger_diagnostics, warning_diagnostics
from ._model import read_graph
from ._port_names import port_name_diagnostics
from ._services import service_diagnostics
from ._structure import component_diagnostics, identity_diagnostics


def validate_document(document: JsonValue, catalog: Catalog) -> tuple[Diagnostic, ...]:
    """Diagnostics in path order; when the document does not match its JSON Schema, only those."""
    invalid = document_diagnostics(document)
    if invalid:
        return in_path_order(invalid)
    graph = read_graph(json_object(document), catalog)
    configuration = configuration_diagnostics(graph)
    reported = frozenset(diagnostic.path for diagnostic in configuration)
    return in_path_order(
        [
            *identity_diagnostics(graph),
            *component_diagnostics(graph),
            *configuration,
            *service_diagnostics(graph, catalog, reported),
            *port_name_diagnostics(graph),
            *connection_diagnostics(graph),
            *trigger_diagnostics(graph),
            *limit_diagnostics(graph),
            *warning_diagnostics(graph),
        ]
    )

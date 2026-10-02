"""Local definition validation grouped by schemas, types and graph semantics."""

from ._graph import validate_definition
from ._schemas import LocalSchemas

__all__ = ["LocalSchemas", "validate_definition"]

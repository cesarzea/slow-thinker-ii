"""Select exact installed types from trusted descriptors; graph data supplies no executable path."""

from slow_thinker_ii.adapters.catalog import TypeInstallation
from slow_thinker_ii.application import PreparationRejected
from slow_thinker_ii.contracts import decode_json, encode_json, json_object

from ._models import ResourceSettings


def select_types(
    settings: ResourceSettings, descriptors: tuple[str, ...]
) -> tuple[TypeInstallation, ...]:
    known: dict[tuple[str, str], str] = {}
    for text in descriptors:
        record = json_object(decode_json(text))
        key = str(record["type_id"]), str(record["type_version"])
        if key in known:
            raise ValueError("Duplicate trusted component descriptor")
        known[key] = encode_json(record)
    selected: dict[tuple[str, str], TypeInstallation] = {}
    for item in settings.installations:
        key = item.type_id, item.type_version
        if key in selected or key not in known:
            raise PreparationRejected("installation_selection_invalid")
        selected[key] = TypeInstallation(item.resolution_id, known[key])
    return tuple(selected.values())

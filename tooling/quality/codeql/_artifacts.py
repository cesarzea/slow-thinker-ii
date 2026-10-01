"""Resolve extraction evidence to validated source-relative paths."""

from pathlib import PurePosixPath
from urllib.parse import unquote, urlsplit

from ._shapes import index_value, object_value, objects, text_value
from ._types import CodeQLFailure


def location_paths(notification: dict[str, object], artifacts: list[dict[str, object]]) -> set[str]:
    locations = objects(notification.get("locations"), "Extraction locations")
    if not locations:
        raise CodeQLFailure("Extraction notification has no source locations")
    paths: set[str] = set()
    for location in locations:
        physical = object_value(location.get("physicalLocation"), "Extraction physicalLocation")
        reference = object_value(physical.get("artifactLocation"), "Extraction artifactLocation")
        paths.add(_artifact_path(reference, artifacts))
    return paths


def _artifact_path(reference: dict[str, object], artifacts: list[dict[str, object]]) -> str:
    uri = reference.get("uri")
    indexed_uri: object = None
    if "index" in reference:
        index = index_value(reference["index"], len(artifacts), "Artifact index")
        location = object_value(artifacts[index].get("location"), "Artifact location")
        indexed_uri = location.get("uri")
        text_value(indexed_uri, "Indexed artifact URI")
    if uri is None:
        uri = indexed_uri
    path = _relative_uri(text_value(uri, "Extraction artifact URI"))
    if indexed_uri is not None and _relative_uri(str(indexed_uri)) != path:
        raise CodeQLFailure("Artifact URI disagrees with its indexed artifact")
    return path


def _relative_uri(uri: str) -> str:
    parsed = urlsplit(uri)
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
        raise CodeQLFailure(f"Extraction URI must be source-relative: {uri}")
    decoded = unquote(parsed.path, errors="strict")
    path = PurePosixPath(decoded)
    if not decoded or path.is_absolute() or ".." in path.parts or "\\" in decoded:
        raise CodeQLFailure(f"Invalid source-relative extraction URI: {uri}")
    return path.as_posix()

"""Require successful invocations and complete extraction coverage."""

from ._artifacts import location_paths
from ._descriptors import descriptors as descriptor_table
from ._descriptors import referenced_descriptor
from ._rules import severity
from ._shapes import object_value, objects
from ._types import CodeQLFailure

PREFIXES = {"python": "py", "javascript": "js"}


def extraction_evidence(
    run: dict[str, object], driver: dict[str, object], language: str
) -> tuple[set[str], set[str]]:
    invocations = objects(run.get("invocations"), "SARIF invocations")
    if not invocations:
        raise CodeQLFailure("SARIF has no successful analysis invocations")
    artifacts = objects(run.get("artifacts", []), "SARIF artifacts")
    descriptors = descriptor_table(driver.get("notifications", []), "Notification descriptors")
    evidence: tuple[set[str], set[str]] = (set(), set())
    for invocation in invocations:
        if invocation.get("executionSuccessful") is not True:
            raise CodeQLFailure("SARIF analysis invocation did not complete successfully")
        _collect_notifications(invocation, descriptors, artifacts, language, evidence)
    return evidence


def _collect_notifications(
    invocation: dict[str, object],
    descriptors: list[dict[str, object]],
    artifacts: list[dict[str, object]],
    language: str,
    evidence: tuple[set[str], set[str]],
) -> None:
    identifiers = (
        f"{PREFIXES[language]}/baseline/expected-extracted-files",
        f"{PREFIXES[language]}/diagnostics/successfully-extracted-files",
    )
    for field in ("toolExecutionNotifications", "toolConfigurationNotifications"):
        for notification in objects(invocation.get(field, []), field):
            level = severity(notification.get("level"), "Analysis notification")
            if level in {"warning", "error"}:
                raise CodeQLFailure(f"SARIF contains an analysis {level} notification")
            identifier = _notification_id(notification, descriptors)
            if identifier in identifiers:
                evidence[identifiers.index(identifier)].update(
                    location_paths(notification, artifacts)
                )


def _notification_id(
    notification: dict[str, object], descriptors: list[dict[str, object]]
) -> str | None:
    if "descriptor" not in notification:
        return None
    reference = object_value(notification["descriptor"], "Notification descriptor")
    if descriptors:
        return str(referenced_descriptor(reference, descriptors, "Notification")["id"])
    identifier = reference.get("id")
    if not isinstance(identifier, str) or not identifier or "index" in reference:
        raise CodeQLFailure("Notification descriptor cannot be resolved")
    return identifier


def require_coverage(
    evidence: tuple[set[str], set[str]], owned: frozenset[str], language: str
) -> None:
    for label, present in zip(("baseline", "successful extraction"), evidence, strict=True):
        missing = sorted(owned - present)
        if missing:
            examples = ", ".join(missing[:5])
            raise CodeQLFailure(
                f"Incomplete {language} {label}: {len(missing)} missing files: {examples}"
            )

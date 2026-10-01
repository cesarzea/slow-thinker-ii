"""Field paths in the representative public SARIF fixture."""

from .reports import FieldPath

RUN: FieldPath = ("runs", 0)
DRIVER: FieldPath = (*RUN, "tool", "driver")
INVOCATION: FieldPath = (*RUN, "invocations", 0)
RESULT: FieldPath = (*RUN, "results", 0)
NOTIFICATIONS: FieldPath = (*INVOCATION, "toolExecutionNotifications")
EXPECTED: FieldPath = (*NOTIFICATIONS, 0)
EXTRACTED: FieldPath = (*NOTIFICATIONS, 1)
LOCATION: FieldPath = (*EXPECTED, "locations", 0, "physicalLocation", "artifactLocation")

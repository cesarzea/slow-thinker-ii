"""An in-memory `engine.RunLog` that keeps events in order and can act when one is recorded."""

from collections.abc import Callable
from dataclasses import dataclass

from slow_thinker_ii.contracts import JsonObject


@dataclass(frozen=True)
class LoggedEvent:
    kind: str
    data: JsonObject
    node_id: str | None
    activation_id: str | None


@dataclass(frozen=True)
class _Action:
    kind: str
    node_id: str | None
    run: Callable[[], None]


class RecordingLog:
    """Engine `RunLog` fake that keeps every event in order.

    `when(kind, action, node_id=...)` runs `action` once, right after the next event of that
    kind (for that node, when given); an action that raises makes `record` raise.
    """

    def __init__(self) -> None:
        self.events: list[LoggedEvent] = []
        self._actions: list[_Action] = []

    def record(
        self,
        kind: str,
        data: JsonObject,
        *,
        node_id: str | None = None,
        activation_id: str | None = None,
    ) -> None:
        self.events.append(LoggedEvent(kind, data, node_id, activation_id))
        due = [action for action in self._actions if _matches(action, kind, node_id)]
        if due:
            self._actions.remove(due[0])
            due[0].run()

    def when(self, kind: str, action: Callable[[], None], node_id: str | None = None) -> None:
        self._actions.append(_Action(kind, node_id, action))

    def kinds(self) -> list[str]:
        return [event.kind for event in self.events]

    def of(self, kind: str) -> list[LoggedEvent]:
        return [event for event in self.events if event.kind == kind]


def _matches(action: _Action, kind: str, node_id: str | None) -> bool:
    return action.kind == kind and action.node_id in (None, node_id)

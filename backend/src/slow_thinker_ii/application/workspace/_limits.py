"""Validated settings commands and immutable effective profiles."""

import math
import re
from dataclasses import dataclass, replace

from slow_thinker_ii.accounting import display_amount, parse_limit
from slow_thinker_ii.contracts import JsonObject, decode_json, encode_json, json_object

from .._limits_profile import LimitsProfile
from .._operator_records import ExecutionConfiguration
from ._errors import WorkspaceError

DURATIONS: tuple[str, ...] = ("run_seconds", "call_seconds", "startup_seconds", "shutdown_seconds")
COUNTS: tuple[str, ...] = ("max_calls", "max_depth", "max_payload_bytes")
BUDGETS: tuple[str, ...] = ("run_budget", "session_budget", "month_budget")


@dataclass(frozen=True)
class LimitsCommand:
    command_id: str
    expected_revision: str
    values_json: str

    def to_json(self) -> str:
        return encode_json(
            {
                "command_id": self.command_id,
                "expected_revision": self.expected_revision,
                "limits": decode_json(self.values_json),
            }
        )


@dataclass(frozen=True)
class ConfigurationResult:
    command_id: str
    configuration_revision: str
    replayed: bool

    def to_value(self) -> JsonObject:
        return {
            "command_id": self.command_id,
            "configuration_revision": self.configuration_revision,
            "replayed": self.replayed,
        }


def limits_command(value: JsonObject) -> LimitsCommand:
    identity, revision = value.get("command_id"), value.get("expected_revision")
    if set(value) != {"command_id", "expected_revision", "limits"}:
        raise WorkspaceError("invalid_limits")
    if not isinstance(identity, str) or re.fullmatch(r"[a-f0-9]{32}", identity) is None:
        raise WorkspaceError("invalid_limits")
    if not isinstance(revision, str) or not revision or len(revision) > 4096:
        raise WorkspaceError("invalid_limits")
    try:
        changes = json_object(value["limits"])
        _values(changes)
    except (ValueError, OverflowError) as error:
        raise WorkspaceError("invalid_limits") from error
    return LimitsCommand(identity, revision, encode_json(changes))


def _values(value: JsonObject) -> None:
    if not value or set(value) - set(DURATIONS + COUNTS + BUDGETS):
        raise ValueError("Unsupported limits")
    for key, item in value.items():
        if key in DURATIONS:
            if (
                type(item) not in (int, float)
                or not math.isfinite(float(str(item)))
                or float(str(item)) <= 0
            ):
                raise ValueError("Invalid duration")
        elif key in COUNTS:
            if type(item) is not int or item < 1:
                raise ValueError("Invalid count")
        elif not isinstance(item, str) or len(item) > 64:
            raise ValueError("Invalid budget")
        else:
            parse_limit(item)


def apply_limits(
    current: ExecutionConfiguration, command: LimitsCommand, maximum: LimitsProfile
) -> ExecutionConfiguration:
    changes = json_object(decode_json(command.values_json))
    _values(changes)
    effective = json_object(decode_json(current.limits.to_json()))
    for key, value in changes.items():
        effective[key] = parse_limit(str(value)) if key in BUDGETS else value
    ceiling = json_object(decode_json(maximum.to_json()))
    if any(_number(effective[key]) > _number(ceiling[key]) for key in changes):
        raise WorkspaceError("invalid_limits")
    try:
        profile = _profile(effective)
    except ValueError as error:
        raise WorkspaceError("invalid_limits") from error
    return replace(current, revision=f"settings-{command.command_id}", limits=profile)


def _profile(value: JsonObject) -> LimitsProfile:
    return LimitsProfile(
        str(value["revision"]),
        float(str(value["run_seconds"])),
        float(str(value["call_seconds"])),
        float(str(value["startup_seconds"])),
        float(str(value["shutdown_seconds"])),
        int(str(value["max_calls"])),
        int(str(value["max_depth"])),
        int(str(value["max_payload_bytes"])),
        int(str(value["run_budget"])),
        int(str(value["session_budget"])),
        int(str(value["month_budget"])),
    )


def _number(value: object) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise WorkspaceError("invalid_limits")
    return value


def limits_value(profile: LimitsProfile) -> JsonObject:
    result = json_object(decode_json(profile.to_json()))
    result.pop("revision")
    for key in BUDGETS:
        result[key] = display_amount(int(str(result[key])))
    return result


def within_limits(profile: LimitsProfile, maximum: LimitsProfile) -> bool:
    values = json_object(decode_json(profile.to_json()))
    ceiling = json_object(decode_json(maximum.to_json()))
    return all(
        _number(values[key]) <= _number(ceiling[key]) for key in DURATIONS + COUNTS + BUDGETS
    )

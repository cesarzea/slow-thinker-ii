"""Rows of `runs` and `run_events` as the application's records."""

import sqlite3

from slow_thinker_ii.application import RecordedEvent, RunRecord

from ._rows import (
    integer,
    moment,
    optional_integer,
    optional_moment,
    optional_object,
    optional_text,
    stored_object,
    stored_value,
    text,
)


def run_record(row: sqlite3.Row) -> RunRecord:
    return RunRecord(
        text(row, "id"),
        text(row, "graph_id"),
        optional_integer(row, "graph_version"),
        integer(row, "graph_change"),
        text(row, "status"),
        optional_text(row, "reason"),
        text(row, "detail"),
        stored_value(row, "input_json"),
        moment(row, "created_at"),
        optional_moment(row, "ended_at"),
        optional_object(row, "totals_json"),
    )


def recorded_event(row: sqlite3.Row) -> RecordedEvent:
    return RecordedEvent(
        text(row, "run_id"),
        integer(row, "seq"),
        moment(row, "at"),
        integer(row, "elapsed_ms"),
        text(row, "kind"),
        text(row, "evidence"),
        optional_text(row, "node_id"),
        optional_text(row, "activation_id"),
        stored_object(row, "data_json"),
    )

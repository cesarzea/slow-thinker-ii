"""A blocking user selector cannot defeat the owned process deadline and bounded kill escalation."""

import asyncio
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.process import ComponentProcess, ProcessLaunch
from slow_thinker_ii.adapters.process._ownership import GraphOwnership
from slow_thinker_ii.adapters.sqlite import SqliteProcessJournal
from support.process_fixture import assert_reaped
from support.run_admission import run_case

from .conftest import PreparedBundle
from .selector_fixture import selector_bootstrap, selector_installation


async def test_nonterminating_installed_selector_is_reaped_without_raw_stderr(
    tmp_path: Path, prepared_bundle: PreparedBundle
) -> None:
    python, description = await asyncio.to_thread(selector_installation, prepared_bundle, tmp_path)
    bootstrap = selector_bootstrap(tmp_path, description)
    case = run_case(tmp_path / "run.sqlite")
    journal = SqliteProcessJournal(case.database, 4096)
    owner = GraphOwnership(journal, "run", "runtime").host("selector", tmp_path)
    launch = ProcessLaunch(
        python, "slow_thinker_redirector", bootstrap, tmp_path, 5, 0.9, 1_048_576, ownership=owner
    )
    process = ComponentProcess(launch, description.operations)
    async with process.connect() as connection:
        with pytest.raises(TimeoutError):
            await connection.call("route", '{"value":{}}', "test-grant", 0.25)
    assert_reaped(process, forced=True)
    assert not journal.pending()
    with case.store.begin() as transaction:
        events = transaction.events("run")
        diagnostics = [event.payload_json for event in events if event.event == "host.diagnostic"]
    assert len(diagnostics) == 1 and "size_bytes" in diagnostics[0]
    assert "private-selector-token" not in str(events)

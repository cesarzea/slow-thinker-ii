"""Mark interrupted work without replaying any ambiguous dispatch."""

from ._run_ports import RunStore


def recover_runs(store: RunStore) -> tuple[str, ...]:
    with store.begin() as transaction:
        runs = transaction.unfinished()
        for run in runs:
            transaction.stop(run.run_id, "backend_interrupted", "interrupted")
        return tuple(run.run_id for run in runs)

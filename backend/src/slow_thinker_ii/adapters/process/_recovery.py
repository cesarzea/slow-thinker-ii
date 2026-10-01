"""Restart recovery never replays work and signals only completely verified owned identities."""

import asyncio

import psutil

from slow_thinker_ii.application import OwnedLaunch, ProcessJournal

from ._identity import verified_process


def recover_one(launch: OwnedLaunch, journal: ProcessJournal, seconds: float) -> None:
    identity = launch.identity
    if identity is None:
        journal.unconfirmed(launch.marker, "launch_identity_unavailable")
        return
    try:
        process = verified_process(identity)
        process.terminate()
        try:
            process.wait(timeout=seconds / 2)
        except psutil.TimeoutExpired:
            process = verified_process(identity)
            process.kill()
            process.wait(timeout=seconds / 2)
    except psutil.NoSuchProcess:
        journal.stopped(launch.marker, "process_absent")
        return
    except (psutil.Error, OSError, ValueError):
        journal.unconfirmed(launch.marker, "ownership_or_exit_unconfirmed")
        return
    journal.stopped(launch.marker, "verified_recovery_exit")


async def recover_processes(journal: ProcessJournal, seconds: float) -> None:
    for launch in journal.pending():
        await asyncio.to_thread(recover_one, launch, journal, seconds)
    journal.reconcile()

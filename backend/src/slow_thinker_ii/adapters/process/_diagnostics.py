"""Drain process diagnostics and retain bounded metadata without unknown embedded credentials."""

import asyncio

from slow_thinker_ii.contracts import encode_json

from ._launch import ProcessLaunch


async def capture_diagnostics(reader: asyncio.StreamReader, launch: ProcessLaunch) -> None:
    total = 0
    try:
        while chunk := await reader.read(8192):
            total = min(total + len(chunk), 2**63 - 1)
    finally:
        owner = launch.ownership
        if owner is not None and total:
            owner.journal.diagnostic(
                owner.marker,
                encode_json(
                    {
                        "instance": owner.launch.instance_id,
                        "category": "process_stderr",
                        "capture_status": "unavailable",
                        "reason": "unstructured_credentials_possible",
                        "size_bytes": total,
                    }
                ),
            )

"""Recorded public price evidence; never a simulated model inference."""

from pathlib import Path

from slow_thinker_ii.accounting import TariffRevision
from slow_thinker_ii.adapters.tariffs import parse_catalog

PAYLOAD = (Path(__file__).parents[1] / "fixtures/vercel-luna.json").read_bytes()


class RecordedCatalog:
    def __init__(self) -> None:
        self.calls = 0
        self.payload = PAYLOAD
        self.error: OSError | ValueError | None = None

    async def fetch(self, now: int) -> TariffRevision:
        self.calls += 1
        if self.error is not None:
            raise self.error
        return parse_catalog(self.payload, now)

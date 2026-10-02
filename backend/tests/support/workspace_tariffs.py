"""Recorded public DeepSeek evidence is separate from deterministic model results."""

from pathlib import Path

from slow_thinker_ii.accounting import TariffRevision
from slow_thinker_ii.adapters.tariffs import parse_deepseek_pricing

DEEPSEEK_PAYLOAD = (Path(__file__).parents[1] / "fixtures/deepseek-pricing.html").read_bytes()


class RecordedDeepSeek:
    def __init__(self) -> None:
        self.calls = 0
        self.payload = DEEPSEEK_PAYLOAD
        self.error: OSError | ValueError | None = None

    async def fetch(self, now: int) -> TariffRevision:
        self.calls += 1
        error = self.error
        if error is not None:
            raise error
        return parse_deepseek_pricing(self.payload, now)

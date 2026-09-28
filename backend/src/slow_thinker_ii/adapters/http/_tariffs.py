"""Read-only visibility of automatic tariff refresh and its validated revision."""

from time import time

from fastapi import APIRouter
from pydantic import BaseModel

from slow_thinker_ii.application import REFRESH_SECONDS, TariffStore


class TariffStatusReply(BaseModel):
    revision: str | None
    profile: str | None
    last_attempt: int | None
    last_success: int | None
    refresh_error: str | None
    stale: bool
    currency: str


def tariff_router(store: TariffStore) -> APIRouter:
    router = APIRouter(prefix="/api/v1")

    def status() -> TariffStatusReply:
        current = store.status()
        profile = (
            None if current.revision is None else store.revision(current.revision).tariff.profile
        )
        stale = current.last_success is None or time() - current.last_success >= REFRESH_SECONDS
        return TariffStatusReply(
            revision=current.revision,
            profile=profile,
            last_attempt=current.last_attempt,
            last_success=current.last_success,
            refresh_error=current.error,
            stale=stale,
            currency="USD",
        )

    router.add_api_route("/tariffs", status, methods=["GET"])
    return router

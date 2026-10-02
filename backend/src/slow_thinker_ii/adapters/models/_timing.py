"""Only an uninterrupted reviewed UTC billing interval permits a calculated settlement."""

import math
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from slow_thinker_ii.accounting import TokenRates
from slow_thinker_ii.contracts import JsonObject, json_object

from ._billing import DirectBilling

SHANGHAI = ZoneInfo("Asia/Shanghai")


def timestamp(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("unverified_transport_timing")
    return float(value)


def interval_rates(payload: JsonObject, response: JsonObject, billing: DirectBilling) -> TokenRates:
    transport = json_object(payload.get("transport"))
    start = timestamp(transport.get("request_started_at"))
    finish = timestamp(transport.get("response_finished_at"))
    if finish < start:
        raise ValueError("unverified_transport_timing")
    first, last = datetime.fromtimestamp(start, UTC), datetime.fromtimestamp(finish, UTC)
    rates = at(first, billing)
    if rates is None or finish - start > 14 * 86400:
        raise ValueError("unreviewed_billing_interval")
    if "created" in response:
        created = response["created"]
        if type(created) is not int or not math.floor(start) <= created <= math.floor(finish):
            raise ValueError("inconsistent_provider_timing")
    if at(last, billing) != rates or crosses_boundary(first, last, billing):
        raise ValueError("billing_interval_boundary")
    return rates


def at(instant: datetime, billing: DirectBilling) -> TokenRates | None:
    if instant.weekday() >= 5 or not (1 <= instant.hour < 4 or 6 <= instant.hour < 10):
        return billing.off_peak
    local = instant.astimezone(SHANGHAI).date()
    if local.year != billing.calendar_year:
        return None
    if any(start <= local.isoformat() <= finish for start, finish in billing.holidays):
        return billing.off_peak
    return billing.peak


def crosses_boundary(first: datetime, last: datetime, billing: DirectBilling) -> bool:
    day = first.replace(hour=0, minute=0, second=0, microsecond=0)
    while day <= last:
        for hour in (1, 4, 6, 10, 16):
            boundary = day.replace(hour=hour)
            if first < boundary <= last and at(boundary - timedelta(microseconds=1), billing) != at(
                boundary, billing
            ):
                return True
        day += timedelta(days=1)
    return False

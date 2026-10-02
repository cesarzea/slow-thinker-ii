"""Reviewed official holiday policy is independent of daily numerical price imports."""

from slow_thinker_ii.contracts import JsonObject, JsonValue

CALENDAR_SOURCE = "https://www.gov.cn/zhengce/zhengceku/202511/content_7047091.htm"
HOLIDAYS = (
    ("2026-01-01", "2026-01-03"),
    ("2026-02-15", "2026-02-23"),
    ("2026-04-04", "2026-04-06"),
    ("2026-05-01", "2026-05-05"),
    ("2026-06-19", "2026-06-21"),
    ("2026-09-25", "2026-09-27"),
    ("2026-10-01", "2026-10-07"),
)


def calendar_policy() -> JsonObject:
    ranges: list[JsonValue] = [[start, finish] for start, finish in HOLIDAYS]
    return {
        "year": 2026,
        "source": CALENDAR_SOURCE,
        "timezone": "Asia/Shanghai",
        "ranges": ranges,
        "weekend_makeup_days": "off_peak",
        "unreviewed_peak_weekdays": "unresolved",
    }


def schedule_policy() -> JsonObject:
    return {
        "timezone": "UTC",
        "weekdays": [0, 1, 2, 3, 4],
        "peak_hours": [[1, 4], [6, 10]],
        "excluding_chinese_public_holidays": True,
        "calendar": calendar_policy(),
    }

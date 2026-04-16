from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TimePoint:
    seconds: float


@dataclass(frozen=True)
class TimeRange:
    start_seconds: float
    end_seconds: float


@dataclass(frozen=True)
class ParsedTimeRef:
    kind: str
    point: TimePoint | None = None
    time_range: TimeRange | None = None


def parse_time_point(text: str) -> TimePoint | None:
    value = (text or "").strip().replace(",", ".")
    if not value:
        return None
    try:
        parts = value.split(":")
        if len(parts) != 3:
            return None
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        if hours < 0 or minutes < 0 or seconds < 0:
            return None
        return TimePoint(hours * 3600 + minutes * 60 + seconds)
    except Exception:
        return None


def format_time_point(value: TimePoint | float, clamp_zero: bool = True) -> str:
    # Transitional compatibility: existing callers may still pass float seconds.
    seconds = value.seconds if isinstance(value, TimePoint) else float(value)
    if clamp_zero and seconds < 0:
        seconds = 0.0
    total_ms = int(round(seconds * 1000))
    hours, rem = divmod(total_ms, 3600000)
    minutes, rem = divmod(rem, 60000)
    secs, ms = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{ms:03d}"


def parse_time_range(text: str) -> TimeRange | None:
    raw = (text or "").strip()
    if "-->" not in raw:
        return None
    left, right = [part.strip() for part in raw.split("-->", 1)]
    start = parse_time_point(left)
    end = parse_time_point(right)
    if start is None or end is None:
        return None
    return normalize_range(start.seconds, end.seconds)


def format_time_range(value: TimeRange) -> str:
    return f"{format_time_point(value.start_seconds)} --> {format_time_point(value.end_seconds)}"


def parse_times_line(text: str) -> ParsedTimeRef | None:
    time_range = parse_time_range(text)
    if time_range is not None:
        return ParsedTimeRef(kind="range", time_range=time_range)
    point = parse_time_point(text)
    if point is not None:
        return ParsedTimeRef(kind="point", point=point)
    return None


def seconds_to_ms(seconds: float) -> int:
    return int(round(float(seconds) * 1000))


def ms_to_seconds(ms: int) -> float:
    return int(ms) / 1000.0


def normalize_range(start_seconds: float, end_seconds: float, min_duration_ms: int = 0) -> TimeRange:
    start = max(0.0, float(start_seconds))
    end = max(0.0, float(end_seconds))
    if end < start:
        start, end = end, start
    if min_duration_ms > 0:
        min_duration_seconds = min_duration_ms / 1000.0
        end = max(end, start + min_duration_seconds)
    return TimeRange(start, end)

from __future__ import annotations

import shutil
import subprocess


def find_ffmpeg() -> str | None:
    return shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")


def find_ffprobe() -> str | None:
    return shutil.which("ffprobe") or shutil.which("ffprobe.exe")


def run_simple_command(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def parse_progress_line(line: str) -> tuple[str, object] | None:
    text = (line or "").strip()
    if not text:
        return None
    if text.startswith("out_time_ms="):
        try:
            return ("out_time_seconds", float(text.split("=", 1)[1]) / 1_000_000.0)
        except Exception:
            return None
    if text.startswith("out_time_us="):
        try:
            return ("out_time_seconds", float(text.split("=", 1)[1]) / 1_000_000.0)
        except Exception:
            return None
    if text.startswith("total_size="):
        try:
            return ("total_size", int(text.split("=", 1)[1]))
        except Exception:
            return ("total_size", 0)
    if text.startswith("speed="):
        return ("speed", text.split("=", 1)[1].strip() or "-")
    if text.startswith("progress="):
        return ("progress", text.split("=", 1)[1].strip() or "")
    return None


def build_bleep_audio_filter(
    intervals: list[tuple[float, float, float]],
    freq: int,
    gain: float,
    sample_rate: int = 48000,
) -> str:
    items = ["[0:a]anull[src0]"]
    current = "src0"
    for idx, (start, end, _duration) in enumerate(intervals):
        nxt = f"src{idx+1}"
        items.append(f"[{current}]volume=enable='between(t,{start:.3f},{end:.3f})':volume=0[{nxt}]")
        current = nxt
    items.append(f"[{current}]anull[muted]")
    for idx, (start, _end, duration) in enumerate(intervals):
        items.append(
            f"sine=f={freq}:sample_rate={sample_rate}:d={duration:.3f},"
            f"volume={gain},adelay={int(start*1000)}:all=1[b{idx}]"
        )
    amix_inputs = "[muted]" + "".join(f"[b{idx}]" for idx in range(len(intervals)))
    items.append(f"{amix_inputs}amix=inputs={1+len(intervals)}:normalize=0[aout]")
    return ";".join(items)

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from bleepling.services.time_service import format_time_point, parse_time_point


class CutService:
    def _ffmpeg(self) -> str | None:
        return shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")

    def _ffprobe(self) -> str | None:
        return shutil.which("ffprobe") or shutil.which("ffprobe.exe")

    def working_video_dir(self, project) -> Path:
        path = project.root_path / "03_processing" / "04_cutting" / "working_video"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def clips_output_dir(self, project) -> Path:
        path = project.input_video_dir
        path.mkdir(parents=True, exist_ok=True)
        return path

    def sanitize_filename(self, text: str, default: str = "clip") -> str:
        text = (text or "").strip()
        if not text:
            text = default
        text = re.sub(r"[\\/:*?\"<>|]+", "_", text)
        text = re.sub(r"\s+", " ", text).strip().replace(" ", "_")
        text = re.sub(r"_+", "_", text)
        return text[:150] or default

    def seconds_to_ts(self, seconds: float) -> str:
        return format_time_point(seconds, clamp_zero=True)

    def ts_to_seconds(self, value: str) -> float:
        point = parse_time_point(value)
        if point is None:
            raise ValueError("Zeitformat muss HH:MM:SS.mmm sein.")
        return point.seconds

    def probe_duration(self, media_path: Path) -> float | None:
        ffprobe = self._ffprobe()
        if not ffprobe or not media_path.exists():
            return None
        try:
            cmd = [
                ffprobe,
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(media_path),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float((result.stdout or "").strip())
        except Exception:
            return None

    def derive_working_video_stem(self, source_files: list[Path]) -> str:
        if not source_files:
            return "arbeitsvideo"
        first = self.sanitize_filename(source_files[0].stem, "video")
        if len(source_files) == 1:
            return f"{first}_arbeitsvideo"
        return f"{first}_plus_{len(source_files)-1}_weitere_arbeitsvideo"

    def working_manifest_path(self, working_video_path: Path) -> Path:
        return working_video_path.with_suffix(".json")

    def write_working_manifest(self, working_video_path: Path, source_files: list[Path]) -> None:
        payload = {
            "sources": [p.name for p in source_files],
            "source_count": len(source_files),
        }
        self.working_manifest_path(working_video_path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def list_working_videos(self, project) -> list[Path]:
        directory = self.working_video_dir(project)
        return sorted([p for p in directory.iterdir() if p.is_file() and p.suffix.lower() == ".mp4"], key=lambda p: p.name.lower())

    def find_matching_working_video(self, project, source_files: list[Path]) -> Path | None:
        if not source_files:
            return None
        wanted = [p.name for p in source_files]
        wanted_stem = self.derive_working_video_stem(source_files)
        candidates = self.list_working_videos(project)
        # 1. Exact manifest match
        for path in candidates:
            manifest = self.working_manifest_path(path)
            if manifest.exists():
                try:
                    data = json.loads(manifest.read_text(encoding="utf-8"))
                    if data.get("sources") == wanted:
                        return path
                except Exception:
                    pass
        # 2. Name fallback
        named = self.working_video_dir(project) / f"{wanted_stem}.mp4"
        if named.exists():
            return named
        # 3. Single-source relaxed fallback
        if len(source_files) == 1:
            stem = self.sanitize_filename(source_files[0].stem, "video")
            for path in candidates:
                if path.stem.lower().startswith(stem.lower()):
                    return path
        return None

    def build_working_video(self, project, source_files: list[Path], output_stem: str | None = None) -> Path:
        ffmpeg = self._ffmpeg()
        if not ffmpeg:
            raise RuntimeError("FFmpeg wurde nicht gefunden.")
        if not source_files:
            raise ValueError("Es wurden keine Quellvideos ausgewählt.")
        stem = output_stem or self.derive_working_video_stem(source_files)
        target = self.working_video_dir(project) / f"{self.sanitize_filename(stem, 'arbeitsvideo')}.mp4"
        if len(source_files) == 1:
            cmd = [
                ffmpeg, "-y",
                "-i", str(source_files[0]),
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-crf", "18",
                "-c:a", "aac",
                "-movflags", "+faststart",
                str(target),
            ]
        else:
            inputs: list[str] = []
            parts: list[str] = []
            for idx, path in enumerate(source_files):
                inputs.extend(["-i", str(path)])
                parts.append(f"[{idx}:v:0][{idx}:a:0]")
            filter_complex = "".join(parts) + f"concat=n={len(source_files)}:v=1:a=1[v][a]"
            cmd = [
                ffmpeg, "-y", *inputs,
                "-filter_complex", filter_complex,
                "-map", "[v]",
                "-map", "[a]",
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-crf", "18",
                "-c:a", "aac",
                "-movflags", "+faststart",
                str(target),
            ]
        self._run(cmd, "Arbeitsvideo konnte nicht erzeugt werden.")
        self.write_working_manifest(target, source_files)
        return target

    def create_clip(self, project, working_video: Path, start_s: float, end_s: float, title: str) -> Path:
        ffmpeg = self._ffmpeg()
        if not ffmpeg:
            raise RuntimeError("FFmpeg wurde nicht gefunden.")
        if not working_video.exists():
            raise FileNotFoundError("Arbeitsvideo wurde nicht gefunden.")
        if end_s <= start_s:
            raise ValueError("Ende muss hinter Beginn liegen.")
        name = self.sanitize_filename(title, "clip")
        target = self.clips_output_dir(project) / f"{name}.mp4"
        cmd = [
            ffmpeg, "-y",
            "-ss", self.seconds_to_ts(start_s),
            "-to", self.seconds_to_ts(end_s),
            "-i", str(working_video),
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "18",
            "-c:a", "aac",
            "-movflags", "+faststart",
            str(target),
        ]
        self._run(cmd, f"Clip '{name}' konnte nicht erzeugt werden.")
        return target

    def open_in_system(self, path: Path) -> None:
        if os.name == "nt":
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif shutil.which("xdg-open"):
            subprocess.Popen(["xdg-open", str(path)])
        elif shutil.which("open"):
            subprocess.Popen(["open", str(path)])
        else:
            raise RuntimeError("Der Zielpfad kann auf diesem System nicht automatisch geöffnet werden.")

    def _run(self, cmd: list[str], error_prefix: str) -> None:
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as exc:
            msg = (exc.stderr or exc.stdout or "").strip()
            raise RuntimeError(f"{error_prefix} {msg}".strip()) from exc

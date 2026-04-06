from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from bleepling.models.media_item import MediaItem
from bleepling.models.project import Project
from bleepling.utils.file_types import AUDIO_EXTENSIONS, VIDEO_EXTENSIONS, ALL_MEDIA_EXTENSIONS


class MediaService:
    SCAN_BUCKETS = {
        "video": ("01_input/video", True),
        "audio": ("01_input/audio", False),
        "transcription_json": ("02_transcription/json", False),
        "times": ("03_processing/03_times", False),
        "name_candidates": ("03_processing/01_name_candidates_raw", False),
    }

    def scan_project_media(self, project: Project) -> list[MediaItem]:
        items: list[MediaItem] = []
        for bucket_name, (rel_path, recursive) in self.SCAN_BUCKETS.items():
            bucket_path = project.root_path / rel_path
            if not bucket_path.exists():
                continue
            files = bucket_path.rglob('*') if recursive else bucket_path.iterdir()
            for file_path in sorted(files, key=lambda p: str(p).lower()):
                if not file_path.is_file():
                    continue
                ext = file_path.suffix.lower()
                media_type = self._detect_media_type(ext, bucket_name)
                stat = file_path.stat()
                items.append(
                    MediaItem(
                        filename=file_path.name,
                        media_type=media_type,
                        source_bucket=bucket_name,
                        size_bytes=stat.st_size,
                        modified_at=datetime.fromtimestamp(stat.st_mtime),
                        path=file_path,
                    )
                )
        return items

    def import_files(self, project: Project, source_files: list[Path]) -> list[Path]:
        copied_targets: list[Path] = []
        for source in source_files:
            if not source.exists() or not source.is_file():
                continue
            target_dir = self._select_target_dir(project, source)
            target_path = self._get_nonconflicting_target(target_dir / source.name)
            shutil.copy2(source, target_path)
            copied_targets.append(target_path)
        return copied_targets

    def _select_target_dir(self, project: Project, source: Path) -> Path:
        ext = source.suffix.lower()
        name_lower = source.name.lower()
        if ext in VIDEO_EXTENSIONS:
            return project.root_path / "01_input" / "video"
        if ext in AUDIO_EXTENSIONS:
            return project.root_path / "01_input" / "audio"
        if ext == '.json' and 'words' in name_lower:
            return project.root_path / "02_transcription" / "json"
        if ext == '.txt' and (name_lower.endswith('.times.txt') or 'times' in name_lower):
            return project.root_path / "03_processing" / "03_times"
        if ext == '.txt' and ('namen_kandidaten' in name_lower or 'candidates' in name_lower):
            return project.root_path / "03_processing" / "01_name_candidates_raw"
        return project.root_path / "01_input" / "video"

    def _detect_media_type(self, ext: str, bucket_name: str) -> str:
        if ext in VIDEO_EXTENSIONS:
            return "Video"
        if ext in AUDIO_EXTENSIONS:
            return "Audio"
        if bucket_name == 'transcription_json':
            return 'Words-JSON'
        if bucket_name == 'times':
            return 'Times'
        if bucket_name == 'name_candidates':
            return 'Kandidaten'
        if ext in ALL_MEDIA_EXTENSIONS:
            return "Medium"
        return "Datei"

    def _get_nonconflicting_target(self, desired_path: Path) -> Path:
        if not desired_path.exists():
            return desired_path
        stem = desired_path.stem
        suffix = desired_path.suffix
        parent = desired_path.parent
        counter = 1
        while True:
            candidate = parent / f"{stem}_{counter}{suffix}"
            if not candidate.exists():
                return candidate
            counter += 1

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


@dataclass
class MediaItem:
    filename: str
    media_type: str
    source_bucket: str
    size_bytes: int
    modified_at: datetime
    path: Path

    @property
    def size_mb(self) -> float:
        return round(self.size_bytes / (1024 * 1024), 2)

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json

@dataclass
class Project:
    name: str
    root_path: Path
    language: str = "de"
    theme: str = "dark"
    version: str = "1"
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def root(self) -> Path:
        return self.root_path

    @property
    def config_dir(self) -> Path:
        return self.root_path / "99_config"

    @property
    def project_file(self) -> Path:
        return self.config_dir / "project.json"

    @property
    def blocklist_file(self) -> Path:
        return self.config_dir / "blocklist.txt"

    @property
    def allowlist_file(self) -> Path:
        return self.config_dir / "allowlist.txt"

    @property
    def app_state_file(self) -> Path:
        return self.config_dir / "app_state.json"

    @property
    def settings_file(self) -> Path:
        return self.app_state_file

    @property
    def logs_dir(self) -> Path:
        return self.root_path / "05_logs"

    @property
    def log_file(self) -> Path:
        return self.logs_dir / "project.log"

    @property
    def input_video_dir(self) -> Path:
        return self.root_path / "01_input" / "video"

    @property
    def input_audio_dir(self) -> Path:
        return self.root_path / "01_input" / "audio"

    @property
    def transcription_wav_dir(self) -> Path:
        return self.root_path / "02_transcription" / "wav"

    @property
    def candidates_raw_dir(self) -> Path:
        return self.root_path / "03_processing" / "01_name_candidates_raw"

    @property
    def candidates_reviewed_dir(self) -> Path:
        return self.root_path / "03_processing" / "02_name_candidates_reviewed"

    @property
    def times_dir(self) -> Path:
        return self.root_path / "03_processing" / "03_times"

    @property
    def output_video_dir(self) -> Path:
        return self.root_path / "04_output" / "videos"

    @property
    def transcription_json_dir(self) -> Path:
        return self.root_path / "02_transcription" / "json"

    @property
    def titlecards_output_dir(self) -> Path:
        return self.root_path / "04_output" / "titlecards"

    @property
    def titlecards_state_file(self) -> Path:
        return self.config_dir / "titlecards_state.json"


    def read_titlecards_state(self):
        defaults = {}
        try:
            if self.titlecards_state_file.exists():
                data = json.loads(self.titlecards_state_file.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    defaults.update(data)
        except Exception:
            pass
        return defaults

    def write_titlecards_state(self, data):
        merged = self.read_titlecards_state()
        if isinstance(data, dict):
            merged.update(data)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.titlecards_state_file.write_text(
            json.dumps(merged, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def read_settings(self):
        defaults = {
            "transcription_mode": "auto",
            "whisper_model": "medium",
            "compute_type": "float16",
            "extra_cuda_paths": "",
            "theme": "light",
            "render_backend": "auto",
            "render_quality": 30,
            "render_preset": "medium",
            "render_audio_bitrate": "96k",
            "render_scale": "Originalgröße beibehalten",
        }
        try:
            if self.settings_file.exists():
                data = json.loads(self.settings_file.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    defaults.update(data)
        except Exception:
            pass
        return defaults

    def write_settings(self, data):
        merged = self.read_settings()
        if isinstance(data, dict):
            merged.update(data)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.settings_file.write_text(
            json.dumps(merged, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

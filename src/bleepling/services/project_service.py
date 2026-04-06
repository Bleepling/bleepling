from __future__ import annotations

import json
from pathlib import Path

from bleepling.models.project import Project


class ProjectService:
    REQUIRED_DIRS: tuple[str, ...] = (
        "01_input/audio",
        "01_input/video",
        "01_input/video/old",
        "01_input/video/vtt_alt",
        "02_transcription/json",
        "02_transcription/wav",
        "03_processing/01_name_candidates_raw",
        "03_processing/02_name_candidates_reviewed",
        "03_processing/03_times",
        "03_processing/bleep_lists",
        "03_processing/cleaned",
        "03_processing/name_candidates",
        "04_output/videos",
        "05_logs",
        "06_presets",
        "99_config",
    )

    OPTIONAL_COMPAT_DIRS: tuple[str, ...] = (
        "99_scripts/gui_bleep_tool",
        "99_scripts/gui_bleep_tool_v3",
        "99_scripts/gui_bleep_tool_v4",
        "99_scripts/gui_bleep_tool_v5",
    )

    DEFAULT_TEXT_FILES: dict[str, str] = {
        "99_config/blocklist.txt": "",
        "99_config/allowlist.txt": "",
        "99_config/app_state.json": "{}\n",
        "05_logs/project.log": "",
    }

    def create_project(self, base_dir: Path, project_name: str) -> Project:
        safe_name = project_name.strip()
        if not safe_name:
            raise ValueError("Der Projektname darf nicht leer sein.")

        root_path = base_dir / safe_name
        if root_path.exists() and any(root_path.iterdir()):
            raise FileExistsError("Der Zielordner existiert bereits und ist nicht leer.")

        root_path.mkdir(parents=True, exist_ok=True)
        for rel_dir in self.REQUIRED_DIRS + self.OPTIONAL_COMPAT_DIRS:
            (root_path / rel_dir).mkdir(parents=True, exist_ok=True)

        for rel_file, content in self.DEFAULT_TEXT_FILES.items():
            target = root_path / rel_file
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")

        project = Project(name=safe_name, root_path=root_path)
        self.save_project(project)
        return project

    def save_project(self, project: Project) -> None:
        payload = {
            "name": project.name,
            "root_path": str(project.root_path),
            "language": project.language,
            "theme": project.theme,
            "version": project.version,
            "metadata": project.metadata,
        }
        project.project_file.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def load_project(self, project_root: Path) -> Project:
        project_file = project_root / "99_config" / "project.json"
        if not project_file.exists():
            raise FileNotFoundError("project.json wurde nicht gefunden.")

        payload = json.loads(project_file.read_text(encoding="utf-8"))
        return Project(
            name=payload["name"],
            root_path=Path(payload["root_path"]),
            language=payload.get("language", "de"),
            theme=payload.get("theme", "dark"),
            version=payload.get("version", "1"),
            metadata=payload.get("metadata", {}),
        )

    def validate_project(self, project_root: Path) -> list[str]:
        missing: list[str] = []
        for rel_dir in self.REQUIRED_DIRS:
            if not (project_root / rel_dir).exists():
                missing.append(rel_dir)
        if not (project_root / "99_config" / "project.json").exists():
            missing.append("99_config/project.json")
        return missing

    def get_project_summary(self, project: Project) -> dict[str, str]:
        return {
            "Projektname": project.name,
            "Projektordner": str(project.root_path),
            "Sprache": project.language,
            "Theme": project.theme,
            "Version": project.version,
        }

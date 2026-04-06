from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from bleepling.models.project import Project


@dataclass
class DiagnosticItem:
    name: str
    status: str
    details: str


class EnvironmentService:
    COMMON_CUDA_BASES = [
        Path(r"C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA"),
        Path(r"C:/Program Files/NVIDIA/CUDNN"),
        Path(r"C:/Program Files/"),
        Path(r"C:/ProgramData"),
        Path.home() / "AppData/Local/Programs",
        Path.home() / ".lmstudio/extensions/backends/vendor",
        Path.home() / ".docker/bin",
    ]

    CUDA_DLLS = [
        "cublas64_12.dll",
        "cublasLt64_12.dll",
        "cudart64_12.dll",
        "cudnn64_9.dll",
        "cudnn_ops64_9.dll",
        "cudnn_cnn64_9.dll",
        "cudnn_adv64_9.dll",
    ]

    def diagnose(self, project: Project | None, extra_cuda_paths: Iterable[str] | None = None) -> list[DiagnosticItem]:
        items: list[DiagnosticItem] = []
        items.append(self._diagnose_python())
        items.append(self._diagnose_ffmpeg())
        items.append(self._diagnose_python_module("faster_whisper", "Python-Modul faster-whisper"))
        items.append(self._diagnose_python_module("ctranslate2", "Python-Modul ctranslate2"))
        items.append(self._diagnose_python_module("openpyxl", "Python-Modul openpyxl (XLSX-Import)"))
        items.append(self._diagnose_python_module("docx", "Python-Modul python-docx (DOCX-Import)"))
        items.append(self._diagnose_python_module("pdfplumber", "Python-Modul pdfplumber (PDF-Tabellenimport)"))
        items.append(self._diagnose_any_python_module(("pypdf", "PyPDF2"), "Python-Modul pypdf/PyPDF2 (einfacher PDF-Import)"))
        items.extend(self._diagnose_cuda(extra_cuda_paths or []))
        if project:
            items.append(self._diagnose_project_log(project))
        return items

    def get_recommended_cuda_paths(self, extra_cuda_paths: Iterable[str] | None = None) -> list[Path]:
        discovered: list[Path] = []
        seen: set[str] = set()
        for raw in extra_cuda_paths or []:
            try:
                path = Path(str(raw)).expanduser()
            except Exception:
                continue
            if path.exists():
                key = str(path).lower()
                if key not in seen:
                    seen.add(key)
                    discovered.append(path)
        for base in self.COMMON_CUDA_BASES:
            if not base.exists():
                continue
            try:
                matches = list(base.rglob("cublas64_12.dll"))
            except Exception:
                matches = []
            for match in matches[:20]:
                parent = match.parent
                key = str(parent).lower()
                if key not in seen:
                    seen.add(key)
                    discovered.append(parent)
        return discovered

    def build_runtime_env(self, extra_cuda_paths: Iterable[str] | None = None) -> dict[str, str]:
        env = os.environ.copy()
        path_entries = env.get("PATH", "").split(os.pathsep) if env.get("PATH") else []
        normalized = {p.lower() for p in path_entries if p}
        for path in self.get_recommended_cuda_paths(extra_cuda_paths):
            text = str(path)
            if text.lower() not in normalized:
                path_entries.insert(0, text)
                normalized.add(text.lower())
        env["PATH"] = os.pathsep.join(path_entries)
        return env

    def get_installation_help_text(self) -> str:
        return (
            "Empfehlung für Windows:\n"
            "1) Python-Pakete wie faster-whisper und ctranslate2 gehören in dieselbe Python-Umgebung, mit der Bleepling gestartet wird.\n"
            "2) CUDA-/cuDNN-DLLs müssen in einem Ordner liegen, der für den Bleepling-Prozess erreichbar ist, idealerweise in einem dedizierten CUDA-bin-Ordner oder in einem von Bleepling konfigurierten Zusatzpfad.\n"
            "3) Nach einer Nachinstallation bitte die Prüfung erneut ausführen.\n"
            "4) Für fremde PCs ist ein konfigurierbarer Zusatzpfad robuster als verteilte Einzel-DLLs in zufälligen Programmen."
        )

    def get_install_command(self) -> str:
        py = shutil.which("python") or sys.executable or "python"
        return (
            f'"{py}" -m pip install -U pip setuptools wheel\n'
            f'"{py}" -m pip install -U faster-whisper ctranslate2 openpyxl python-docx pdfplumber pypdf PyPDF2'
        )

    def get_path_command(self, extra_cuda_paths: Iterable[str] | None = None) -> str:
        paths = [str(p) for p in self.get_recommended_cuda_paths(extra_cuda_paths)]
        if not paths:
            return "Keine CUDA-Pfade gefunden. Bitte zuerst einen Zusatzpfad eintragen oder CUDA/cuDNN installieren."
        joined = ";".join(paths)
        return f'set PATH={joined};%PATH%'

    def _diagnose_python(self) -> DiagnosticItem:
        return DiagnosticItem("Python", "ok", sys.executable)

    def _diagnose_ffmpeg(self) -> DiagnosticItem:
        ffmpeg = shutil.which("ffmpeg")
        if ffmpeg:
            return DiagnosticItem("FFmpeg", "ok", ffmpeg)
        return DiagnosticItem("FFmpeg", "warn", "FFmpeg wurde im PATH nicht gefunden.")

    def _diagnose_python_module(self, module_name: str, label: str) -> DiagnosticItem:
        try:
            __import__(module_name)
            return DiagnosticItem(label, "ok", "verfügbar")
        except Exception as exc:
            return DiagnosticItem(label, "warn", f"fehlt oder nicht ladbar: {exc}")


    def _diagnose_any_python_module(self, module_names: tuple[str, ...], label: str) -> DiagnosticItem:
        errors = []
        for module_name in module_names:
            try:
                __import__(module_name)
                return DiagnosticItem(label, "ok", f"verfügbar über {module_name}")
            except Exception as exc:
                errors.append(f"{module_name}: {exc}")
        return DiagnosticItem(label, "warn", "fehlt oder nicht ladbar: " + " | ".join(errors))

    def _diagnose_cuda(self, extra_cuda_paths: Iterable[str]) -> list[DiagnosticItem]:
        items: list[DiagnosticItem] = []
        discovered = self.get_recommended_cuda_paths(extra_cuda_paths)
        if discovered:
            items.append(DiagnosticItem("CUDA-Pfade", "ok", "\n".join(str(p) for p in discovered[:12])))
        else:
            items.append(DiagnosticItem("CUDA-Pfade", "warn", "Keine passenden CUDA-Verzeichnisse mit cublas64_12.dll gefunden."))

        env = self.build_runtime_env(extra_cuda_paths)
        for dll_name in self.CUDA_DLLS:
            found = self._find_dll_in_path(dll_name, env.get("PATH", ""))
            if found:
                items.append(DiagnosticItem(dll_name, "ok", str(found)))
            else:
                items.append(DiagnosticItem(dll_name, "warn", "im Bleepling-Laufzeitpfad nicht gefunden"))

        gpu_test = self._probe_gpu_python(env)
        items.append(gpu_test)
        return items

    def _find_dll_in_path(self, dll_name: str, path_value: str) -> Path | None:
        for entry in [p for p in path_value.split(os.pathsep) if p]:
            try:
                candidate = Path(entry) / dll_name
            except Exception:
                continue
            if candidate.exists():
                return candidate
        return None

    def _probe_gpu_python(self, env: dict[str, str]) -> DiagnosticItem:
        code = (
            "import sys\n"
            "try:\n"
            " import ctranslate2\n"
            " print('CT2_OK')\n"
            " translator = ctranslate2.Translator('cpu', device='cpu') if False else None\n"
            " print('IMPORT_OK')\n"
            "except Exception as exc:\n"
            " print(type(exc).__name__ + ': ' + str(exc))\n"
            " sys.exit(2)\n"
        )
        try:
            result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env, timeout=20)
        except Exception as exc:
            return DiagnosticItem("GPU-Probe", "warn", f"Probe konnte nicht ausgeführt werden: {exc}")
        if result.returncode == 0:
            return DiagnosticItem("GPU-Probe", "ok", (result.stdout or "Import erfolgreich").strip())
        details = ((result.stderr or "") + "\n" + (result.stdout or "")).strip()
        if not details:
            details = "Import von ctranslate2 fehlgeschlagen."
        return DiagnosticItem("GPU-Probe", "warn", details)

    def _diagnose_project_log(self, project: Project) -> DiagnosticItem:
        try:
            path = project.log_file
            if path.exists():
                return DiagnosticItem("Projektlog", "ok", str(path))
        except Exception:
            pass
        return DiagnosticItem("Projektlog", "warn", "Projektlog nicht gefunden.")

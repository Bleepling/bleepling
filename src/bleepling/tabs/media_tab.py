
from __future__ import annotations
import os
import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
import re
import shutil

from bleepling.utils.help_dialog import show_help_dialog

try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None


def _list_files(directory: Path, exts: set[str]):
    if not directory.exists():
        return []
    return sorted([p.name for p in directory.iterdir() if p.is_file() and p.suffix.lower() in exts], key=str.lower)


def _list_paths(directory: Path, exts: set[str]):
    if not directory.exists():
        return []
    return sorted([p for p in directory.iterdir() if p.is_file() and p.suffix.lower() in exts], key=lambda p: p.name.lower())


class MediaTab(ttk.Frame):
    def __init__(self, master, app, set_status=None):
        super().__init__(master)
        self.app = app
        self._external_set_status = set_status
        self.bird_img = None
        self.section_rows: list[ttk.Frame] = []

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=12, pady=12)
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        left = ttk.Frame(body)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.grid_rowconfigure(0, weight=1)
        left.grid_columnconfigure(0, weight=1)
        left.grid_columnconfigure(1, weight=0)

        self.list_canvas = tk.Canvas(left, highlightthickness=0)
        self.list_canvas.grid(row=0, column=0, sticky="nsew")
        yscroll = ttk.Scrollbar(left, orient="vertical", command=self.list_canvas.yview)
        yscroll.grid(row=0, column=1, sticky="ns")
        self.list_canvas.configure(yscrollcommand=yscroll.set)
        self.list_inner = ttk.Frame(self.list_canvas)
        self.list_inner.bind("<Configure>", lambda _e: self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all")))
        self.list_canvas.create_window((0, 0), window=self.list_inner, anchor="nw")

        right = ttk.Frame(body)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(0, weight=0)
        right.grid_rowconfigure(1, weight=1)
        right.grid_rowconfigure(2, weight=0)
        right.grid_rowconfigure(3, weight=1)
        right.grid_columnconfigure(0, weight=1)

        controls = ttk.Frame(right)
        controls.grid(row=0, column=0, sticky="ne", pady=(0, 8))
        ttk.Button(controls, text="Video importieren", command=self.import_video, style="Accent.TButton").pack(side="left")
        ttk.Button(controls, text="WAV importieren", command=self.import_wav, style="Accent.TButton").pack(side="left", padx=6)
        ttk.Button(controls, text="Liste aktualisieren", command=self.refresh, style="Accent.TButton").pack(side="left", padx=6)
        ttk.Button(controls, text="?", width=3, command=self.show_help, style="Accent.TButton").pack(side="left", padx=(6, 0))

        ttk.Frame(right).grid(row=1, column=0, sticky="nsew")
        self.bird_label = ttk.Label(right)
        self.bird_label.grid(row=2, column=0, sticky="n")
        ttk.Frame(right).grid(row=3, column=0, sticky="nsew")

        self.refresh()

    def _asset(self, name: str) -> Path:
        return Path(__file__).resolve().parents[3] / "assets" / name

    def _set_status(self, msg: str):
        if callable(self._external_set_status):
            self._external_set_status(msg)
        elif hasattr(self.app, "set_status"):
            self.app.set_status(msg)

    def _open_directory(self, directory: Path):
        directory.mkdir(parents=True, exist_ok=True)
        try:
            Path(directory)
            if hasattr(os, "startfile"):
                os.startfile(str(directory))
            else:
                raise OSError("Ordner konnte nicht mit dem System geöffnet werden.")
        except Exception as exc:
            self._set_status(f"Ordner konnte nicht geöffnet werden: {exc}")

    def _working_video_dir(self, project) -> Path:
        path = project.root_path / "03_processing" / "04_cutting" / "working_video"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _output_audio_dir(self, project) -> Path:
        path = project.root_path / "04_output" / "audio"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _clips_output_dir(self, project) -> Path:
        return project.input_video_dir

    def _is_clip_video(self, path: Path) -> bool:
        stem = path.stem.lower()
        return bool(re.search(r"(?:^|[_-])clip(?:[_-]|\d|$)", stem))

    def show_help(self):
        show_help_dialog(
            self,
            "Hilfe – Medien",
            "Hier findest du die wichtigsten Projektdateien nach Bereichen geordnet. "
            "Der Reiter dient als schnelle Übersicht und als Sprungbrett in die jeweiligen Projektordner.\n\n"
            "Angezeigt werden zum Beispiel Quellvideos, Projektclips, Transkriptionsdateien, "
            "Times-Dateien, Arbeitsvideos, Output-Dateien und Titelkarten.\n\n"
            "Mit 'Liste aktualisieren' werden die relevanten Projektordner neu eingelesen. "
            "Mit 'Ordner öffnen' springst du direkt in den passenden Ordner des aktuellen Abschnitts.",
        )

    def _append_section(self, title: str, directory: Path, exts: set[str], files: list[Path] | None = None):
        section = ttk.Frame(self.list_inner)
        section.pack(fill="x", anchor="n", pady=(0, 4))
        self.section_rows.append(section)

        header = ttk.Frame(section)
        header.pack(fill="x")
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text=f"{title} ({directory}):", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Button(
            header,
            text="Ordner öffnen",
            command=lambda d=directory: self._open_directory(d),
            width=18,
        ).grid(row=0, column=1, sticky="e", padx=(8, 0))

        names = [p.name for p in files] if files is not None else _list_files(directory, exts)
        content = ttk.Frame(section)
        content.pack(fill="x", pady=(1, 0))
        if names:
            for name in names:
                ttk.Label(content, text=name, justify="left").pack(anchor="w")
        else:
            ttk.Label(content, text="-", justify="left").pack(anchor="w")

    def _refresh_bird(self):
        theme = getattr(self.app, "current_theme", "light")
        bird_name = "vogel3_dark_512.png" if theme == "dark" else "vogel3_light_512.png"
        bird_path = self._asset(bird_name)
        if Image is not None and ImageTk is not None and bird_path.exists():
            img = Image.open(bird_path)
            self.bird_img = ImageTk.PhotoImage(img)
            self.bird_label.configure(image=self.bird_img, text="")
        else:
            self.bird_label.configure(image="", text="🐤")

    def import_video(self):
        if not self.app.project:
            self._set_status("Kein Projekt geladen.")
            return
        path = filedialog.askopenfilename(filetypes=[("Videos", "*.mp4 *.mov *.mkv *.avi *.m4v *.wmv")])
        if not path:
            return
        shutil.copy2(path, self.app.project.input_video_dir / Path(path).name)
        self.refresh()
        try:
            self.app.bleeping_tab.refresh()
        except Exception:
            pass
        self._set_status(f"Video importiert: {Path(path).name}")

    def import_wav(self):
        if not self.app.project:
            self._set_status("Kein Projekt geladen.")
            return
        path = filedialog.askopenfilename(filetypes=[("Audio", "*.wav")])
        if not path:
            return
        shutil.copy2(path, self.app.project.transcription_wav_dir / Path(path).name)
        self.refresh()
        try:
            self.app.bleeping_tab.refresh()
        except Exception:
            pass
        self._set_status(f"WAV importiert: {Path(path).name}")

    def refresh(self):
        self._refresh_bird()
        for child in self.list_inner.winfo_children():
            child.destroy()
        self.section_rows.clear()
        if not self.app.project:
            ttk.Label(self.list_inner, text="Kein Projekt geladen.").pack(anchor="w")
            return

        p = self.app.project
        video_exts = {".mp4", ".mov", ".mkv", ".avi", ".m4v", ".wmv"}
        audio_exts = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg"}
        image_exts = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}
        source_video_paths = _list_paths(p.input_video_dir, video_exts)
        source_videos = [path for path in source_video_paths if not self._is_clip_video(path)]
        clip_videos = [path for path in source_video_paths if self._is_clip_video(path)]
        working_video_paths = _list_paths(self._working_video_dir(p), {".mp4"})
        working_video_meta = _list_paths(self._working_video_dir(p), {".json"})

        self._append_section("Quellvideos", p.input_video_dir, video_exts, source_videos)
        self._append_section("Projektclips", self._clips_output_dir(p), video_exts, clip_videos)
        self._append_section("Quell-Audiodateien", p.input_audio_dir, audio_exts)
        self._append_section("Transkriptions-WAV", p.transcription_wav_dir, {".wav"})
        self._append_section("Transkriptions-JSON / words.json", p.transcription_json_dir, {".json"})
        self._append_section("Kandidaten roh", p.candidates_raw_dir, {".txt"})
        self._append_section("Kandidaten geprüft", p.candidates_reviewed_dir, {".txt"})
        self._append_section("Times-Dateien", p.times_dir, {".txt"})
        self._append_section("Arbeitsvideos", self._working_video_dir(p), {".mp4"}, working_video_paths)
        self._append_section("Arbeitsvideo-Metadaten", self._working_video_dir(p), {".json"}, working_video_meta)
        self._append_section("Output-Videos", p.output_video_dir, video_exts)
        self._append_section("Output-Audio", self._output_audio_dir(p), audio_exts)
        self._append_section("Titelkarten / Bilddateien", p.titlecards_output_dir, image_exts)
        self.list_canvas.yview_moveto(0)


from __future__ import annotations
import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
import shutil

try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None


def _list_files(directory: Path, exts: set[str]):
    if not directory.exists():
        return []
    return sorted([p.name for p in directory.iterdir() if p.is_file() and p.suffix.lower() in exts], key=str.lower)


class MediaTab(ttk.Frame):
    def __init__(self, master, app, set_status=None):
        super().__init__(master)
        self.app = app
        self._external_set_status = set_status
        self.bird_img = None

        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=12, pady=12)

        ttk.Button(bar, text="Video importieren", command=self.import_video, style="Accent.TButton").pack(side="left")
        ttk.Button(bar, text="WAV importieren", command=self.import_wav, style="Accent.TButton").pack(side="left", padx=6)
        ttk.Button(bar, text="Liste aktualisieren", command=self.refresh, style="Accent.TButton").pack(side="left", padx=6)

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        left = ttk.Frame(body)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.grid_rowconfigure(0, weight=1)
        left.grid_columnconfigure(0, weight=1)

        self.text = tk.Text(left, height=24, wrap="none")
        self.text.grid(row=0, column=0, sticky="nsew")

        right = ttk.Frame(body)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=0)
        right.grid_rowconfigure(2, weight=1)
        right.grid_columnconfigure(0, weight=1)

        ttk.Frame(right).grid(row=0, column=0, sticky="nsew")
        self.bird_label = ttk.Label(right)
        self.bird_label.grid(row=1, column=0, sticky="n")
        ttk.Frame(right).grid(row=2, column=0, sticky="nsew")

        self.refresh()

    def _asset(self, name: str) -> Path:
        return Path(__file__).resolve().parents[3] / "assets" / name

    def _set_status(self, msg: str):
        if callable(self._external_set_status):
            self._external_set_status(msg)
        elif hasattr(self.app, "set_status"):
            self.app.set_status(msg)

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
        self.text.delete("1.0", "end")
        if not self.app.project:
            self.text.insert("end", "Kein Projekt geladen.")
            return

        p = self.app.project
        self.text.insert("end", "Videos:\n")
        for f in _list_files(p.input_video_dir, {".mp4", ".mov", ".mkv", ".avi", ".m4v", ".wmv"}):
            self.text.insert("end", f"  {f}\n")

        self.text.insert("end", "\nWAV:\n")
        for f in _list_files(p.transcription_wav_dir, {".wav"}):
            self.text.insert("end", f"  {f}\n")

        self.text.insert("end", "\nwords.json:\n")
        for f in _list_files(p.transcription_json_dir, {".json"}):
            self.text.insert("end", f"  {f}\n")

        self.text.insert("end", "\nKandidaten:\n")
        for f in _list_files(p.candidates_raw_dir, {".txt"}):
            self.text.insert("end", f"  {f}\n")

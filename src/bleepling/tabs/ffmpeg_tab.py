from __future__ import annotations
import json
import os
import queue
import shutil
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, simpledialog, ttk

try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None

VIDEO_CODEC_OPTIONS = {
    "H.264 (GPU / NVIDIA, schnell)": "h264_nvenc",
    "H.264 (CPU, sehr kompatibel)": "libx264",
    "H.265 (CPU, kleinere Dateien)": "libx265",
}
AUDIO_CODEC_OPTIONS = {
    "AAC (für MP4/Video empfohlen)": "aac",
    "MP3 (für reine Audiodateien)": "mp3",
}
SCALE_OPTIONS = {
    "Originalgröße beibehalten": "iw:-2",
    "1280 px Breite (kleiner für Web)": "1280:-2",
    "1920 px Breite (größer / Full HD)": "1920:-2",
}
PRESET_LEVELS = ["ultrafast", "superfast", "veryfast", "fast", "medium", "slow", "veryslow"]
NVENC_PRESET_MAP = {
    "ultrafast": "p1",
    "superfast": "p2",
    "veryfast": "p3",
    "fast": "p4",
    "medium": "p5",
    "slow": "p6",
    "veryslow": "p7",
}

def _list_files(directory: Path, exts: set[str]):
    if not directory.exists():
        return []
    return sorted([p.name for p in directory.iterdir() if p.is_file() and p.suffix.lower() in exts], key=str.lower)

def _read_lines(path: Path):
    if not path.exists():
        return []
    return [x.strip() for x in path.read_text(encoding="utf-8", errors="ignore").splitlines() if x.strip()]

def _fmt_mb(num_bytes):
    try:
        return f"{float(num_bytes) / (1024 * 1024):.1f} MB"
    except Exception:
        return "-"

def _fmt_mmss(seconds):
    try:
        total = int(round(float(seconds)))
    except Exception:
        return "-"
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

def _safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default

def _safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default

def _fps_from_ratio(ratio: str) -> float:
    try:
        if "/" in ratio:
            a, b = ratio.split("/", 1)
            a = float(a); b = float(b)
            if b:
                return a / b
        return float(ratio)
    except Exception:
        return 0.0

class FFmpegTab(ttk.Frame):
    def __init__(self, master, app, set_status=None):
        super().__init__(master)
        self.app = app
        self._external_set_status = set_status
        self.proc = None
        self.progress_win = None
        self.progress_img = None
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_text_var = tk.StringVar(value="")
        self.render_queue = queue.Queue()
        self.media_info = {}
        self._build()

    def _asset(self, name: str) -> Path:
        return Path(__file__).resolve().parents[3] / "assets" / name

    def _project(self):
        return getattr(self.app, "project", None)

    def _output_video_dir(self, p) -> Path:
        return getattr(p, "output_video_dir", p.root_path / "04_output" / "videos")

    def _output_audio_dir(self, p) -> Path:
        return p.root_path / "04_output" / "audio"

    def _ffmpeg(self):
        return shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")

    def _ffprobe(self):
        return shutil.which("ffprobe") or shutil.which("ffprobe.exe")

    def _presets_file(self) -> Path:
        base = Path.home() / ".bleepling"
        base.mkdir(parents=True, exist_ok=True)
        return base / "export_profiles.json"

    def _load_saved_profiles(self) -> dict:
        try:
            p = self._presets_file()
            if p.exists():
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
        return {}

    def _save_saved_profiles(self, data: dict):
        self._presets_file().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _settings(self):
        p = self._project()
        return p.read_settings() if p else {}

    def _set_status(self, msg: str):
        if callable(self._external_set_status):
            self._external_set_status(msg)
        elif hasattr(self.app, "set_status"):
            self.app.set_status(msg)
        try:
            self.log_box.delete("1.0", "end")
            self.log_box.insert("1.0", msg)
        except Exception:
            pass

    def _media_path(self) -> Path | None:
        p = self._project()
        if not p or not self.media_var.get():
            return None
        name = self.media_var.get()
        v = p.input_video_dir / name
        a = p.input_audio_dir / name
        if v.exists():
            return v
        if a.exists():
            return a
        return None

    def _probe_media(self, media_path: Path) -> dict:
        ffprobe = self._ffprobe()
        if not ffprobe or not media_path.exists():
            return {}
        try:
            cmd = [ffprobe, "-v", "error", "-show_entries", "stream=width,height,codec_name,r_frame_rate,codec_type:format=duration,size,bit_rate", "-of", "json", str(media_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout or "{}")
            streams = data.get("streams") or []
            fmt = data.get("format") or {}
            v = next((s for s in streams if s.get("codec_type") == "video"), None)
            a = next((s for s in streams if s.get("codec_type") == "audio"), None)
            return {
                "has_video": v is not None,
                "has_audio": a is not None,
                "width": _safe_int(v.get("width")) if v else 0,
                "height": _safe_int(v.get("height")) if v else 0,
                "video_codec": (v or {}).get("codec_name", "-"),
                "audio_codec": (a or {}).get("codec_name", "-"),
                "fps": _fps_from_ratio((v or {}).get("r_frame_rate", "0/1")) if v else 0.0,
                "duration": _safe_float(fmt.get("duration")),
                "size_bytes": _safe_int(fmt.get("size")),
                "bit_rate": _safe_int(fmt.get("bit_rate")),
            }
        except Exception:
            return {}

    def _effective_video_codec(self) -> str:
        chosen = VIDEO_CODEC_OPTIONS.get(self.video_codec_display.get(), "h264_nvenc")
        backend = self._settings().get("render_backend", "auto")
        gpu_ok = shutil.which("nvidia-smi") is not None
        if backend == "cpu" and chosen == "h264_nvenc":
            return "libx264"
        if backend == "gpu" and gpu_ok and chosen == "libx264":
            return "h264_nvenc"
        if backend == "auto" and chosen == "h264_nvenc" and not gpu_ok:
            return "libx264"
        return chosen

    def _effective_preset(self) -> str:
        vis = self.preset_display.get()
        codec = self._effective_video_codec()
        return NVENC_PRESET_MAP.get(vis, "p5") if codec == "h264_nvenc" else vis

    def _refresh_profile_list(self):
        names = sorted(self._load_saved_profiles().keys(), key=str.lower)
        self.saved_profile_combo["values"] = names
        if names and not self.profile_name_var.get():
            self.profile_name_var.set(names[0])

    def _refresh_media_info(self):
        media_path = self._media_path()
        if not media_path:
            self.media_info = {}
            self.source_info_var.set("Ausgangsmedium: -")
            return
        self.media_info = self._probe_media(media_path)
        info = self.media_info
        if info:
            if info.get("has_video"):
                txt = f"Ausgangsmedium: {info.get('video_codec','-')} / {info.get('audio_codec','-')} | {info.get('width',0)}x{info.get('height',0)} | {info.get('fps',0):.2f} fps | {_fmt_mmss(info.get('duration'))} | {_fmt_mb(info.get('size_bytes'))}"
            else:
                txt = f"Ausgangsmedium: reine Audiodatei ({info.get('audio_codec','-')}) | {_fmt_mmss(info.get('duration'))} | {_fmt_mb(info.get('size_bytes'))}"
        else:
            txt = "Ausgangsmedium: Werte konnten nicht vollständig gelesen werden"
        self.source_info_var.set(txt)

    def refresh(self):
        p = self._project()
        if not p:
            return
        files = []
        files.extend(_list_files(p.input_video_dir, {".mp4", ".mov", ".mkv", ".avi", ".m4v", ".wmv"}))
        files.extend(_list_files(p.input_audio_dir, {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg"}))
        files = sorted(set(files), key=str.lower)
        self.media_combo["values"] = files
        self.times_combo["values"] = _list_files(p.times_dir, {".txt"})
        if files and (not self.media_var.get() or self.media_var.get() not in files):
            self.media_var.set(files[0])
        if self.times_combo["values"] and (not self.times_var.get() or self.times_var.get() not in self.times_combo["values"]):
            preferred = None
            if self.media_var.get():
                stem = Path(self.media_var.get()).stem
                for name in self.times_combo["values"]:
                    if name.startswith(stem):
                        preferred = name
                        break
            self.times_var.set(preferred or self.times_combo["values"][0])
        if not self.output_name_var.get().strip() and self.media_var.get():
            self._on_media_changed()
        self._refresh_media_info()
        self._update_estimates()
        self._refresh_profile_list()

    def _build(self):
        self.media_var = tk.StringVar()
        self.times_var = tk.StringVar()
        self.output_name_var = tk.StringVar()
        self.video_codec_display = tk.StringVar(value="H.264 (GPU / NVIDIA, schnell)")
        self.audio_codec_display = tk.StringVar(value="AAC (für MP4/Video empfohlen)")
        self.crf_var = tk.IntVar(value=30)
        self.audio_bitrate_var = tk.StringVar(value="96k")
        self.scale_display = tk.StringVar(value="1280 px Breite (kleiner für Web)")
        self.preset_display = tk.StringVar(value="medium")
        self.faststart_var = tk.BooleanVar(value=True)
        self.bleep_freq_var = tk.IntVar(value=1000)
        self.bleep_gain_var = tk.DoubleVar(value=0.70)
        self.bleep_pre_ms_var = tk.IntVar(value=600)
        self.bleep_post_ms_var = tk.IntVar(value=1000)
        self.mode_var = tk.StringVar(value="web")
        self.profile_name_var = tk.StringVar(value="")
        self.source_info_var = tk.StringVar(value="Ausgangsmedium: -")
        self.estimate_size_var = tk.StringVar(value="Voraussichtliche Ausgabegröße: -")
        self.estimate_time_var = tk.StringVar(value="Voraussichtliche Renderdauer: -")

        top = ttk.LabelFrame(self, text="Quelle und Ausgabe")
        top.pack(fill="x", padx=10, pady=10)
        top.grid_columnconfigure(1, weight=1)
        ttk.Label(top, text="Mediadatei im Projekt").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        self.media_combo = ttk.Combobox(top, textvariable=self.media_var, width=46, state="readonly")
        self.media_combo.grid(row=0, column=1, sticky="we", padx=8, pady=4)
        self.media_combo.bind("<<ComboboxSelected>>", lambda e: self._on_media_changed())
        ttk.Button(top, text="Liste aktualisieren", command=self.refresh, style="Accent.TButton").grid(row=0, column=2, sticky="w", padx=8, pady=4)
        ttk.Label(top, text="Times-Datei").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        self.times_combo = ttk.Combobox(top, textvariable=self.times_var, width=46, state="readonly")
        self.times_combo.grid(row=1, column=1, sticky="we", padx=8, pady=4)
        ttk.Button(top, text="Datei auswählen", command=self.choose_times, style="Accent.TButton").grid(row=1, column=2, sticky="w", padx=8, pady=4)
        ttk.Label(top, text="Ausgabedatei").grid(row=2, column=0, sticky="w", padx=8, pady=4)
        ttk.Entry(top, textvariable=self.output_name_var, width=49).grid(row=2, column=1, sticky="we", padx=8, pady=4)
        ttk.Button(top, text="Web-Standard setzen", command=self.set_web_defaults, style="Accent.TButton").grid(row=2, column=2, sticky="w", padx=8, pady=4)
        ttk.Label(top, textvariable=self.source_info_var).grid(row=3, column=0, columnspan=3, sticky="w", padx=8, pady=(4, 8))

        profile = ttk.LabelFrame(self, text="Exportprofil")
        profile.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Label(profile, text="Profil").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        ttk.Combobox(profile, textvariable=self.mode_var, state="readonly", width=18, values=["web", "qualität", "kleinste datei", "wie quellvideo"]).grid(row=0, column=1, sticky="w", padx=8, pady=4)
        ttk.Button(profile, text="Profil anwenden", command=self.apply_profile, style="Accent.TButton").grid(row=0, column=2, sticky="w", padx=8, pady=4)
        ttk.Label(profile, text="Eigenes Profil").grid(row=0, column=3, sticky="w", padx=8, pady=4)
        self.saved_profile_combo = ttk.Combobox(profile, textvariable=self.profile_name_var, state="readonly", width=20)
        self.saved_profile_combo.grid(row=0, column=4, sticky="w", padx=8, pady=4)
        ttk.Button(profile, text="Profil laden", command=self.load_custom_profile, style="Accent.TButton").grid(row=0, column=5, sticky="w", padx=8, pady=4)
        ttk.Button(profile, text="Profil speichern", command=self.save_custom_profile, style="Accent.TButton").grid(row=0, column=6, sticky="w", padx=8, pady=4)

        ttk.Label(profile, text="Video-Codec").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        ttk.Combobox(profile, textvariable=self.video_codec_display, state="readonly", width=32, values=list(VIDEO_CODEC_OPTIONS.keys())).grid(row=1, column=1, columnspan=2, sticky="w", padx=8, pady=4)
        ttk.Label(profile, text="Preset").grid(row=1, column=3, sticky="w", padx=8, pady=4)
        ttk.Combobox(profile, textvariable=self.preset_display, state="readonly", width=12, values=PRESET_LEVELS).grid(row=1, column=4, sticky="w", padx=8, pady=4)
        ttk.Label(profile, text="Qualität (CQ/CRF)").grid(row=1, column=5, sticky="w", padx=8, pady=4)
        ttk.Spinbox(profile, from_=18, to=38, textvariable=self.crf_var, width=5).grid(row=1, column=6, sticky="w", padx=8, pady=4)

        ttk.Label(profile, text="Audio-Codec").grid(row=2, column=0, sticky="w", padx=8, pady=4)
        ttk.Combobox(profile, textvariable=self.audio_codec_display, state="readonly", width=32, values=list(AUDIO_CODEC_OPTIONS.keys())).grid(row=2, column=1, columnspan=2, sticky="w", padx=8, pady=4)
        ttk.Label(profile, text="Audio-Bitrate").grid(row=2, column=3, sticky="w", padx=8, pady=4)
        ttk.Combobox(profile, textvariable=self.audio_bitrate_var, state="readonly", width=12, values=["64k", "96k", "128k", "160k", "192k"]).grid(row=2, column=4, sticky="w", padx=8, pady=4)
        ttk.Label(profile, text="Skalierung").grid(row=2, column=5, sticky="w", padx=8, pady=4)
        ttk.Combobox(profile, textvariable=self.scale_display, state="readonly", width=28, values=list(SCALE_OPTIONS.keys())).grid(row=2, column=6, sticky="w", padx=8, pady=4)
        ttk.Checkbutton(profile, text="Web-Optimierung (faststart)", variable=self.faststart_var).grid(row=3, column=0, columnspan=2, sticky="w", padx=8, pady=(2, 4))
        ttk.Label(profile, textvariable=self.estimate_size_var).grid(row=4, column=0, columnspan=7, sticky="w", padx=8, pady=(4, 2))
        ttk.Label(profile, textvariable=self.estimate_time_var).grid(row=5, column=0, columnspan=7, sticky="w", padx=8, pady=(0, 8))

        helpf = ttk.LabelFrame(self, text="Erklärung")
        helpf.pack(fill="x", padx=10, pady=(0, 10))
        help_text = "Standard ist eine kleine browserkompatible Ausgabe. H.264 ist für Web am kompatibelsten. AAC ist für MP4/Video empfohlen; MP3 eignet sich für reine Audiodateien. Die Größen- und Zeitschätzung ist nur grob."
        ttk.Label(helpf, text=help_text, wraplength=1200, justify="left").pack(anchor="w", padx=8, pady=8)

        bleepf = ttk.LabelFrame(self, text="Bleep-Parameter")
        bleepf.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Label(bleepf, text="Bleep-Frequenz (Hz)").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        ttk.Spinbox(bleepf, from_=400, to=3000, increment=50, textvariable=self.bleep_freq_var, width=8).grid(row=0, column=1, sticky="w", padx=8, pady=4)
        ttk.Label(bleepf, text="Bleep-Lautstärke (0.0 - 1.0)").grid(row=0, column=2, sticky="w", padx=8, pady=4)
        ttk.Spinbox(bleepf, from_=0.1, to=1.0, increment=0.05, textvariable=self.bleep_gain_var, width=8).grid(row=0, column=3, sticky="w", padx=8, pady=4)
        ttk.Label(bleepf, text="Vorlauf (ms)").grid(row=0, column=4, sticky="w", padx=8, pady=4)
        ttk.Spinbox(bleepf, from_=0, to=3000, increment=10, textvariable=self.bleep_pre_ms_var, width=8).grid(row=0, column=5, sticky="w", padx=8, pady=4)
        ttk.Label(bleepf, text="Nachlauf (ms)").grid(row=0, column=6, sticky="w", padx=8, pady=4)
        ttk.Spinbox(bleepf, from_=0, to=4000, increment=10, textvariable=self.bleep_post_ms_var, width=8).grid(row=0, column=7, sticky="w", padx=8, pady=4)

        runf = ttk.LabelFrame(self, text="Rendern")
        runf.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(runf, text="FFmpeg-Befehl prüfen", command=self.preview_command, style="Accent.TButton").pack(side="left", padx=8, pady=8)
        ttk.Button(runf, text="Gebleeptes Video erzeugen", command=self.run_render_video, style="Accent.TButton").pack(side="left", padx=8, pady=8)
        ttk.Button(runf, text="Gebleeptes Audio erzeugen", command=self.run_render_audio, style="Accent.TButton").pack(side="left", padx=8, pady=8)

        self.log_box = tk.Text(self, height=14, wrap="word")
        self.log_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        for var in (self.video_codec_display, self.audio_codec_display, self.audio_bitrate_var, self.scale_display, self.preset_display, self.mode_var):
            var.trace_add("write", lambda *_: self._update_estimates())
        self.crf_var.trace_add("write", lambda *_: self._update_estimates())
        self.faststart_var.trace_add("write", lambda *_: self._update_estimates())
        self.refresh(); self.apply_profile()

    def save_custom_profile(self):
        name = simpledialog.askstring("Profil speichern", "Name für das Exportprofil:", parent=self.winfo_toplevel())
        if not name or not name.strip():
            return
        data = self._load_saved_profiles()
        data[name.strip()] = {
            "video_codec_display": self.video_codec_display.get(),
            "audio_codec_display": self.audio_codec_display.get(),
            "preset_display": self.preset_display.get(),
            "quality": int(self.crf_var.get()),
            "audio_bitrate": self.audio_bitrate_var.get(),
            "scale_display": self.scale_display.get(),
            "faststart": bool(self.faststart_var.get()),
            "bleep_freq": int(self.bleep_freq_var.get()),
            "bleep_gain": float(self.bleep_gain_var.get()),
            "bleep_pre_ms": int(self.bleep_pre_ms_var.get()),
            "bleep_post_ms": int(self.bleep_post_ms_var.get()),
        }
        self._save_saved_profiles(data)
        self._refresh_profile_list(); self.profile_name_var.set(name.strip())
        self._set_status(f"Exportprofil gespeichert: {name.strip()}")

    def load_custom_profile(self):
        name = self.profile_name_var.get().strip()
        if not name:
            return
        data = self._load_saved_profiles().get(name)
        if not data:
            return
        self.video_codec_display.set(data.get("video_codec_display", self.video_codec_display.get()))
        self.audio_codec_display.set(data.get("audio_codec_display", self.audio_codec_display.get()))
        self.preset_display.set(data.get("preset_display", self.preset_display.get()))
        self.crf_var.set(data.get("quality", self.crf_var.get()))
        self.audio_bitrate_var.set(data.get("audio_bitrate", self.audio_bitrate_var.get()))
        self.scale_display.set(data.get("scale_display", self.scale_display.get()))
        self.faststart_var.set(data.get("faststart", self.faststart_var.get()))
        self.bleep_freq_var.set(data.get("bleep_freq", self.bleep_freq_var.get()))
        self.bleep_gain_var.set(data.get("bleep_gain", self.bleep_gain_var.get()))
        self.bleep_pre_ms_var.set(data.get("bleep_pre_ms", self.bleep_pre_ms_var.get()))
        self.bleep_post_ms_var.set(data.get("bleep_post_ms", self.bleep_post_ms_var.get()))
        self._update_estimates(); self._set_status(f"Exportprofil geladen: {name}")

    def _on_media_changed(self):
        self._refresh_media_info()
        if self.media_var.get():
            stem = Path(self.media_var.get()).stem
            media_path = self._media_path()
            if media_path and media_path.suffix.lower() in {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg"}:
                self.output_name_var.set(f"{stem}_bleeped.mp3")
            else:
                self.output_name_var.set(f"{stem}_bleeped_web.mp4")
        self.refresh()

    def set_web_defaults(self):
        self.mode_var.set("web")
        self.apply_profile()

    def apply_profile(self):
        mode = self.mode_var.get()
        backend = self._settings().get("render_backend", "auto")
        gpu_ok = shutil.which("nvidia-smi") is not None
        prefer_gpu = backend == "gpu" or (backend == "auto" and gpu_ok)
        if mode == "web":
            self.video_codec_display.set("H.264 (GPU / NVIDIA, schnell)" if prefer_gpu else "H.264 (CPU, sehr kompatibel)")
            self.audio_codec_display.set("AAC (für MP4/Video empfohlen)")
            self.crf_var.set(30); self.audio_bitrate_var.set("96k"); self.scale_display.set("1280 px Breite (kleiner für Web)"); self.preset_display.set("medium"); self.faststart_var.set(True)
        elif mode == "qualität":
            self.video_codec_display.set("H.264 (GPU / NVIDIA, schnell)" if prefer_gpu else "H.264 (CPU, sehr kompatibel)")
            self.audio_codec_display.set("AAC (für MP4/Video empfohlen)")
            self.crf_var.set(23); self.audio_bitrate_var.set("160k"); self.scale_display.set("Originalgröße beibehalten"); self.preset_display.set("slow"); self.faststart_var.set(True)
        elif mode == "kleinste datei":
            self.video_codec_display.set("H.265 (CPU, kleinere Dateien)" if backend == "cpu" else "H.264 (GPU / NVIDIA, schnell)" if prefer_gpu else "H.264 (CPU, sehr kompatibel)")
            self.audio_codec_display.set("AAC (für MP4/Video empfohlen)")
            self.crf_var.set(33); self.audio_bitrate_var.set("64k"); self.scale_display.set("1280 px Breite (kleiner für Web)"); self.preset_display.set("medium"); self.faststart_var.set(True)
        elif mode == "wie quellvideo":
            info = self.media_info or {}
            self.video_codec_display.set("H.264 (GPU / NVIDIA, schnell)" if prefer_gpu else "H.264 (CPU, sehr kompatibel)")
            self.audio_codec_display.set("AAC (für MP4/Video empfohlen)")
            self.audio_bitrate_var.set("128k"); self.scale_display.set("Originalgröße beibehalten"); self.preset_display.set("medium"); self.faststart_var.set(True)
            src_h = info.get("height", 0)
            self.crf_var.set(24 if src_h >= 720 and src_h < 1080 else 23 if src_h >= 1080 else 26)
        self._update_estimates(); self._set_status(f"Profil angewendet: {mode}")

    def choose_times(self):
        p = self._project()
        if not p:
            return
        path = filedialog.askopenfilename(title="Times-Datei auswählen", initialdir=str(p.times_dir), filetypes=[("Textdateien", "*.txt")])
        if path:
            self.times_var.set(Path(path).name)

    def _estimate_video_bitrate_kbps(self):
        info = self.media_info or {}
        width = info.get("width", 1280) or 1280
        scale = SCALE_OPTIONS.get(self.scale_display.get(), "1280:-2")
        target_width = 1280 if scale == "1280:-2" else 1920 if scale == "1920:-2" else width
        base = 600 if target_width <= 854 else 1200 if target_width <= 1280 else 2600 if target_width <= 1920 else 4200
        q = int(self.crf_var.get())
        base *= 2 ** ((28 - q) / 6.0)
        if self._effective_video_codec() == "libx265":
            base *= 0.72
        src_br = info.get("bit_rate", 0)
        if self.mode_var.get() == "wie quellvideo" and src_br:
            base = max(500.0, src_br / 1000.0 * 0.9)
        return max(250.0, base)

    def _estimate_output_size_mb(self):
        info = self.media_info or {}
        duration = info.get("duration", 0.0)
        if not duration:
            return None
        audio_kbps = _safe_float((self.audio_bitrate_var.get() or "96").replace("k", ""))
        if not info.get("has_video"):
            return (audio_kbps * 1000.0 / 8.0) * duration / (1024.0 * 1024.0)
        video_kbps = self._estimate_video_bitrate_kbps()
        return ((video_kbps + audio_kbps + 24.0) * 1000.0 / 8.0) * duration / (1024.0 * 1024.0)

    def _estimate_render_seconds(self):
        info = self.media_info or {}
        duration = info.get("duration", 0.0)
        if not duration:
            return None
        if not info.get("has_video"):
            return duration * 0.06
        codec = self._effective_video_codec()
        base_factor = {"ultrafast": 0.12, "superfast": 0.14, "veryfast": 0.18, "fast": 0.22, "medium": 0.28, "slow": 0.35, "veryslow": 0.45}.get(self.preset_display.get(), 0.28) if codec == "h264_nvenc" else {"ultrafast": 0.35, "superfast": 0.45, "veryfast": 0.65, "fast": 1.0, "medium": 1.35, "slow": 2.0, "veryslow": 2.6}.get(self.preset_display.get(), 1.35)
        width = info.get("width", 1280) or 1280
        scale = SCALE_OPTIONS.get(self.scale_display.get(), "1280:-2")
        scale_factor = 0.85 if scale == "1280:-2" and width > 1280 else 1.15 if scale == "1920:-2" and width <= 1280 else 1.0
        return duration * (base_factor * scale_factor + 0.08)

    def _update_estimates(self):
        size_mb = self._estimate_output_size_mb()
        self.estimate_size_var.set("Voraussichtliche Ausgabegröße: -" if size_mb is None else f"Voraussichtliche Ausgabegröße: ca. {size_mb:.1f} MB (Ausgangsmedium: {_fmt_mb((self.media_info or {}).get('size_bytes',0))})")
        sec = self._estimate_render_seconds()
        if sec is None:
            self.estimate_time_var.set("Voraussichtliche Renderdauer: -")
        else:
            cpu_count = os.cpu_count() or 0
            gpu_text = "GPU erkannt" if shutil.which("nvidia-smi") else "keine GPU-Erkennung"
            self.estimate_time_var.set(f"Voraussichtliche Renderdauer: grob {_fmt_mmss(sec)} (System: {cpu_count} Threads, {gpu_text}, zweistufiger Export)")

    def _get_paths(self):
        p = self._project()
        if not p:
            raise RuntimeError("Kein Projekt geladen.")
        media = self._media_path()
        if not media:
            raise RuntimeError("Keine Mediadatei gewählt.")
        if not self.times_var.get():
            raise RuntimeError("Keine Times-Datei gewählt.")
        return p, media, p.times_dir / self.times_var.get(), self.output_name_var.get().strip()

    def _audio_filter_from_times(self, times_path: Path):
        times = _read_lines(times_path)
        if not times:
            raise RuntimeError("Die Times-Datei ist leer.")
        freq = int(self.bleep_freq_var.get())
        gain = float(self.bleep_gain_var.get())
        pre = int(self.bleep_pre_ms_var.get()) / 1000.0
        post = int(self.bleep_post_ms_var.get()) / 1000.0
        parsed = []
        for i, ts in enumerate(times):
            parts = ts.split(":")
            if len(parts) != 3:
                continue
            h = int(parts[0]); mm = int(parts[1]); sec = float(parts[2])
            center = h * 3600 + mm * 60 + sec
            start = max(0.0, center - pre)
            end = center + post
            dur = max(0.08, end - start if end > start else 0.35)
            parsed.append((i, start, end, dur))
        if not parsed:
            raise RuntimeError("Es konnten keine gültigen Zeitpunkte gelesen werden.")
        items = ["[0:a]anull[src0]"]
        current = "src0"
        for idx, start, end, dur in parsed:
            nxt = f"src{idx+1}"
            items.append(f"[{current}]volume=enable='between(t,{start:.3f},{end:.3f})':volume=0[{nxt}]")
            current = nxt
        items.append(f"[{current}]anull[muted]")
        for idx, start, end, dur in parsed:
            items.append(f"sine=f={freq}:sample_rate=48000:d={dur:.3f},volume={gain},adelay={int(start*1000)}:all=1[b{idx}]")
        amix_inputs = "[muted]" + "".join(f"[b{idx}]" for idx, *_ in parsed)
        items.append(f"{amix_inputs}amix=inputs={1+len(parsed)}:normalize=0[aout]")
        return ";".join(items), len(parsed)

    def preview_command(self):
        try:
            ffmpeg = self._ffmpeg()
            if not ffmpeg:
                raise RuntimeError("FFmpeg wurde nicht gefunden.")
            p, media, times, output_name = self._get_paths()
            is_audio = media.suffix.lower() in {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg"} or not self.media_info.get("has_video", True)
            audio_filter, count = self._audio_filter_from_times(times)
            if is_audio:
                out_dir = self._output_audio_dir(p)
                ext = ".mp3" if AUDIO_CODEC_OPTIONS.get(self.audio_codec_display.get(), "aac") == "mp3" else ".m4a"
                out = out_dir / (Path(output_name or media.stem).stem + ext)
                cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(media), "-filter_complex", audio_filter, "-map", "[aout]"]
                cmd += ["-c:a", "libmp3lame", "-b:a", self.audio_bitrate_var.get()] if AUDIO_CODEC_OPTIONS.get(self.audio_codec_display.get(), "aac") == "mp3" else ["-c:a", "aac", "-b:a", self.audio_bitrate_var.get()]
                cmd += [str(out)]
                self._set_status(f"Audioexport vorbereitet. Bleeps: {count}\n\n{' '.join(cmd[:24])} ... {out}")
                return
            out_dir = self._output_video_dir(p)
            out = out_dir / ((output_name or f'{media.stem}_bleeped_web').removesuffix('.mp4') + '.mp4')
            temp_audio = out_dir / (out.stem + ".tmp_bleep.wav")
            cmd1 = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(media), "-filter_complex", audio_filter, "-map", "[aout]", "-c:a", "pcm_s16le", str(temp_audio)]
            cmd2 = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(media), "-i", str(temp_audio), "-map", "0:v:0", "-map", "1:a:0"]
            scale = SCALE_OPTIONS.get(self.scale_display.get(), "1280:-2")
            if scale != "iw:-2":
                cmd2 += ["-vf", f"scale={scale}"]
            codec = self._effective_video_codec(); preset = self._effective_preset()
            cmd2 += ["-c:v", codec, "-preset", preset]
            cmd2 += (["-cq", str(self.crf_var.get())] if codec == "h264_nvenc" else ["-crf", str(self.crf_var.get())])
            cmd2 += ["-c:a", "aac", "-b:a", self.audio_bitrate_var.get()]
            if self.faststart_var.get(): cmd2 += ["-movflags", "+faststart"]
            cmd2 += [str(out)]
            self._set_status(f"Zweistufiger Export vorbereitet. Bleeps: {count}\n\nSchritt 1: {' '.join(cmd1[:18])} ... {temp_audio}\n\nSchritt 2: {' '.join(cmd2[:22])} ... {out}")
        except Exception as e:
            self._set_status(f"Vorschau fehlgeschlagen: {e}")

    def _show_progress_window(self):
        if self.progress_win is not None:
            return
        win = tk.Toplevel(self); win.title("Bleepling rendert"); win.transient(self.winfo_toplevel())
        try: win.attributes("-topmost", True)
        except Exception: pass
        win.resizable(False, False)
        frame = ttk.Frame(win, padding=18); frame.pack(fill="both", expand=True)
        bird_path = self._asset("vogel2_light_512_fixed.png")
        if Image is not None and ImageTk is not None and bird_path.exists():
            img = Image.open(bird_path).resize((180, 180)); self.progress_img = ImageTk.PhotoImage(img); ttk.Label(frame, image=self.progress_img).pack(pady=(0, 10))
        else:
            ttk.Label(frame, text="🐤", font=("Segoe UI Emoji", 36)).pack(pady=(0, 10))
        ttk.Label(frame, text="Bleepling rendert gerade… bitte warten", justify="center").pack(pady=(0, 10))
        self.progress_var.set(0.0); self.progress_text_var.set("0 %")
        ttk.Progressbar(frame, variable=self.progress_var, maximum=100, length=360, mode="determinate").pack(pady=(0, 6))
        ttk.Label(frame, textvariable=self.progress_text_var).pack()
        ttk.Button(frame, text="Rendern abbrechen", command=self.cancel_render, style="Accent.TButton").pack(pady=(12, 0))
        win.update_idletasks(); root = self.winfo_toplevel(); rx, ry, rw, rh = root.winfo_rootx(), root.winfo_rooty(), root.winfo_width(), root.winfo_height(); ww, wh = win.winfo_width(), win.winfo_height(); win.geometry(f"+{rx + max(0, (rw-ww)//2)}+{ry + max(0, (rh-wh)//2)}")
        self.progress_win = win
        try: self.app.set_running(True)
        except Exception: pass

    def _hide_progress_window(self):
        try:
            if self.progress_win is not None:
                self.progress_win.destroy()
        except Exception:
            pass
        self.progress_win = None
        try: self.app.set_running(False)
        except Exception: pass

    def cancel_render(self):
        try:
            if self.proc and self.proc.poll() is None:
                self.proc.terminate(); self._set_status("Renderprozess wurde abgebrochen.")
        except Exception:
            pass

    def _poll_render_queue(self):
        try:
            while True:
                item = self.render_queue.get_nowait(); kind = item.get("kind")
                if kind == "progress":
                    pct = max(0.0, min(100.0, item.get("percent", 0.0))); self.progress_var.set(pct); self.progress_text_var.set(item.get("label", f"{pct:.1f} %")); self.update_idletasks()
                elif kind == "done":
                    self._hide_progress_window(); self._set_status(item.get("message", "Rendern abgeschlossen.")); return
                elif kind == "error":
                    self._hide_progress_window(); self._set_status(item.get("message", "Rendern fehlgeschlagen.")); return
        except queue.Empty:
            pass
        if self.progress_win is not None: self.after(150, self._poll_render_queue)

    def _run_simple_cmd(self, cmd):
        return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")

    def _run_video_progress_cmd(self, cmd, duration, stage_name):
        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
        stderr_parts = []; percent = 0.0; size_text = "-"; speed_text = "-"
        if self.proc.stdout is not None:
            for raw_line in self.proc.stdout:
                line = (raw_line or "").strip()
                if not line: continue
                if line.startswith("out_time_ms="):
                    out_time_sec = _safe_float(line.split("=",1)[1],0.0)/1_000_000.0
                    if duration: percent=max(percent,min(100.0,(out_time_sec/duration)*100.0)); self.render_queue.put({"kind":"progress","percent":percent,"label":f"{stage_name} | {percent:.1f} % | Medienzeit {_fmt_mmss(out_time_sec)} | Größe {size_text} | Speed {speed_text}"})
                elif line.startswith("out_time_us="):
                    out_time_sec = _safe_float(line.split("=",1)[1],0.0)/1_000_000.0
                    if duration: percent=max(percent,min(100.0,(out_time_sec/duration)*100.0)); self.render_queue.put({"kind":"progress","percent":percent,"label":f"{stage_name} | {percent:.1f} % | Medienzeit {_fmt_mmss(out_time_sec)} | Größe {size_text} | Speed {speed_text}"})
                elif line.startswith("total_size="):
                    size_text = _fmt_mb(_safe_int(line.split("=",1)[1],0)); self.render_queue.put({"kind":"progress","percent":percent,"label":f"{stage_name} | {percent:.1f} % | Größe {size_text} | Speed {speed_text}"})
                elif line.startswith("speed="):
                    speed_text = line.split("=",1)[1].strip() or "-"; self.render_queue.put({"kind":"progress","percent":percent,"label":f"{stage_name} | {percent:.1f} % | Größe {size_text} | Speed {speed_text}"})
                elif line.startswith("progress=end"):
                    self.render_queue.put({"kind":"progress","percent":100.0,"label":f"{stage_name} | 100.0 % | Größe {size_text} | Speed {speed_text}"})
        if self.proc.stderr is not None: stderr_parts.append(self.proc.stderr.read())
        rc = self.proc.wait(); self.proc = None
        return rc, "\n".join(stderr_parts).strip()

    def _render_worker_video(self, media, times, out):
        try:
            ffmpeg = self._ffmpeg(); out_dir = out.parent; out_dir.mkdir(parents=True, exist_ok=True)
            audio_filter, count = self._audio_filter_from_times(times); temp_audio = out_dir / (out.stem + ".tmp_bleep.wav")
            self.render_queue.put({"kind":"progress","percent":2.0,"label":f"Schritt 1/2: Audio wird gebleept ({count} Bleep(s))"})
            cmd1 = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(media), "-filter_complex", audio_filter, "-map", "[aout]", "-c:a", "pcm_s16le", str(temp_audio)]
            res1 = self._run_simple_cmd(cmd1)
            if res1.returncode != 0: raise RuntimeError((res1.stderr or res1.stdout or "Fehler in Schritt 1")[:5000])
            self.render_queue.put({"kind":"progress","percent":15.0,"label":f"Schritt 1/2 abgeschlossen | {_fmt_mb(temp_audio.stat().st_size if temp_audio.exists() else 0)}"})
            duration = (self.media_info or {}).get("duration",0.0)
            cmd2 = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-progress", "pipe:1", "-nostats", "-i", str(media), "-i", str(temp_audio), "-map", "0:v:0", "-map", "1:a:0"]
            scale = SCALE_OPTIONS.get(self.scale_display.get(), "1280:-2")
            if scale != "iw:-2": cmd2 += ["-vf", f"scale={scale}"]
            codec = self._effective_video_codec(); preset = self._effective_preset(); cmd2 += ["-c:v", codec, "-preset", preset]; cmd2 += (["-cq", str(self.crf_var.get())] if codec == "h264_nvenc" else ["-crf", str(self.crf_var.get())]); cmd2 += ["-c:a", "aac", "-b:a", self.audio_bitrate_var.get()]
            if self.faststart_var.get(): cmd2 += ["-movflags", "+faststart"]
            cmd2 += [str(out)]
            rc2, err2 = self._run_video_progress_cmd(cmd2, duration, "Schritt 2/2: Video wird mit fertiger Audiospur erzeugt")
            if rc2 != 0: raise RuntimeError((err2 or "Fehler in Schritt 2")[:5000])
            try:
                if temp_audio.exists(): temp_audio.unlink()
            except Exception: pass
            self.render_queue.put({"kind":"done","message":f"Gebleeptes Video erzeugt: {out.name}\nAusgabeordner: {out_dir}"})
        except Exception as e:
            self.proc = None; self.render_queue.put({"kind":"error","message":f"Rendern fehlgeschlagen: {e}"})

    def _render_worker_audio(self, media, times, out):
        try:
            ffmpeg = self._ffmpeg(); out.parent.mkdir(parents=True, exist_ok=True)
            audio_filter, count = self._audio_filter_from_times(times)
            self.render_queue.put({"kind":"progress","percent":5.0,"label":f"Audio wird gebleept ({count} Bleep(s))"})
            cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(media), "-filter_complex", audio_filter, "-map", "[aout]"]
            if AUDIO_CODEC_OPTIONS.get(self.audio_codec_display.get(), "aac") == "mp3": cmd += ["-c:a", "libmp3lame", "-b:a", self.audio_bitrate_var.get()]
            else: cmd += ["-c:a", "aac", "-b:a", self.audio_bitrate_var.get()]
            cmd += [str(out)]
            res = self._run_simple_cmd(cmd)
            if res.returncode != 0: raise RuntimeError((res.stderr or res.stdout or "Fehler beim Audioexport")[:5000])
            self.render_queue.put({"kind":"done","message":f"Gebleeptes Audio erzeugt: {out.name}\nAusgabeordner: {out.parent}"})
        except Exception as e:
            self.proc = None; self.render_queue.put({"kind":"error","message":f"Audioexport fehlgeschlagen: {e}"})

    def run_render_video(self):
        try:
            p, media, times, output_name = self._get_paths()
            if media.suffix.lower() in {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg"} or not self.media_info.get("has_video", True):
                self._set_status("Für reine Audiodateien bitte 'Gebleeptes Audio erzeugen' verwenden.")
                return
            out = self._output_video_dir(p) / ((output_name or f"{media.stem}_bleeped_web").removesuffix(".mp4") + ".mp4")
            self._show_progress_window(); self.progress_text_var.set("Export wird vorbereitet …")
            threading.Thread(target=self._render_worker_video, args=(media, times, out), daemon=True).start(); self.after(150, self._poll_render_queue)
        except Exception as e:
            self._hide_progress_window(); self._set_status(f"Rendern fehlgeschlagen: {e}")

    def run_render_audio(self):
        try:
            p, media, times, output_name = self._get_paths()
            ext = ".mp3" if AUDIO_CODEC_OPTIONS.get(self.audio_codec_display.get(), "aac") == "mp3" else ".m4a"
            out = self._output_audio_dir(p) / (Path(output_name or f"{media.stem}_bleeped").stem + ext)
            self._show_progress_window(); self.progress_text_var.set("Audioexport wird vorbereitet …")
            threading.Thread(target=self._render_worker_audio, args=(media, times, out), daemon=True).start(); self.after(150, self._poll_render_queue)
        except Exception as e:
            self._hide_progress_window(); self._set_status(f"Audioexport fehlgeschlagen: {e}")

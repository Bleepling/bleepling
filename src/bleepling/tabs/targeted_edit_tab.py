
from __future__ import annotations
import os
import re
import shutil
import subprocess
import threading
import queue
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from bleepling.services.render_service import (
    build_bleep_audio_filter,
    find_ffmpeg,
    find_ffprobe,
    parse_progress_line,
    run_simple_command,
)
from bleepling.services.time_service import parse_times_line

try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None


VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".m4v", ".wmv"}


def _list_files(directory: Path, exts: set[str]):
    if not directory.exists():
        return []
    return sorted(
        [p.name for p in directory.iterdir() if p.is_file() and p.suffix.lower() in exts],
        key=str.lower,
    )


def _read_lines(text: str):
    return [x.strip() for x in text.splitlines() if x.strip()]


def _safe_float(value, default=0.0):
    try:
        if isinstance(value, str):
            value = value.strip().replace(",", ".")
        return float(value)
    except Exception:
        return default


def _fmt_mmss(seconds):
    try:
        total = int(round(float(seconds)))
    except Exception:
        return "-"
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


class TargetedEditTab(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.proc = None
        self.progress_win = None
        self.progress_img = None
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_text_var = tk.StringVar(value="")
        self.render_queue = queue.Queue()
        self.last_output_file: Path | None = None

        self.media_var = tk.StringVar()
        self.pre_image_var = tk.StringVar()
        self.post_image_var = tk.StringVar()
        self.pre_seconds_var = tk.StringVar(value="3.0")
        self.post_seconds_var = tk.StringVar(value="3.0")
        self.pre_ms_var = tk.IntVar(value=600)
        self.post_ms_var = tk.IntVar(value=1000)

        self._build()

    def _asset(self, name: str) -> Path:
        return Path(__file__).resolve().parents[3] / "assets" / name

    def _ffmpeg(self):
        return find_ffmpeg()

    def _ffprobe(self):
        return find_ffprobe()

    def _project(self):
        return getattr(self.app, "project", None)

    def _output_video_dir(self, p) -> Path:
        return getattr(p, "output_video_dir", p.root_path / "04_output" / "videos")

    def _titlecards_dir(self, p) -> Path:
        path = getattr(p, "titlecards_output_dir", p.root_path / "04_output" / "titlecards")
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _current_output_file(self) -> Path | None:
        media = self._media_path()
        if self.last_output_file and self.last_output_file.exists() and media is not None:
            if self.last_output_file.name.lower().startswith(f"{media.stem}_edited".lower()):
                return self.last_output_file
        project = self._project()
        if not project or media is None:
            return None
        return self._find_existing_output_file(project, media.stem)

    def _find_vlc(self) -> str | None:
        candidates = [
            shutil.which("vlc"),
            shutil.which("vlc.exe"),
            r"C:\Program Files\VideoLAN\VLC\vlc.exe",
            r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
        ]
        for candidate in candidates:
            if candidate and Path(candidate).exists():
                return str(candidate)
        return None

    def _set_status(self, msg: str):
        if hasattr(self.app, "set_status"):
            try:
                short_msg = (msg or "").splitlines()[0].strip() or "Bereit."
                self.app.set_status(short_msg)
            except Exception:
                pass
        try:
            self.log_box.delete("1.0", "end")
            self.log_box.insert("1.0", msg)
        except Exception:
            pass

    def _find_existing_output_file(self, project, media_stem: str) -> Path | None:
        out_dir = self._output_video_dir(project)
        if not out_dir.exists():
            return None
        pattern = re.compile(rf"^{re.escape(media_stem)}_edited(?:-(\d{{2}}))?\.mp4$", re.IGNORECASE)
        matches: list[tuple[int, Path]] = []
        for path in out_dir.iterdir():
            if not path.is_file():
                continue
            match = pattern.match(path.name)
            if not match:
                continue
            suffix = match.group(1)
            rank = int(suffix) if suffix else 0
            matches.append((rank, path))
        if not matches:
            return None
        matches.sort(key=lambda item: item[0])
        return matches[-1][1]

    def _build_output_file(self, project, media_stem: str) -> Path:
        out_dir = self._output_video_dir(project)
        out_dir.mkdir(parents=True, exist_ok=True)
        base = out_dir / f"{media_stem}_edited.mp4"
        if not base.exists():
            return base
        counter = 1
        while True:
            candidate = out_dir / f"{media_stem}_edited-{counter:02d}.mp4"
            if not candidate.exists():
                return candidate
            counter += 1

    def _probe_media(self, media_path: Path) -> dict:
        ffprobe = self._ffprobe()
        if not ffprobe or not media_path.exists():
            return {}
        try:
            cmd = [
                ffprobe, "-v", "error",
                "-show_entries", "stream=width,height,codec_type:format=duration",
                "-of", "default=noprint_wrappers=1:nokey=0",
                str(media_path),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding="utf-8", errors="replace")
            data = {}
            for line in result.stdout.splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    data.setdefault(k, []).append(v)
            widths = data.get("width", ["0"])
            heights = data.get("height", ["0"])
            duration = _safe_float((data.get("duration") or ["0"])[0], 0.0)
            return {
                "width": int(widths[0]),
                "height": int(heights[0]),
                "duration": duration,
            }
        except Exception:
            return {}

    def _available_video_paths(self):
        p = self._project()
        if not p:
            return {}
        files = {}
        for name in _list_files(p.input_video_dir, VIDEO_EXTS):
            files[name] = p.input_video_dir / name
        out_dir = self._output_video_dir(p)
        for name in _list_files(out_dir, VIDEO_EXTS):
            if ".tmp_" in name:
                continue
            files[name] = out_dir / name
        return files

    def _media_path(self) -> Path | None:
        return self._available_video_paths().get(self.media_var.get())

    def refresh(self):
        files = self._available_video_paths()
        self.media_combo["values"] = list(files.keys())
        if files and (not self.media_var.get() or self.media_var.get() not in files):
            self.media_var.set(next(iter(files.keys())))
        self._refresh_hint()

    def _refresh_hint(self):
        media = self._media_path()
        if not media:
            self.image_hint_var.set("Idealgröße für Vor- und Nachspannbild: -")
            return
        info = self._probe_media(media)
        if info.get("width") and info.get("height"):
            self.image_hint_var.set(f"Idealgröße für Vor- und Nachspannbild: {info['width']} x {info['height']} Pixel")
        else:
            self.image_hint_var.set("Idealgröße für Vor- und Nachspannbild: konnte nicht gelesen werden")

    def _pick_pre_image(self):
        project = self._project()
        initialdir = None
        current = self.pre_image_var.get().strip()
        if current:
            current_path = Path(current)
            if current_path.exists():
                initialdir = str(current_path.parent)
        if initialdir is None and project:
            initialdir = str(self._titlecards_dir(project))
        path = filedialog.askopenfilename(
            title="Bild für Vorspann auswählen",
            initialdir=initialdir,
            filetypes=[("Bilddateien", "*.png;*.jpg;*.jpeg;*.webp;*.bmp")],
        )
        if path:
            self.pre_image_var.set(path)

    def _pick_post_image(self):
        project = self._project()
        initialdir = None
        current = self.post_image_var.get().strip()
        if current:
            current_path = Path(current)
            if current_path.exists():
                initialdir = str(current_path.parent)
        if initialdir is None and project:
            initialdir = str(self._titlecards_dir(project))
        path = filedialog.askopenfilename(
            title="Bild für Nachspann auswählen",
            initialdir=initialdir,
            filetypes=[("Bilddateien", "*.png;*.jpg;*.jpeg;*.webp;*.bmp")],
        )
        if path:
            self.post_image_var.set(path)

    def _get_segment_seconds(self, value, label: str) -> float:
        text = str(value).strip()
        seconds = _safe_float(text, -1.0)
        if seconds <= 0.0:
            raise RuntimeError(f"Bitte bei {label} eine gueltige Dauer in Sekunden eingeben, z. B. 8.5 oder 8,5.")
        return seconds

    def _open_output_dir(self):
        project = self._project()
        if not project:
            messagebox.showerror("Gezielte Nachbearbeitung", "Kein Projekt geladen.")
            return
        out_dir = self._output_video_dir(project)
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            os.startfile(str(out_dir))
        except Exception as exc:
            messagebox.showerror("Gezielte Nachbearbeitung", f"Output-Ordner konnte nicht geöffnet werden:\n{exc}")

    def _play_output_video(self):
        output_file = self._current_output_file()
        if output_file is None:
            messagebox.showerror("Gezielte Nachbearbeitung", "Bitte zuerst ein Video im Projekt auswählen.")
            return
        if not output_file.exists():
            messagebox.showerror("Gezielte Nachbearbeitung", "Es wurde noch kein gerendertes Ergebnis für dieses Video gefunden.")
            return
        vlc_path = self._find_vlc()
        if not vlc_path:
            messagebox.showerror("Gezielte Nachbearbeitung", "VLC wurde auf diesem Rechner nicht gefunden.")
            return
        try:
            subprocess.Popen([vlc_path, str(output_file)])
        except Exception as exc:
            messagebox.showerror("Gezielte Nachbearbeitung", f"Das Ergebnis konnte nicht mit VLC abgespielt werden:\n{exc}")

    def _on_media_changed(self, *_):
        self.last_output_file = None
        self._refresh_hint()

    def _get_ffmpeg_bleep_settings(self):
        ff = getattr(self.app, "ffmpeg_tab", None)
        if ff is None:
            return {"freq": 1000, "gain": 0.70}
        try:
            freq = int(ff.bleep_freq_var.get())
        except Exception:
            freq = 1000
        try:
            gain = float(ff.bleep_gain_var.get())
        except Exception:
            gain = 0.70
        return {"freq": freq, "gain": gain}

    def _parse_times(self):
        lines = _read_lines(self.times_text.get("1.0", "end"))
        parsed = []
        pre = int(self.pre_ms_var.get()) / 1000.0
        post = int(self.post_ms_var.get()) / 1000.0
        for line in lines:
            parsed_ref = parse_times_line(line)
            if parsed_ref is None:
                continue
            if parsed_ref.kind == "range" and parsed_ref.time_range is not None:
                # Altpfad: Dieser Reiter arbeitet bisher faktisch point-basiert.
                # Echte Intervalle werden hier noch nicht fachlich verarbeitet.
                continue
            if parsed_ref.kind != "point" or parsed_ref.point is None:
                continue
            center = parsed_ref.point.seconds
            start = max(0.0, center - pre)
            end = center + post
            dur = max(0.08, end - start if end > start else 0.35)
            parsed.append((start, end, dur))
        return parsed

    def _build_audio_filter(self, intervals):
        cfg = self._get_ffmpeg_bleep_settings()
        freq = cfg["freq"]
        gain = cfg["gain"]
        return build_bleep_audio_filter(intervals, freq, gain, sample_rate=48000)

    def _show_progress_window(self):
        if self.progress_win is not None:
            return
        win = tk.Toplevel(self)
        win.title("Bleepling rendert")
        win.transient(self.winfo_toplevel())
        try:
            win.attributes("-topmost", True)
        except Exception:
            pass
        win.resizable(False, False)

        frame = ttk.Frame(win, padding=18)
        frame.pack(fill="both", expand=True)

        bird_path = self._asset("vogel2_light_512_fixed.png")
        if Image is not None and ImageTk is not None and bird_path.exists():
            img = Image.open(bird_path).resize((180, 180))
            self.progress_img = ImageTk.PhotoImage(img)
            ttk.Label(frame, image=self.progress_img).pack(pady=(0, 10))
        else:
            ttk.Label(frame, text="🐤", font=("Segoe UI Emoji", 36)).pack(pady=(0, 10))

        ttk.Label(frame, text="Bleepling rendert gerade… bitte warten", justify="center").pack(pady=(0, 10))
        ttk.Progressbar(frame, variable=self.progress_var, maximum=100, length=360, mode="determinate").pack(pady=(0, 6))
        ttk.Label(frame, textvariable=self.progress_text_var).pack()
        ttk.Button(frame, text="Rendern abbrechen", command=self.cancel_render, style="Accent.TButton").pack(pady=(12, 0))

        win.update_idletasks()
        root = self.winfo_toplevel()
        x = root.winfo_rootx() + max(0, (root.winfo_width() - win.winfo_width()) // 2)
        y = root.winfo_rooty() + max(0, (root.winfo_height() - win.winfo_height()) // 2)
        win.geometry(f"+{x}+{y}")

        self.progress_var.set(0.0)
        self.progress_text_var.set("0 %")
        self.progress_win = win
        try:
            self.app.set_running(True)
        except Exception:
            pass

    def _hide_progress_window(self):
        try:
            if self.progress_win is not None:
                self.progress_win.destroy()
        except Exception:
            pass
        self.progress_win = None
        try:
            self.app.set_running(False)
        except Exception:
            pass

    def cancel_render(self):
        try:
            if self.proc and self.proc.poll() is None:
                self.proc.terminate()
                self._set_status("Renderprozess wurde abgebrochen.")
        except Exception:
            pass

    def _poll_render_queue(self):
        try:
            while True:
                item = self.render_queue.get_nowait()
                kind = item.get("kind")
                if kind == "progress":
                    pct = max(0.0, min(100.0, item.get("percent", 0.0)))
                    self.progress_var.set(pct)
                    self.progress_text_var.set(item.get("label", f"{pct:.1f} %"))
                    self.update_idletasks()
                elif kind == "done":
                    self._hide_progress_window()
                    output_file = item.get("output_file")
                    self.last_output_file = Path(output_file) if output_file else None
                    self._set_status(item.get("message", "Rendern abgeschlossen."))
                    return
                elif kind == "error":
                    self._hide_progress_window()
                    self._set_status(item.get("message", "Rendern fehlgeschlagen."))
                    return
        except queue.Empty:
            pass
        if self.progress_win is not None:
            self.after(150, self._poll_render_queue)

    def _run_simple(self, cmd):
        return run_simple_command(cmd)

    def _run_progress_cmd(self, cmd, duration):
        self.proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        err = []
        size_text = "-"
        speed_text = "-"
        percent = 0.0
        if self.proc.stdout is not None:
            for raw in self.proc.stdout:
                line = (raw or "").strip()
                event = parse_progress_line(line)
                if event is None:
                    continue
                event_kind, event_value = event
                if event_kind == "out_time_seconds":
                    out_time = float(event_value)
                    if duration > 0:
                        percent = max(percent, min(100.0, out_time / duration * 100.0))
                    self.render_queue.put({"kind": "progress", "percent": percent, "label": f"{percent:.1f} % | Medienzeit {_fmt_mmss(out_time)} | Größe {size_text} | Speed {speed_text}"})
                elif event_kind == "total_size":
                    try:
                        size_bytes = int(event_value)
                        size_text = f"{size_bytes / (1024*1024):.1f} MB"
                    except Exception:
                        size_text = "-"
                elif event_kind == "speed":
                    speed_text = str(event_value)
                elif event_kind == "progress" and event_value == "end":
                    self.render_queue.put({"kind": "progress", "percent": 100.0, "label": f"100.0 % | Größe {size_text} | Speed {speed_text}"})
        if self.proc.stderr is not None:
            err.append(self.proc.stderr.read())
        rc = self.proc.wait()
        self.proc = None
        return rc, "\n".join(err).strip()

    def _worker(self, media: Path, out_file: Path, prepend: str, append: str, intervals):
        temp_audio = None
        temp_targeted = None
        temp_concat_media = None
        try:
            ffmpeg = self._ffmpeg()
            if not ffmpeg:
                raise RuntimeError("FFmpeg wurde nicht gefunden.")

            info = self._probe_media(media)
            width = info.get("width", 1920) or 1920
            height = info.get("height", 1080) or 1080
            duration = info.get("duration", 0.0)

            out_dir = out_file.parent
            out_dir.mkdir(parents=True, exist_ok=True)

            working_video = media

            if intervals:
                self.render_queue.put({"kind": "progress", "percent": 5.0, "label": "Schritt 1/2: Gezielte Bleeps werden vorbereitet"})
                temp_audio = out_dir / f"{out_file.stem}.tmp_targeted_bleep.wav"
                temp_targeted = out_dir / f"{out_file.stem}.tmp_targeted_video.mp4"
                audio_filter = self._build_audio_filter(intervals)

                cmd_audio = [
                    ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(media),
                    "-filter_complex", audio_filter,
                    "-map", "[aout]",
                    "-c:a", "pcm_s16le",
                    str(temp_audio),
                ]
                res = self._run_simple(cmd_audio)
                if res.returncode != 0:
                    raise RuntimeError((res.stderr or res.stdout or "Fehler bei gezielten Bleeps")[:5000])

                codec = "h264_nvenc" if shutil.which("nvidia-smi") else "libx264"
                cmd_mux = [
                    ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-progress", "pipe:1", "-nostats",
                    "-i", str(media),
                    "-i", str(temp_audio),
                    "-map", "0:v:0",
                    "-map", "1:a:0",
                    "-c:v", codec,
                ]
                if codec == "h264_nvenc":
                    cmd_mux += ["-preset", "p5", "-cq", "30"]
                else:
                    cmd_mux += ["-preset", "medium", "-crf", "30"]
                cmd_mux += ["-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(temp_targeted)]
                rc, err = self._run_progress_cmd(cmd_mux, duration)
                if rc != 0:
                    raise RuntimeError((err or "Fehler beim gezielten Nachbleepen")[:5000])

                working_video = temp_targeted
            have_pre = bool(prepend)
            have_post = bool(append)

            if have_pre or have_post:
                self.render_queue.put({"kind": "progress", "percent": 72.0 if intervals else 8.0, "label": "Schritt 2/2: Vor- und Nachspann werden gemeinsam gerendert"})
                temp_concat_media = out_dir / f"{out_file.stem}.tmp_concat_media.mp4"

                inputs = []
                filter_parts = []
                concat_labels = []
                segment_idx = 0
                input_idx = 0

                pre_seconds = self._get_segment_seconds(self.pre_seconds_var.get(), "Bild voranstellen") if have_pre else 0.0
                post_seconds = self._get_segment_seconds(self.post_seconds_var.get(), "Bild hintenanstellen") if have_post else 0.0

                def add_image_segment(image_path: str, seconds: float):
                    nonlocal segment_idx, input_idx
                    video_input_idx = input_idx
                    inputs.extend(["-loop", "1", "-t", str(seconds), "-i", image_path])
                    input_idx += 1
                    audio_input_idx = video_input_idx + 1
                    inputs.extend(["-f", "lavfi", "-t", str(seconds), "-i", "anullsrc=r=48000:cl=stereo"])
                    input_idx += 1
                    filter_parts.append(
                        f"[{video_input_idx}:v:0]scale={width}:{height}:force_original_aspect_ratio=decrease,"
                        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=25,format=yuv420p[vseg{segment_idx}]"
                    )
                    filter_parts.append(f"[{audio_input_idx}:a:0]aresample=48000,asetpts=PTS-STARTPTS[aseg{segment_idx}]")
                    concat_labels.append(f"[vseg{segment_idx}][aseg{segment_idx}]")
                    segment_idx += 1

                if have_pre:
                    add_image_segment(prepend, pre_seconds)

                video_input_idx = input_idx
                inputs.extend(["-i", str(working_video)])
                input_idx += 1
                filter_parts.append(
                    f"[{video_input_idx}:v:0]scale={width}:{height}:force_original_aspect_ratio=decrease,"
                    f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=25,format=yuv420p[vseg{segment_idx}]"
                )
                filter_parts.append(f"[{video_input_idx}:a:0]aresample=48000,asetpts=PTS-STARTPTS[aseg{segment_idx}]")
                concat_labels.append(f"[vseg{segment_idx}][aseg{segment_idx}]")
                segment_idx += 1

                if have_post:
                    add_image_segment(append, post_seconds)

                filter_parts.append(f"{''.join(concat_labels)}concat=n={segment_idx}:v=1:a=1[vout][aout]")
                filter_complex = ";".join(filter_parts)

                codec = "h264_nvenc" if shutil.which("nvidia-smi") else "libx264"
                cmd_video = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-progress", "pipe:1", "-nostats"] + inputs + [
                    "-filter_complex", filter_complex,
                    "-map", "[vout]",
                    "-map", "[aout]",
                    "-c:v", codec,
                ]
                if codec == "h264_nvenc":
                    cmd_video += ["-preset", "p5", "-cq", "30"]
                else:
                    cmd_video += ["-preset", "medium", "-crf", "30"]
                final_duration = duration + (pre_seconds if have_pre else 0.0) + (post_seconds if have_post else 0.0)
                cmd_video += ["-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(temp_concat_media)]
                rc, err = self._run_progress_cmd(cmd_video, max(final_duration, 1.0))
                if rc != 0:
                    raise RuntimeError((err or "Fehler beim Zusammensetzen von Vor- und Nachspann")[:5000])
                shutil.move(str(temp_concat_media), str(out_file))
            else:
                if intervals:
                    shutil.move(str(working_video), str(out_file))
                else:
                    raise RuntimeError("Es wurden keine Änderungen angegeben.")

            self.render_queue.put({
                "kind": "done",
                "message": f"Änderungen gerendert.\nAusgabedatei: {out_file.name}\nAusgabeordner: {out_dir}",
                "output_file": str(out_file),
            })
        except Exception as e:
            self.proc = None
            self.render_queue.put({"kind": "error", "message": f"Rendern fehlgeschlagen: {e}"})
        finally:
            for temp in (temp_audio, temp_targeted, temp_concat_media):
                try:
                    if temp and temp.exists():
                        temp.unlink()
                except Exception:
                    pass

    def render_changes(self):
        p = self._project()
        media = self._media_path()
        if not p or media is None:
            messagebox.showerror("Gezielte Nachbearbeitung", "Bitte zuerst ein Video auswählen.")
            return

        prepend = self.pre_image_var.get().strip()
        append = self.post_image_var.get().strip()
        intervals = self._parse_times()

        if not intervals and not prepend and not append:
            messagebox.showerror("Gezielte Nachbearbeitung", "Es wurden weder Bleep-Zeiten noch Vor- oder Nachspannbilder angegeben.")
            return

        stem = media.stem
        out_file = self._build_output_file(p, stem)
        self.last_output_file = out_file

        self._show_progress_window()
        self.progress_text_var.set("Änderungen werden vorbereitet …")
        threading.Thread(target=self._worker, args=(media, out_file, prepend, append, intervals), daemon=True).start()
        self.after(150, self._poll_render_queue)

    def _build(self):
        top = ttk.LabelFrame(self, text="Quelle")
        top.pack(fill="x", padx=12, pady=(12, 8))

        ttk.Label(top, text="Video im Projekt").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.media_combo = ttk.Combobox(top, textvariable=self.media_var, width=58, state="readonly")
        self.media_combo.grid(row=0, column=1, sticky="we", padx=8, pady=6)
        self.media_combo.bind("<<ComboboxSelected>>", self._on_media_changed)
        ttk.Button(top, text="Liste aktualisieren", command=self.refresh, style="Accent.TButton").grid(row=0, column=2, sticky="w", padx=8, pady=6)

        self.image_hint_var = tk.StringVar(value="Idealgröße für Vor- und Nachspannbild: -")
        ttk.Label(top, textvariable=self.image_hint_var).grid(row=1, column=0, columnspan=3, sticky="w", padx=8, pady=(0, 8))
        ttk.Label(top, text="Es können sowohl ursprüngliche Eingabevideos als auch bereits gerenderte Projektvideos aus dem Ausgabeordner gewählt werden.", justify="left").grid(row=2, column=0, columnspan=3, sticky="w", padx=8, pady=(0, 8))
        top.grid_columnconfigure(1, weight=1)

        bleepf = ttk.LabelFrame(self, text="1) Gezieltes Nachbleepen")
        bleepf.pack(fill="x", padx=12, pady=(0, 8))

        ttk.Label(
            bleepf,
            text="Bitte pro Zeile einen Zeitpunkt im Format HH:MM:SS.mmm eintragen. Es gelten Bleep-Frequenz und Bleep-Lautstärke aus dem Reiter Video & Audio / FFmpeg. Vor- und Nachlauf können hier separat gesetzt werden.",
            justify="left",
            wraplength=1250,
        ).pack(anchor="w", padx=8, pady=(8, 6))

        self.times_text = tk.Text(bleepf, height=7, wrap="none")
        self.times_text.pack(fill="x", padx=8, pady=(0, 8))

        rowb = ttk.Frame(bleepf)
        rowb.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Label(rowb, text="Vorlauf (ms)").pack(side="left")
        ttk.Spinbox(rowb, from_=0, to=5000, increment=10, textvariable=self.pre_ms_var, width=8).pack(side="left", padx=(8, 20))
        ttk.Label(rowb, text="Nachlauf (ms)").pack(side="left")
        ttk.Spinbox(rowb, from_=0, to=5000, increment=10, textvariable=self.post_ms_var, width=8).pack(side="left", padx=(8, 20))

        pref = ttk.LabelFrame(self, text="2) Bild voranstellen")
        pref.pack(fill="x", padx=12, pady=(0, 8))
        ttk.Label(pref, text="Bilddatei").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(pref, textvariable=self.pre_image_var, width=80).grid(row=0, column=1, sticky="we", padx=8, pady=6)
        ttk.Button(pref, text="Bild auswählen", command=self._pick_pre_image, style="Accent.TButton").grid(row=0, column=2, sticky="w", padx=8, pady=6)
        ttk.Label(pref, text="Dauer in Sekunden").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        ttk.Spinbox(pref, from_=0.5, to=60.0, increment=0.5, textvariable=self.pre_seconds_var, width=8).grid(row=1, column=1, sticky="w", padx=8, pady=6)
        pref.grid_columnconfigure(1, weight=1)

        postf = ttk.LabelFrame(self, text="3) Bild hintenanstellen")
        postf.pack(fill="x", padx=12, pady=(0, 8))
        ttk.Label(postf, text="Bilddatei").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ttk.Entry(postf, textvariable=self.post_image_var, width=80).grid(row=0, column=1, sticky="we", padx=8, pady=6)
        ttk.Button(postf, text="Bild auswählen", command=self._pick_post_image, style="Accent.TButton").grid(row=0, column=2, sticky="w", padx=8, pady=6)
        ttk.Label(postf, text="Dauer in Sekunden").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        ttk.Spinbox(postf, from_=0.5, to=60.0, increment=0.5, textvariable=self.post_seconds_var, width=8).grid(row=1, column=1, sticky="w", padx=8, pady=6)
        postf.grid_columnconfigure(1, weight=1)

        runf = ttk.LabelFrame(self, text="Rendern")
        runf.pack(fill="x", padx=12, pady=(0, 8))
        ttk.Label(
            runf,
            text="Ablauf: Erst wird das gezielte Nachbleepen auf das gewählte Video angewendet. Danach werden Vor- und Nachspannbilder gemeinsam in einem einzigen weiteren Schritt zusammengesetzt. Dadurch bleiben die Bleep-Zeiten korrekt und Vor- und Nachspann werden nicht unnötig zweimal gerendert.",
            justify="left",
            wraplength=1250,
        ).pack(anchor="w", padx=8, pady=(8, 6))
        ttk.Button(runf, text="Änderungen rendern", command=self.render_changes, style="Accent.TButton").pack(anchor="w", padx=8, pady=(0, 8))

        bottom = ttk.Frame(self)
        bottom.pack(fill="x", padx=12, pady=(0, 12))

        self.log_box = tk.Text(bottom, height=5, wrap="word")
        self.log_box.pack(fill="x", pady=(0, 6))

        actions = ttk.Frame(bottom)
        actions.pack(fill="x")
        tk.Button(
            actions,
            text="Ergebnis abspielen",
            command=self._play_output_video,
            bg="#c62828",
            fg="white",
            activebackground="#b71c1c",
            activeforeground="white",
            relief="raised",
            bd=1,
            highlightthickness=1,
            highlightbackground="black",
            highlightcolor="black",
            width=22,
            padx=6,
            pady=4,
        ).pack(side="right")
        ttk.Button(actions, text="Output-Ordner öffnen", command=self._open_output_dir, width=22).pack(side="right", padx=(0, 8))


from __future__ import annotations

import ctypes
import json
import re
import shutil
import subprocess
import threading
import tempfile
from pathlib import Path
import tkinter as tk
from tkinter import ttk

VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".m4v", ".wmv"}
AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}
MEDIA_EXTS = VIDEO_EXTS | AUDIO_EXTS
REVIEWABLE_DECISIONS = {"bleepen", "prüfen", "offen"}
MIN_BLEEP_DURATION = 0.08
SPAN_PAD_MS = 250
MATCH_WINDOW_SECONDS = 6.0
MAX_GAP_BETWEEN_MATCHED_WORDS = 2.2
END_SAFETY_PAD_MS = 50


def _list_files(directory: Path, exts: set[str]):
    if not directory.exists():
        return []
    return sorted([p.name for p in directory.iterdir() if p.is_file() and p.suffix.lower() in exts], key=str.lower)


def _parse_timestamp(value: str) -> float | None:
    text = (value or "").strip().replace(",", ".")
    if not text:
        return None
    try:
        parts = text.split(":")
        if len(parts) != 3:
            return None
        h = int(parts[0])
        m = int(parts[1])
        s = float(parts[2])
        if h < 0 or m < 0 or s < 0:
            return None
        return h * 3600 + m * 60 + s
    except Exception:
        return None


def _format_timestamp(seconds: float) -> str:
    total_ms = max(0, int(round(float(seconds) * 1000)))
    h = total_ms // 3600000
    total_ms %= 3600000
    m = total_ms // 60000
    total_ms %= 60000
    s = total_ms // 1000
    ms = total_ms % 1000
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def _normalize_token(text: str) -> str:
    text = (text or "").strip().lower()
    text = text.replace("ß", "ss")
    text = re.sub(r"[^\wäöüÄÖÜß]+", "", text, flags=re.UNICODE)
    return text


def _tokenize_label(label: str) -> list[str]:
    parts = re.split(r"\s+", (label or "").strip())
    return [tok for tok in (_normalize_token(p) for p in parts) if tok]


class _MciAudioPlayer:
    def __init__(self):
        self._alias = f"bleepling_preview_{id(self):x}"
        self._winmm = getattr(ctypes, "windll", None)
        self._is_open = False
        self._paused = False

    @property
    def available(self) -> bool:
        return self._winmm is not None and hasattr(self._winmm, "winmm")

    def _send(self, command: str) -> str:
        if not self.available:
            raise RuntimeError("Die Audio-Vorschau über Windows MCI ist auf diesem System nicht verfügbar.")
        buffer = ctypes.create_unicode_buffer(512)
        err = self._winmm.winmm.mciSendStringW(command, buffer, len(buffer), 0)
        if err != 0:
            err_buf = ctypes.create_unicode_buffer(512)
            self._winmm.winmm.mciGetErrorStringW(err, err_buf, len(err_buf))
            message = err_buf.value or f"MCI-Fehler {err}"
            raise RuntimeError(message)
        return buffer.value.strip()

    def load(self, path: Path):
        if self._is_open:
            try:
                self.close()
            except Exception:
                pass
        quoted = str(path).replace('"', "")
        try:
            self._send(f'open "{quoted}" type waveaudio alias {self._alias}')
        except RuntimeError as exc:
            message = str(exc).lower()
            if "alias" in message and ("bereits verwendet" in message or "already" in message):
                try:
                    self._send(f"close {self._alias}")
                except Exception:
                    pass
                self._send(f'open "{quoted}" type waveaudio alias {self._alias}')
            else:
                raise
        self._is_open = True
        self._paused = False

    def play(self, from_ms: int | None = None):
        if not self._is_open:
            return
        if self._paused and from_ms is None:
            self._send(f"resume {self._alias}")
        elif from_ms is not None:
            self._send(f"play {self._alias} from {max(0, int(from_ms))}")
        else:
            self._send(f"play {self._alias}")
        self._paused = False

    def pause(self):
        if self._is_open:
            self._send(f"pause {self._alias}")
            self._paused = True

    def stop(self):
        if self._is_open:
            self._send(f"stop {self._alias}")
            self._send(f"seek {self._alias} to start")
            self._paused = False

    def seek(self, position_ms: int, auto_play: bool = False):
        if not self._is_open:
            return
        pos = max(0, int(position_ms))
        self._send(f"seek {self._alias} to {pos}")
        if auto_play:
            self.play(from_ms=pos)

    def get_position_ms(self) -> int:
        if not self._is_open:
            return 0
        try:
            return int(self._send(f"status {self._alias} position") or 0)
        except Exception:
            return 0

    def get_length_ms(self) -> int:
        if not self._is_open:
            return 0
        try:
            return int(self._send(f"status {self._alias} length") or 0)
        except Exception:
            return 0

    def close(self):
        if self._is_open:
            try:
                self._send(f"close {self._alias}")
            finally:
                self._is_open = False
                self._paused = False


class HitReviewTab(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.player = _MciAudioPlayer()
        self.current_media_path: Path | None = None
        self.media_map: dict[str, Path] = {}
        self.source_map: dict[str, Path] = {}
        self.words_map: dict[str, Path] = {}
        self.words_cache: dict[str, list[dict]] = {}
        self.hits: list[dict] = []
        self.active_hit_index: int | None = None
        self._preview_meta: dict[str, float | str] = {}
        self._preview_cache: dict[tuple, Path] = {}
        self._preview_generation_token = 0
        self._position_after_id = None
        self._generation_thread: threading.Thread | None = None
        self._bird_image = None
        self._bird_label = None

        self.media_var = tk.StringVar()
        self.source_var = tk.StringVar()
        self.preview_preroll_var = tk.IntVar(value=3)
        self.preview_postroll_var = tk.IntVar(value=2)
        self.timestamp_var = tk.StringVar(value="00:00:00.000")
        self.filter_var = tk.StringVar(value="offen / prüfen / bleepen")
        self.info_var = tk.StringVar(value="Noch kein Treffer ausgewählt.")
        self.audio_status_var = tk.StringVar(value="Audio-Vorschau bereit.")
        self.bleep_summary_var = tk.StringVar(value="Bleepfenster: -")
        self.position_var = tk.StringVar(value="Position: 00:00:00.000 / 00:00:00.000")
        self.preview_hint_var = tk.StringVar(
            value="Audio-Vorschau: Der Reiter erzeugt einen kurzen Prüfclip rund um den Treffer. "
                  "Maßgeblich ist die erkannte Wortspanne vom ersten bis zum letzten zugehörigen Wort."
        )

        self._build()
        self.after(200, self._poll_position)

    def destroy(self):
        try:
            if self._position_after_id is not None:
                self.after_cancel(self._position_after_id)
        except Exception:
            pass
        try:
            self.player.close()
        except Exception:
            pass
        super().destroy()

    def _project(self):
        return getattr(self.app, "project", None)

    def _set_status(self, msg: str):
        self.audio_status_var.set(msg)
        try:
            self.app.set_status(msg)
        except Exception:
            pass

    def _ffmpeg(self) -> str | None:
        return shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")

    def _preview_dir(self) -> Path:
        p = self._project()
        if not p:
            return Path(tempfile.gettempdir()) / "bleepling_hit_review_preview"
        return p.logs_dir / "hit_review_preview"

    def _get_ffmpeg_bleep_settings(self) -> dict[str, float | int]:
        ff = getattr(self.app, "ffmpeg_tab", None)
        try:
            freq = int(ff.bleep_freq_var.get()) if ff is not None else 1000
        except Exception:
            freq = 1000
        try:
            gain = float(ff.bleep_gain_var.get()) if ff is not None else 0.90
        except Exception:
            gain = 0.90
        return {"freq": freq, "gain": gain}

    def _available_media_paths(self) -> dict[str, Path]:
        p = self._project()
        if not p:
            return {}
        files: dict[str, Path] = {}
        for name in _list_files(p.input_video_dir, MEDIA_EXTS):
            files[name] = p.input_video_dir / name
        for name in _list_files(p.input_audio_dir, MEDIA_EXTS):
            files[name] = p.input_audio_dir / name
        for name in _list_files(getattr(p, "transcription_wav_dir", p.root_path / "02_transcription" / "wav"), MEDIA_EXTS):
            files.setdefault(name, getattr(p, "transcription_wav_dir", p.root_path / "02_transcription" / "wav") / name)
        output_video_dir = getattr(p, "output_video_dir", p.root_path / "04_output" / "videos")
        for name in _list_files(output_video_dir, VIDEO_EXTS):
            files.setdefault(name, output_video_dir / name)
        return files

    def _available_source_paths(self) -> dict[str, Path]:
        p = self._project()
        if not p:
            return {}
        result: dict[str, Path] = {}
        if p.candidates_reviewed_dir.exists():
            for path in sorted(p.candidates_reviewed_dir.glob("*.txt"), key=lambda x: x.name.lower()):
                result[f"reviewed: {path.name}"] = path
        if p.times_dir.exists():
            for path in sorted(p.times_dir.glob("*.times.txt"), key=lambda x: x.name.lower()):
                label = f"times: {path.name}"
                if label not in result:
                    result[label] = path
        return result

    def _available_words_json_paths(self) -> dict[str, Path]:
        p = self._project()
        if not p:
            return {}
        roots = [
            getattr(p, "input_audio_dir", None),
            getattr(p, "times_dir", None),
            getattr(p, "root_path", None),
        ]
        result: dict[str, Path] = {}
        for root in roots:
            if root and Path(root).exists():
                for path in Path(root).rglob("*.words.json"):
                    result[path.name.lower()] = path
        return result

    def _media_stem_variants(self, path_or_name: str) -> set[str]:
        stem = Path(path_or_name).stem.lower()
        variants = {stem}
        for suffix in (".times", "_reviewed", ".quick", ".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".mp4", ".mov", ".mkv", ".avi", ".m4v", ".wmv"):
            if stem.endswith(suffix):
                variants.add(stem[: -len(suffix)])
        return {v for v in variants if v}

    def _guess_matching_source_label(self, media_name: str) -> str | None:
        media_variants = self._media_stem_variants(media_name)
        for label, path in self.source_map.items():
            if media_variants & self._media_stem_variants(path.name):
                return label
        return None

    def _guess_matching_media_name(self, source_label: str) -> str | None:
        source_path = self.source_map.get(source_label)
        if not source_path:
            return None
        source_variants = self._media_stem_variants(source_path.name)
        for name in self.media_map:
            if source_variants & self._media_stem_variants(name):
                return name
        return None

    def _guess_words_json_for_media(self, media_path: Path | None) -> Path | None:
        if media_path is None:
            return None
        media_variants = self._media_stem_variants(media_path.name)
        for path in self.words_map.values():
            json_variants = self._media_stem_variants(path.name)
            if media_variants & json_variants:
                return path
            try:
                data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
                src = str(data.get("source_file", ""))
                if src and (media_variants & self._media_stem_variants(src)):
                    return path
            except Exception:
                continue
        return None

    def _load_words_entries(self, json_path: Path) -> list[dict]:
        cache_key = str(json_path)
        if cache_key in self.words_cache:
            return self.words_cache[cache_key]
        entries: list[dict] = []
        try:
            data = json.loads(json_path.read_text(encoding="utf-8", errors="replace"))
            for segment in data.get("segments", []):
                for w in segment.get("words", []):
                    raw = str(w.get("word", ""))
                    norm = _normalize_token(raw)
                    if not norm:
                        continue
                    entries.append(
                        {
                            "start": float(w.get("start", 0.0)),
                            "end": float(w.get("end", 0.0)),
                            "word": raw,
                            "norm": norm,
                        }
                    )
        except Exception:
            entries = []
        self.words_cache[cache_key] = entries
        return entries

    def _parse_reviewed_file(self, path: Path) -> list[dict]:
        hits: list[dict] = []
        for line_number, raw_line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue
            parts = [part.strip() for part in line.split(" | ", 4)]
            if len(parts) < 3:
                continue
            timestamp = parts[0]
            label = parts[1]
            source_decision = parts[2].strip().lower()
            reason = parts[3] if len(parts) > 3 else ""
            context = parts[4] if len(parts) > 4 else ""
            review_status = source_decision if source_decision in {"bleepen", "prüfen", "ignorieren", "erlaubt"} else "offen"
            hits.append(
                {
                    "timestamp": timestamp,
                    "begin_ts": timestamp,
                    "end_ts": timestamp,
                    "label": label or "(ohne Kandidat)",
                    "source_decision": source_decision or "offen",
                    "review_status": review_status,
                    "reason": reason,
                    "context": context,
                    "line_number": line_number,
                    "adjusted": False,
                    "start_offset_ms": 0,
                    "end_offset_ms": 0,
                    "detected_start": None,
                    "detected_end": None,
                }
            )
        return hits

    def _parse_times_file(self, path: Path) -> list[dict]:
        hits: list[dict] = []
        for line_number, raw_line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            timestamp = raw_line.strip()
            if not timestamp:
                continue
            hits.append(
                {
                    "timestamp": timestamp,
                    "begin_ts": timestamp,
                    "end_ts": timestamp,
                    "label": "(aus Times-Datei)",
                    "source_decision": "bleepen",
                    "review_status": "offen",
                    "reason": "aus Times-Datei geladen",
                    "context": "",
                    "line_number": line_number,
                    "adjusted": False,
                    "start_offset_ms": 0,
                    "end_offset_ms": 0,
                    "detected_start": None,
                    "detected_end": None,
                }
            )
        return hits

    def _resolve_hit_spans(self):
        media_path = self.media_map.get(self.media_var.get())
        words_json = self._guess_words_json_for_media(media_path)
        if not words_json:
            for hit in self.hits:
                hit["begin_ts"] = hit["timestamp"]
                hit["end_ts"] = hit["timestamp"]
                hit["detected_start"] = _parse_timestamp(hit["timestamp"])
                hit["detected_end"] = _parse_timestamp(hit["timestamp"])
            return
        words = self._load_words_entries(words_json)
        for hit in self.hits:
            start, end = self._match_hit_span(hit, words)
            if start is None or end is None:
                ts = _parse_timestamp(hit["timestamp"])
                start = end = ts
            hit["detected_start"] = start
            hit["detected_end"] = end
            if start is not None:
                hit["begin_ts"] = _format_timestamp(start)
                hit["end_ts"] = _format_timestamp(end if end is not None else start)
            else:
                hit["begin_ts"] = hit["timestamp"]
                hit["end_ts"] = hit["timestamp"]

    def _match_hit_span(self, hit: dict, words: list[dict]) -> tuple[float | None, float | None]:
        ts = _parse_timestamp(hit.get("timestamp", ""))
        tokens = _tokenize_label(hit.get("label", ""))
        if ts is None or not tokens or not words:
            return None, None

        candidates = [i for i, w in enumerate(words) if abs(float(w["start"]) - ts) <= MATCH_WINDOW_SECONDS]
        if not candidates:
            return None, None

        best = None
        for i in candidates:
            if words[i]["norm"] != tokens[0]:
                continue
            if len(tokens) == 1:
                score = abs(float(words[i]["start"]) - ts)
                cand = (score, float(words[i]["start"]), float(words[i]["end"]))
                if best is None or cand < best:
                    best = cand
                continue

            idx = i
            matched = [i]
            ok = True
            for token in tokens[1:]:
                found = None
                for j in range(idx + 1, min(len(words), idx + 80)):
                    if float(words[j]["start"]) - float(words[idx]["end"]) > MAX_GAP_BETWEEN_MATCHED_WORDS:
                        break
                    if words[j]["norm"] == token:
                        found = j
                        break
                if found is None:
                    ok = False
                    break
                matched.append(found)
                idx = found
            if not ok:
                continue
            seq_start = float(words[matched[0]]["start"])
            seq_end = float(words[matched[-1]]["end"])
            score = abs(seq_start - ts) + max(0.0, seq_end - seq_start) * 0.02
            cand = (score, seq_start, seq_end)
            if best is None or cand < best:
                best = cand

        if best is None:
            return None, None
        return best[1], best[2]

    def _load_hits_from_selected_source(self):
        self.hit_tree.delete(*self.hit_tree.get_children())
        self.hits = []
        self.active_hit_index = None
        source_path = self.source_map.get(self.source_var.get())
        if not source_path:
            self.info_var.set("Keine Trefferquelle ausgewählt.")
            return
        try:
            if source_path.name.lower().endswith("_reviewed.txt") or source_path.name.lower().endswith(".reviewed.txt"):
                self.hits = self._parse_reviewed_file(source_path)
            elif source_path.name.lower().endswith(".times.txt"):
                self.hits = self._parse_times_file(source_path)
            else:
                self.hits = self._parse_reviewed_file(source_path)
            self._resolve_hit_spans()
        except Exception as exc:
            self._set_status(f"Trefferquelle konnte nicht geladen werden: {exc}")
            self.info_var.set("Trefferquelle konnte nicht geladen werden.")
            return

        filter_mode = self.filter_var.get().strip().lower()
        visible = 0
        for index, hit in enumerate(self.hits):
            status = hit["review_status"]
            if filter_mode == "nur offene" and status not in REVIEWABLE_DECISIONS:
                continue
            self.hit_tree.insert("", "end", iid=str(index), values=(hit["begin_ts"], hit["end_ts"], hit["label"], hit["source_decision"], hit["review_status"]))
            visible += 1

        if self.hit_tree.get_children():
            first = self.hit_tree.get_children()[0]
            self.hit_tree.selection_set(first)
            self._activate_hit(int(first))
            self._set_status(f"Treffer geladen: {visible} sichtbar / {len(self.hits)} gesamt aus {source_path.name}")
        else:
            self.info_var.set("Keine Treffer für die aktuelle Filterung sichtbar.")
            self._set_status(f"Keine sichtbaren Treffer in {source_path.name}")

    def _find_bird_asset(self) -> Path | None:
        p = self._project()
        candidates: list[Path] = []
        if p is not None:
            root = getattr(p, "root_path", None)
            if root:
                root = Path(root)
                candidates.extend([
                    root / "assets" / "vogel2_light_512_fixed.png",
                    root / "Assets" / "vogel2_light_512_fixed.png",
                    root / "bleepling" / "assets" / "vogel2_light_512_fixed.png",
                    root / "Bleepling" / "assets" / "vogel2_light_512_fixed.png",
                    root / "Bleepling" / "Assets" / "vogel2_light_512_fixed.png",
                    root / "Bliebling" / "Assets" / "vogel2_light_512_fixed.png",
                    root / "Bliebling" / "assets" / "vogel2_light_512_fixed.png",
                ])
        here = Path(__file__).resolve()
        candidates.extend([
            here.parents[1] / "assets" / "vogel2_light_512_fixed.png",
            here.parents[2] / "assets" / "vogel2_light_512_fixed.png",
            here.parents[3] / "assets" / "vogel2_light_512_fixed.png",
            here.parents[3] / "Assets" / "vogel2_light_512_fixed.png",
        ])
        for cand in candidates:
            if cand.exists():
                return cand
        return None

    def _create_bird_label(self, parent):
        bird_path = self._find_bird_asset()
        if bird_path is not None:
            try:
                img = tk.PhotoImage(file=str(bird_path))
                while img.width() > 300:
                    img = img.subsample(2, 2)
                self._bird_image = img
                self._bird_label = ttk.Label(parent, image=self._bird_image, anchor="center")
                return self._bird_label
            except Exception:
                pass
        self._bird_label = ttk.Label(parent, text="🐦", font=("Segoe UI Emoji", 80), anchor="center")
        return self._bird_label

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        left = ttk.Frame(self, padding=10)
        left.grid(row=0, column=0, sticky="nsew")
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)

        right = ttk.Frame(self, padding=(0, 10, 10, 10))
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(2, weight=1)

        source_box = ttk.LabelFrame(left, text="Medium und Trefferquelle", padding=10)
        source_box.grid(row=0, column=0, sticky="ew")
        source_box.columnconfigure(1, weight=1)

        ttk.Label(source_box, text="Medium:").grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.media_combo = ttk.Combobox(source_box, textvariable=self.media_var, state="readonly")
        self.media_combo.grid(row=0, column=1, sticky="ew", pady=(0, 6))
        self.media_combo.bind("<<ComboboxSelected>>", self._on_media_changed)

        ttk.Label(source_box, text="Trefferquelle:").grid(row=1, column=0, sticky="w", pady=(0, 6))
        self.source_combo = ttk.Combobox(source_box, textvariable=self.source_var, state="readonly")
        self.source_combo.grid(row=1, column=1, sticky="ew", pady=(0, 6))
        self.source_combo.bind("<<ComboboxSelected>>", self._on_source_changed)

        ttk.Label(source_box, text="Filter:").grid(row=2, column=0, sticky="w", pady=(0, 6))
        filter_combo = ttk.Combobox(source_box, textvariable=self.filter_var, state="readonly", values=["offen / prüfen / bleepen", "nur offene"])
        filter_combo.grid(row=2, column=1, sticky="w", pady=(0, 6))
        filter_combo.bind("<<ComboboxSelected>>", lambda *_: self._load_hits_from_selected_source())

        timing_box = ttk.LabelFrame(left, text="Prüfbereich und Feintuning", padding=10)
        timing_box.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        timing_box.columnconfigure(0, weight=1)
        timing_box.columnconfigure(1, weight=0)
        timing_box.rowconfigure(1, weight=1)

        ctrl = ttk.Frame(timing_box)
        ctrl.grid(row=0, column=0, sticky="ew")
        for i in range(4):
            ctrl.columnconfigure(i, weight=1)
        ttk.Label(ctrl, text="Prüf-Vorlauf (s):").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(ctrl, from_=1, to=30, textvariable=self.preview_preroll_var, width=6, command=self._invalidate_preview).grid(row=0, column=1, sticky="w")
        ttk.Label(ctrl, text="Prüf-Nachlauf (s):").grid(row=0, column=2, sticky="w")
        ttk.Spinbox(ctrl, from_=1, to=20, textvariable=self.preview_postroll_var, width=6, command=self._invalidate_preview).grid(row=0, column=3, sticky="w")

        self.hit_tree = ttk.Treeview(timing_box, columns=("beginn", "ende", "treffer", "quelle", "status"), show="headings", height=14)
        self.hit_tree.heading("beginn", text="Beginn")
        self.hit_tree.heading("ende", text="Ende")
        self.hit_tree.heading("treffer", text="Treffer")
        self.hit_tree.heading("quelle", text="Quelle")
        self.hit_tree.heading("status", text="Status")
        self.hit_tree.column("beginn", width=100, anchor="w", stretch=False)
        self.hit_tree.column("ende", width=100, anchor="w", stretch=False)
        self.hit_tree.column("treffer", width=240, anchor="w")
        self.hit_tree.column("quelle", width=90, anchor="w", stretch=False)
        self.hit_tree.column("status", width=90, anchor="w", stretch=False)
        self.hit_tree.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        self.hit_tree.bind("<<TreeviewSelect>>", self._on_hit_selected)

        hit_scroll = ttk.Scrollbar(timing_box, orient="vertical", command=self.hit_tree.yview)
        hit_scroll.grid(row=1, column=1, sticky="ns", pady=(8, 0))
        self.hit_tree.configure(yscrollcommand=hit_scroll.set)

        fine_box = ttk.Frame(timing_box)
        fine_box.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        ttk.Label(fine_box, text="Bleep-Beginn:").grid(row=0, column=0, sticky="w")
        for idx, delta_ms in enumerate((-250, -100, -50, 50, 100, 250), start=1):
            ttk.Button(fine_box, text=f"{delta_ms:+d}", width=5, command=lambda d=delta_ms: self._adjust_active_edge("start", d)).grid(row=0, column=idx, padx=(4, 0))
        ttk.Label(fine_box, text="Bleep-Ende:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        for idx, delta_ms in enumerate((-250, -100, -50, 50, 100, 250), start=1):
            ttk.Button(fine_box, text=f"{delta_ms:+d}", width=5, command=lambda d=delta_ms: self._adjust_active_edge("end", d)).grid(row=1, column=idx, padx=(4, 0), pady=(6, 0))

        detail_box = ttk.LabelFrame(left, text="Aktiver Treffer", padding=10)
        detail_box.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        ttk.Label(detail_box, textvariable=self.info_var, wraplength=540, justify="left").grid(row=0, column=0, sticky="w")
        ttk.Label(detail_box, textvariable=self.bleep_summary_var, wraplength=540, justify="left").grid(row=1, column=0, sticky="w", pady=(6, 0))

        audio_header = ttk.Frame(right)
        audio_header.grid(row=0, column=0, sticky="ew")
        audio_header.columnconfigure(0, weight=1)
        ttk.Label(audio_header, text="Treffer prüfen – Audio", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(audio_header, textvariable=self.audio_status_var).grid(row=1, column=0, sticky="w", pady=(2, 8))

        hint_box = ttk.LabelFrame(right, text="Hinweis", padding=10)
        hint_box.grid(row=1, column=0, sticky="ew")
        ttk.Label(hint_box, textvariable=self.preview_hint_var, wraplength=540, justify="left").grid(row=0, column=0, sticky="w")

        player_box = ttk.LabelFrame(right, text="Audio-Vorschau", padding=10)
        player_box.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        player_box.columnconfigure(0, weight=1)
        player_box.rowconfigure(3, weight=1)

        ttk.Label(player_box, textvariable=self.position_var).grid(row=0, column=0, sticky="w")
        self.progress = ttk.Scale(player_box, from_=0, to=1000, orient="horizontal")
        self.progress.grid(row=1, column=0, sticky="ew", pady=(8, 4))

        transport = ttk.Frame(player_box)
        transport.grid(row=2, column=0, sticky="w", pady=(0, 6))
        ttk.Button(transport, text="▶ Prüf", width=7, command=self.play_preview_clip).grid(row=0, column=0, padx=(0, 4))
        ttk.Button(transport, text="Zum Treffer", width=10, command=self.jump_to_hit).grid(row=0, column=1, padx=(0, 4))
        ttk.Button(transport, text="▶", width=3, command=self.play).grid(row=0, column=2, padx=(0, 4))
        ttk.Button(transport, text="⏸", width=3, command=self.pause).grid(row=0, column=3, padx=(0, 4))
        ttk.Button(transport, text="■", width=3, command=self.stop).grid(row=0, column=4, padx=(0, 4))
        ttk.Button(transport, text="Nächster", width=8, command=self.select_next_hit).grid(row=0, column=5, padx=(0, 8))
        ttk.Button(transport, text="−10s", width=5, command=lambda: self._relative_seek(-10.0)).grid(row=0, column=6, padx=(0, 4))
        ttk.Button(transport, text="−5s", width=4, command=lambda: self._relative_seek(-5.0)).grid(row=0, column=7, padx=(0, 4))
        ttk.Button(transport, text="−1s", width=4, command=lambda: self._relative_seek(-1.0)).grid(row=0, column=8, padx=(0, 4))
        ttk.Button(transport, text="+1s", width=4, command=lambda: self._relative_seek(1.0)).grid(row=0, column=9)

        bird_frame = ttk.Frame(player_box)
        bird_frame.grid(row=3, column=0, sticky="nsew")
        bird_frame.columnconfigure(0, weight=1)
        bird_frame.rowconfigure(0, weight=1)
        self._create_bird_label(bird_frame).grid(row=0, column=0)

        actions = ttk.Frame(player_box)
        actions.grid(row=4, column=0, sticky="ew", pady=(8, 0))
        for col in range(3):
            actions.columnconfigure(col, weight=1, uniform="hitreview_actions")

        ttk.Button(actions, text="Übernehmen", command=lambda: self._set_active_status("übernommen")).grid(row=0, column=0, padx=(0, 6), pady=(0, 6), sticky="ew")
        ttk.Button(actions, text="Verwerfen", command=lambda: self._set_active_status("verworfen")).grid(row=0, column=1, padx=3, pady=(0, 6), sticky="ew")
        ttk.Button(actions, text="Offen", command=lambda: self._set_active_status("offen")).grid(row=0, column=2, padx=(6, 0), pady=(0, 6), sticky="ew")

        ttk.Button(actions, text="Markierte übernehmen", command=lambda: self._set_selected_status("übernommen")).grid(row=1, column=0, padx=(0, 6), pady=(0, 6), sticky="ew")
        ttk.Button(actions, text="Markierte verwerfen", command=lambda: self._set_selected_status("verworfen")).grid(row=1, column=1, padx=3, pady=(0, 6), sticky="ew")
        ttk.Button(actions, text="Markierte offen", command=lambda: self._set_selected_status("offen")).grid(row=1, column=2, padx=(6, 0), pady=(0, 6), sticky="ew")

        ttk.Button(actions, text="Alle sichtbaren übernehmen", command=lambda: self._set_all_visible_status("übernommen")).grid(row=2, column=0, padx=(0, 6), sticky="ew")
        ttk.Button(actions, text="Alle sichtbaren verwerfen", command=lambda: self._set_all_visible_status("verworfen")).grid(row=2, column=1, padx=3, sticky="ew")
        ttk.Button(actions, text="Alle sichtbaren offen", command=lambda: self._set_all_visible_status("offen")).grid(row=2, column=2, padx=(6, 0), sticky="ew")

    def _invalidate_preview(self, *_):
        self._preview_meta = {}
        self._preview_generation_token += 1

    def _settings_signature(self) -> tuple:
        s = self._get_ffmpeg_bleep_settings()
        return (
            int(self.preview_preroll_var.get()),
            int(self.preview_postroll_var.get()),
            int(s["freq"]),
            float(s["gain"]),
        )

    def _current_hit(self) -> dict | None:
        if self.active_hit_index is None or not (0 <= self.active_hit_index < len(self.hits)):
            return None
        return self.hits[self.active_hit_index]

    def _compute_preview_window(self, hit: dict) -> dict[str, float]:
        base_start = hit.get("detected_start")
        base_end = hit.get("detected_end")
        if base_start is None or base_end is None:
            ts = _parse_timestamp(hit.get("timestamp", ""))
            if ts is None:
                raise RuntimeError("Ungültiger Zeitstempel im aktiven Treffer.")
            base_start = base_end = ts

        start_offset = float(hit.get("start_offset_ms", 0)) / 1000.0
        end_offset = float(hit.get("end_offset_ms", 0)) / 1000.0

        bleep_start = max(0.0, float(base_start) - (SPAN_PAD_MS / 1000.0) + start_offset)
        bleep_end = max(
            bleep_start + MIN_BLEEP_DURATION,
            float(base_end) + ((SPAN_PAD_MS + END_SAFETY_PAD_MS) / 1000.0) + end_offset,
        )

        clip_start = max(0.0, bleep_start - float(self.preview_preroll_var.get()))
        clip_end = max(bleep_end + float(self.preview_postroll_var.get()), clip_start + 0.5)
        duration = max(0.2, clip_end - clip_start)
        return {
            "base_start": float(base_start),
            "base_end": float(base_end),
            "bleep_start": bleep_start,
            "bleep_end": bleep_end,
            "clip_start": clip_start,
            "clip_end": clip_end,
            "duration": duration,
            "local_hit_ms": int(round((bleep_start - clip_start) * 1000)),
            "local_bleep_start": max(0.0, bleep_start - clip_start),
            "local_bleep_end": max(0.0, bleep_end - clip_start),
        }

    def _update_bleep_summary(self):
        hit = self._current_hit()
        if not hit:
            self.bleep_summary_var.set("Bleepfenster: -")
            return
        try:
            meta = self._compute_preview_window(hit)
            self.bleep_summary_var.set(
                "Erkannte Wortspanne: "
                f"{_format_timestamp(meta['base_start'])} bis {_format_timestamp(meta['base_end'])} | "
                "Bleepfenster: "
                f"{_format_timestamp(meta['bleep_start'])} bis {_format_timestamp(meta['bleep_end'])} "
                f"(Dauer {_format_timestamp(meta['bleep_end'] - meta['bleep_start'])})"
            )
        except Exception:
            self.bleep_summary_var.set("Bleepfenster: -")

    def _on_media_changed(self, *_):
        match = self._guess_matching_source_label(self.media_var.get())
        if match:
            self.source_var.set(match)
            self._load_hits_from_selected_source()
        self._invalidate_preview()

    def _on_source_changed(self, *_):
        guess = self._guess_matching_media_name(self.source_var.get())
        if guess:
            self.media_var.set(guess)
        self._load_hits_from_selected_source()
        self._invalidate_preview()

    def _on_hit_selected(self, *_):
        selected = self.hit_tree.selection()
        if not selected:
            return
        self._activate_hit(int(selected[0]))

    def _activate_hit(self, index: int):
        if index < 0 or index >= len(self.hits):
            return
        self.active_hit_index = index
        hit = self.hits[index]
        self.timestamp_var.set(hit["timestamp"])
        self.info_var.set(
            f"Aktiver Treffer: {hit['label']} | Beginn: {hit.get('begin_ts', hit['timestamp'])} | Ende: {hit.get('end_ts', hit['timestamp'])}\n"
            f"Quelle: {hit['source_decision']} | Status: {hit['review_status']}\n"
            f"Begründung: {hit.get('reason', '') or '-'}\nKontext: {hit.get('context', '') or '-'}"
        )
        self._update_bleep_summary()
        self._invalidate_preview()

    def _adjust_active_edge(self, edge: str, delta_ms: int):
        hit = self._current_hit()
        if not hit:
            return
        key = "start_offset_ms" if edge == "start" else "end_offset_ms"
        hit[key] = int(hit.get(key, 0)) + int(delta_ms)
        hit["adjusted"] = True
        self._update_bleep_summary()
        self._invalidate_preview()
        self._set_status(f"Treffer feinjustiert: {edge} {delta_ms:+d} ms")

    def _refresh_hit_row(self, index: int):
        if 0 <= index < len(self.hits):
            hit = self.hits[index]
            iid = str(index)
            if iid in self.hit_tree.get_children():
                self.hit_tree.item(iid, values=(hit["begin_ts"], hit["end_ts"], hit["label"], hit["source_decision"], hit["review_status"]))

    def _set_indices_status(self, indices: list[int], new_status: str) -> int:
        changed = 0
        for index in indices:
            if 0 <= index < len(self.hits):
                self.hits[index]["review_status"] = new_status
                self._refresh_hit_row(index)
                changed += 1
        if changed and self.active_hit_index is not None:
            self._activate_hit(self.active_hit_index)
        return changed

    def _set_active_status(self, new_status: str):
        hit = self._current_hit()
        if not hit or self.active_hit_index is None:
            return
        changed = self._set_indices_status([self.active_hit_index], new_status)
        if changed:
            self._set_status(f"Trefferstatus gesetzt: {new_status}")

    def _set_selected_status(self, new_status: str):
        selected = [int(iid) for iid in self.hit_tree.selection() if str(iid).isdigit()]
        if not selected:
            self._set_status("Keine Treffer markiert.")
            return
        changed = self._set_indices_status(selected, new_status)
        if changed:
            self._set_status(f"{changed} markierte Treffer auf {new_status} gesetzt.")

    def _set_all_visible_status(self, new_status: str):
        visible = [int(iid) for iid in self.hit_tree.get_children() if str(iid).isdigit()]
        if not visible:
            self._set_status("Keine sichtbaren Treffer vorhanden.")
            return
        changed = self._set_indices_status(visible, new_status)
        if changed:
            self._set_status(f"{changed} sichtbare Treffer auf {new_status} gesetzt.")

    def refresh(self):
        self.media_map = self._available_media_paths()
        self.source_map = self._available_source_paths()
        self.words_map = self._available_words_json_paths()
        self.media_combo["values"] = list(self.media_map.keys())
        self.source_combo["values"] = list(self.source_map.keys())
        if self.media_map and (not self.media_var.get() or self.media_var.get() not in self.media_map):
            self.media_var.set(next(iter(self.media_map.keys())))
        if self.source_map and (not self.source_var.get() or self.source_var.get() not in self.source_map):
            guessed = self._guess_matching_source_label(self.media_var.get()) if self.media_var.get() else None
            self.source_var.set(guessed or next(iter(self.source_map.keys())))
        if self.source_var.get() in self.source_map:
            self._load_hits_from_selected_source()

    def _cache_key(self, kind: str, media_path: Path, hit: dict, meta: dict[str, float]) -> tuple:
        return (
            kind,
            str(media_path),
            hit.get("label", ""),
            int(round(meta["bleep_start"] * 1000)),
            int(round(meta["bleep_end"] * 1000)),
            int(round(meta["clip_start"] * 1000)),
            int(round(meta["clip_end"] * 1000)),
            int(hit.get("start_offset_ms", 0)),
            int(hit.get("end_offset_ms", 0)),
            *self._settings_signature(),
        )

    def _build_preview_command(self, media_path: Path, out_path: Path, kind: str, meta: dict[str, float]) -> list[str]:
        ffmpeg = self._ffmpeg()
        if not ffmpeg:
            raise RuntimeError("FFmpeg wurde nicht gefunden.")
        cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{meta['clip_start']:.3f}", "-t", f"{meta['duration']:.3f}", "-i", str(media_path)]
        if kind == "original":
            cmd += ["-vn", "-ac", "1", "-ar", "44100", "-c:a", "pcm_s16le", str(out_path)]
            return cmd
        settings = self._get_ffmpeg_bleep_settings()
        preview_gain = max(1.8, float(settings["gain"]) * 2.2)
        bleep_start = max(0.0, float(meta["local_bleep_start"]))
        bleep_end = max(bleep_start + MIN_BLEEP_DURATION, float(meta["local_bleep_end"]))
        bleep_duration = max(MIN_BLEEP_DURATION, bleep_end - bleep_start)
        bleep_delay_ms = int(round(bleep_start * 1000.0))
        filt = (
            f"[0:a]aresample=44100,volume='if(between(t,{bleep_start:.3f},{bleep_end:.3f}),0,1)'[base];"
            f"sine=f={int(settings['freq'])}:sample_rate=44100:duration={bleep_duration:.3f},"
            f"volume={preview_gain:.3f},adelay={bleep_delay_ms}|{bleep_delay_ms}[tone];"
            f"[base][tone]amix=inputs=2:normalize=0[aout]"
        )
        cmd += ["-vn", "-filter_complex", filt, "-map", "[aout]", "-ac", "1", "-ar", "44100", "-c:a", "pcm_s16le", str(out_path)]
        return cmd

    def _generate_preview_async(self, kind: str, autoplay_from_ms: int | None = None):
        hit = self._current_hit()
        if not hit:
            self._set_status("Kein aktiver Treffer ausgewählt.")
            return
        media_path = self.media_map.get(self.media_var.get())
        if not media_path or not media_path.exists():
            self._set_status("Kein passendes Medium ausgewählt.")
            return
        self.current_media_path = media_path
        try:
            meta = self._compute_preview_window(hit)
        except Exception as exc:
            self._set_status(f"Prüfbereich konnte nicht berechnet werden: {exc}")
            return
        cache_key = self._cache_key(kind, media_path, hit, meta)
        cached = self._preview_cache.get(cache_key)
        if cached and cached.exists():
            self._load_preview_file(cached, kind, meta, autoplay_from_ms)
            return

        preview_dir = self._preview_dir()
        preview_dir.mkdir(parents=True, exist_ok=True)
        out_path = preview_dir / f"preview_{abs(hash(cache_key))}.wav"
        token = self._preview_generation_token = self._preview_generation_token + 1
        self._set_status(f"{('Prüfclip' if kind == 'beep' else 'Originalclip')} wird erzeugt …")

        def worker():
            try:
                cmd = self._build_preview_command(media_path, out_path, kind, meta)
                proc = subprocess.run(cmd, capture_output=True, text=True)
                if token != self._preview_generation_token:
                    return
                if proc.returncode != 0:
                    msg = (proc.stderr or proc.stdout or "unbekannter FFmpeg-Fehler").strip()
                    self.after(0, lambda: self._set_status(f"Preview-Erzeugung fehlgeschlagen: {msg}"))
                    return
                self._preview_cache[cache_key] = out_path
                self.after(0, lambda: self._load_preview_file(out_path, kind, meta, autoplay_from_ms))
            except Exception as exc:
                if token == self._preview_generation_token:
                    self.after(0, lambda: self._set_status(f"Preview-Erzeugung fehlgeschlagen: {exc}"))

        self._generation_thread = threading.Thread(target=worker, daemon=True)
        self._generation_thread.start()

    def _load_preview_file(self, path: Path, kind: str, meta: dict[str, float], autoplay_from_ms: int | None = None):
        try:
            self.player.load(path)
            self._preview_meta = {**meta, "path": str(path), "kind": kind}
            self._update_position_label(0)
            self.player.play(from_ms=0 if autoplay_from_ms is None else autoplay_from_ms)
            self._set_status(f"{('Prüfclip' if kind == 'beep' else 'Originalclip')} bereit: {path.name}")
        except Exception as exc:
            self._set_status(f"Preview konnte nicht geladen werden: {exc}")

    def play_preview_clip(self):
        self._generate_preview_async("beep", autoplay_from_ms=0)

    def play_original_clip(self):
        hit = self._current_hit()
        if not hit:
            return
        try:
            meta = self._compute_preview_window(hit)
            from_ms = int(meta["local_hit_ms"])
        except Exception:
            from_ms = 0
        self._generate_preview_async("original", autoplay_from_ms=from_ms)

    def jump_to_hit(self):
        hit = self._current_hit()
        if not hit:
            return
        try:
            meta = self._compute_preview_window(hit)
            from_ms = int(meta["local_hit_ms"])
        except Exception:
            from_ms = 0
        if self._preview_meta.get("path"):
            self.player.seek(from_ms, auto_play=True)
            self._update_position_label(from_ms)
            self._set_status("Zum Treffer gesprungen.")
        else:
            self._generate_preview_async("beep", autoplay_from_ms=from_ms)

    def select_next_hit(self):
        children = self.hit_tree.get_children()
        if not children:
            return
        if self.active_hit_index is None:
            target = children[0]
        else:
            current_iid = str(self.active_hit_index)
            if current_iid in children:
                idx = children.index(current_iid)
                target = children[min(len(children) - 1, idx + 1)]
            else:
                target = children[0]
        self.hit_tree.selection_set(target)
        self.hit_tree.see(target)
        self._activate_hit(int(target))
        self.play_preview_clip()

    def play(self):
        if self._preview_meta.get("path"):
            try:
                self.player.play()
                self._set_status("Wiedergabe gestartet.")
                return
            except Exception as exc:
                self._set_status(f"Wiedergabe fehlgeschlagen: {exc}")
        self.play_preview_clip()

    def pause(self):
        try:
            self.player.pause()
            self._set_status("Wiedergabe pausiert.")
        except Exception as exc:
            self._set_status(f"Pause fehlgeschlagen: {exc}")

    def stop(self):
        try:
            self.player.stop()
            self._update_position_label(0)
            self._set_status("Wiedergabe gestoppt.")
        except Exception as exc:
            self._set_status(f"Stop fehlgeschlagen: {exc}")

    def _relative_seek(self, delta_seconds: float):
        if not self._preview_meta.get("path"):
            self.play_preview_clip()
            return
        try:
            current = self.player.get_position_ms()
            length = self.player.get_length_ms()
            new_pos = max(0, min(length, current + int(delta_seconds * 1000)))
            self.player.seek(new_pos, auto_play=True)
            self._update_position_label(new_pos)
            self._set_status(f"Relativer Sprung: {delta_seconds:+.1f} s")
        except Exception as exc:
            self._set_status(f"Relativer Sprung fehlgeschlagen: {exc}")

    def _update_position_label(self, current_ms: int | None = None):
        if current_ms is None:
            current_ms = self.player.get_position_ms()
        length_ms = self.player.get_length_ms()
        self.position_var.set(f"Position: {_format_timestamp((current_ms or 0)/1000.0)} / {_format_timestamp((length_ms or 0)/1000.0)}")
        try:
            self.progress.configure(to=max(1, length_ms or 1))
            self.progress.set(max(0, current_ms or 0))
        except Exception:
            pass

    def _poll_position(self):
        try:
            self._update_position_label()
        except Exception:
            pass
        self._position_after_id = self.after(250, self._poll_position)

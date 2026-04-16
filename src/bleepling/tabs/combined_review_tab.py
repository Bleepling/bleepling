from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from bleepling.services.time_service import parse_time_point
from bleepling.tabs.bleeping_tab import _safe_read_lines, _safe_write_lines
from bleepling.tabs.hit_review_tab import HitReviewTab, _list_files, MEDIA_EXTS, VIDEO_EXTS, _format_timestamp
from bleepling.utils.help_dialog import show_help_dialog


def _write_range_times_lines(path: Path, lines):
    _safe_write_lines(path, lines)


class _BleepingTabBridge:
    def __init__(self, owner: "CombinedReviewTab"):
        self.owner = owner

    def tab(self):
        return getattr(self.owner.app, "bleeping_tab", None)

    def sync_to_tab(self):
        bt = self.tab()
        if bt is None:
            return None
        bt.video_var.set(self.owner.video_var.get())
        bt.wav_var.set(self.owner.wav_var.get())
        bt.json_var.set(self.owner.json_var.get())
        bt.candidate_var.set(self.owner.candidate_var.get())
        bt.block_thr.set(int(self.owner.block_thr.get()))
        bt.allow_thr.set(int(self.owner.allow_thr.get()))
        bt.participant_surnames_only.set(bool(self.owner.participant_surnames_only.get()))
        bt.participant_include_firstnames.set(bool(self.owner.participant_include_firstnames.get()))
        bt.block_text.delete("1.0", "end")
        bt.block_text.insert("1.0", self.owner.block_text.get("1.0", "end"))
        bt.allow_text.delete("1.0", "end")
        bt.allow_text.insert("1.0", self.owner.allow_text.get("1.0", "end"))
        return bt

    def sync_from_tab(self):
        bt = self.tab()
        if bt is None:
            return None
        self.owner.video_var.set(bt.video_var.get())
        self.owner.wav_var.set(bt.wav_var.get())
        self.owner.json_var.set(bt.json_var.get())
        self.owner.candidate_var.set(bt.candidate_var.get())
        self.owner.block_thr.set(int(bt.block_thr.get()))
        self.owner.allow_thr.set(int(bt.allow_thr.get()))
        self.owner.participant_surnames_only.set(bool(bt.participant_surnames_only.get()))
        self.owner.participant_include_firstnames.set(bool(bt.participant_include_firstnames.get()))
        self.owner.block_text.delete("1.0", "end")
        self.owner.block_text.insert("1.0", bt.block_text.get("1.0", "end"))
        self.owner.allow_text.delete("1.0", "end")
        self.owner.allow_text.insert("1.0", bt.allow_text.get("1.0", "end"))
        return bt


class _FFmpegTabBridge:
    def __init__(self, owner: "CombinedReviewTab"):
        self.owner = owner

    def tab(self):
        return getattr(self.owner.app, "ffmpeg_tab", None)

    def push_bleep_params(self):
        ff = self.tab()
        if ff is None:
            return None
        try:
            ff.bleep_freq_var.set(int(self.owner.bleep_freq_var.get()))
            ff.bleep_gain_var.set(float(self.owner.bleep_gain_var.get()))
            ff.bleep_pre_ms_var.set(int(self.owner.bleep_pre_ms_var.get()))
            ff.bleep_post_ms_var.set(int(self.owner.bleep_post_ms_var.get()))
        except Exception:
            pass
        return ff

    def pull_bleep_params(self):
        ff = self.tab()
        if ff is None:
            return None
        try:
            self.owner.bleep_freq_var.set(int(ff.bleep_freq_var.get()))
            self.owner.bleep_gain_var.set(float(ff.bleep_gain_var.get()))
            self.owner.bleep_pre_ms_var.set(int(ff.bleep_pre_ms_var.get()))
            self.owner.bleep_post_ms_var.set(int(ff.bleep_post_ms_var.get()))
        except Exception:
            pass
        return ff


class _CombinedHitListHelper:
    def __init__(self, owner: "CombinedReviewTab"):
        self.owner = owner

    def build_hits_from_preview_rows(self, rows):
        hits = []
        for line_number, row in enumerate(rows, start=1):
            if len(row) < 5:
                continue
            ts, cand, result, rule, ctx = row
            source_decision = str(result).strip().lower()
            hits.append({
                "timestamp": str(ts),
                "begin_ts": str(ts),
                "end_ts": str(ts),
                "label": str(cand).strip() or "(ohne Kandidat)",
                "source_decision": source_decision or "offen",
                "review_status": source_decision if source_decision in {"bleepen", "prüfen", "ignorieren", "erlaubt"} else "offen",
                "reason": str(rule).strip(),
                "context": str(ctx).strip(),
                "line_number": line_number,
                "adjusted": False,
                "start_offset_ms": 0,
                "end_offset_ms": 0,
                "detected_start": None,
                "detected_end": None,
            })
        return hits

    def selected_indices(self) -> list[int]:
        indices: list[int] = []
        for iid in self.owner.hit_tree.selection():
            try:
                indices.append(int(iid))
            except Exception:
                pass
        return sorted(set(i for i in indices if 0 <= i < len(self.owner.hits)))

    def visible_hit_rows(self):
        filter_mode = self.owner.filter_var.get().strip().lower()
        rows = []
        for index, hit in enumerate(self.owner.hits):
            status = str(hit.get("review_status", "")).strip().lower()
            if filter_mode == "nur offene":
                show = status in {"offen", "prüfen"}
            else:
                show = status in {"offen", "prüfen", "bleepen", "übernommen"}
            if not show:
                continue
            rows.append((
                str(index),
                (
                    hit.get("line_number", index + 1),
                    hit["begin_ts"],
                    hit["end_ts"],
                    hit["label"],
                    hit["review_status"],
                    hit.get("reason", "") or hit["source_decision"],
                ),
            ))
        return rows

    def rebuild_tree(self) -> int:
        self.owner.hit_tree.delete(*self.owner.hit_tree.get_children())
        visible_rows = self.visible_hit_rows()
        first_visible_iid = None
        for iid, values in visible_rows:
            self.owner.hit_tree.insert("", "end", iid=iid, values=values)
            if first_visible_iid is None:
                first_visible_iid = iid
        if self.owner.active_hit_index is not None and str(self.owner.active_hit_index) in self.owner.hit_tree.get_children():
            self.owner.hit_tree.selection_set(str(self.owner.active_hit_index))
            self.owner._activate_hit(self.owner.active_hit_index)
        elif first_visible_iid is not None:
            self.owner.hit_tree.selection_set(first_visible_iid)
            self.owner._activate_hit(int(first_visible_iid))
        else:
            self.owner.active_hit_index = None
            self.owner._set_info_text("—", "—", "—", "—", "—", "-", "Keine Treffer für die aktuelle Filterung sichtbar.")
        return len(visible_rows)


class CombinedReviewTab(HitReviewTab):
    """Erste echte Vergleichs-/Testfläche für den verschmolzenen Prüfworkflow.
    Bestehende Reiter bleiben unverändert. Dieser Reiter delegiert die Vorbereitung
    an den vorhandenen Bleeping-Reiter und nutzt die Audio-/Feinprüf-Logik aus
    HitReviewTab, damit mit realen Projektdaten getestet werden kann.
    """
    def _make_bold_labelframe(self, parent, title: str):
        lbl = tk.Label(parent, text=title, font=("Segoe UI", 10, "bold"))
        return ttk.LabelFrame(parent, labelwidget=lbl)
    def _preferred_review_media_map(self) -> dict[str, Path]:
        p = self._project()
        if not p:
            return {}
        files: dict[str, Path] = {}
        # Für die Prüfung bewusst nur Originalmedien und Transkriptions-WAV,
        # keine bereits gerenderten Ausgabedateien.
        for name in _list_files(getattr(p, "transcription_wav_dir", p.root_path / "02_transcription" / "wav"), {".wav"}):
            files.setdefault(name, getattr(p, "transcription_wav_dir", p.root_path / "02_transcription" / "wav") / name)
        for name in _list_files(p.input_audio_dir, MEDIA_EXTS):
            files.setdefault(name, p.input_audio_dir / name)
        for name in _list_files(p.input_video_dir, VIDEO_EXTS):
            files.setdefault(name, p.input_video_dir / name)
        return files
    def _choose_default_review_medium(self) -> str | None:
        preferred = self.wav_var.get().strip()
        if preferred and preferred in self.media_map:
            return preferred
        current = self.media_var.get().strip()
        if current and current in self.media_map:
            return current
        # sonst WAV vor Video bevorzugen
        for name in self.media_map:
            if Path(name).suffix.lower() == ".wav":
                return name
        return next(iter(self.media_map.keys()), None)
    def _build(self):
        # Top-level layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        # vars for top workflow area
        self.video_var = tk.StringVar()
        self.wav_var = tk.StringVar()
        self.json_var = tk.StringVar()
        self.candidate_var = tk.StringVar()
        self.block_thr = tk.IntVar(value=88)
        self.allow_thr = tk.IntVar(value=96)
        self.participant_surnames_only = tk.BooleanVar(value=True)
        self.participant_include_firstnames = tk.BooleanVar(value=False)
        self.bleep_freq_var = tk.IntVar(value=1000)
        self.bleep_gain_var = tk.DoubleVar(value=0.70)
        self.bleep_pre_ms_var = tk.IntVar(value=100)
        self.bleep_post_ms_var = tk.IntVar(value=300)
        top = ttk.Frame(self)
        top.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        for col in range(3):
            top.columnconfigure(col, weight=1)
        prep = self._make_bold_labelframe(top, "1) Vorbereitung")
        prep.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        prep.grid_columnconfigure(1, weight=1)
        prep.grid_columnconfigure(4, weight=1)
        ttk.Label(prep, text="Ausgangsvideo").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        self.video_combo = ttk.Combobox(prep, textvariable=self.video_var, state="readonly", width=24)
        self.video_combo.grid(row=0, column=1, sticky="we", padx=4, pady=4)
        ttk.Button(prep, text="WAV aus Video erzeugen", command=self.make_wav, style="Accent.TButton").grid(row=0, column=2, sticky="w", padx=6, pady=4)
        ttk.Label(prep, text="words.json").grid(row=0, column=3, sticky="w", padx=(12, 4), pady=4)
        self.json_combo = ttk.Combobox(prep, textvariable=self.json_var, state="readonly", width=24)
        self.json_combo.grid(row=0, column=4, sticky="we", padx=4, pady=4)
        ttk.Button(prep, text="Kandidaten erzeugen", command=self.make_candidates, style="Accent.TButton").grid(row=0, column=5, sticky="e", padx=8, pady=4)
        ttk.Label(prep, text="WAV").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        self.wav_combo = ttk.Combobox(prep, textvariable=self.wav_var, state="readonly", width=24)
        self.wav_combo.grid(row=1, column=1, sticky="we", padx=4, pady=4)
        ttk.Button(prep, text="words.json aus WAV", command=self.make_words_json_stub, style="Accent.TButton").grid(row=1, column=2, sticky="w", padx=6, pady=4)
        ttk.Button(prep, text="?", width=3, command=lambda: self._show_info("Vorbereitung", "Zuerst Medium wählen, dann WAV bzw. words.json erzeugen und schließlich die Kandidaten-Datei anlegen." )).grid(row=1, column=5, sticky="e", padx=8, pady=4)
        lists = self._make_bold_labelframe(top, "2) Namenslisten und Regeln")
        lists.grid(row=0, column=1, sticky="nsew", padx=6)
        lists.columnconfigure(0, weight=1)
        lists.columnconfigure(1, weight=1)
        ttk.Label(lists, text="Blocklist (optional)").grid(row=0, column=0, sticky="w", padx=8, pady=(8, 2))
        ttk.Label(lists, text="Allowlist (optional)").grid(row=0, column=1, sticky="w", padx=8, pady=(8, 2))
        self.block_text = tk.Text(lists, height=5, width=32, wrap="none", undo=True)
        self.block_text.grid(row=1, column=0, sticky="nsew", padx=(8, 4), pady=(0, 6))
        self.allow_text = tk.Text(lists, height=5, width=32, wrap="none", undo=True)
        self.allow_text.grid(row=1, column=1, sticky="nsew", padx=(4, 8), pady=(0, 6))
        list_bar = ttk.Frame(lists)
        list_bar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 6))
        ttk.Button(list_bar, text="Teilnehmerliste importieren", command=self.import_participant_list, style="Accent.TButton").pack(side="left")
        ttk.Checkbutton(list_bar, text="Nur Nachnamen", variable=self.participant_surnames_only).pack(side="left", padx=(12, 8))
        ttk.Checkbutton(list_bar, text="Vornamen zusätzlich", variable=self.participant_include_firstnames).pack(side="left")
        list_bar2 = ttk.Frame(lists)
        list_bar2.grid(row=3, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 8))
        for c in range(3):
            list_bar2.columnconfigure(c, weight=1)
        ttk.Button(list_bar2, text="Blocklist aus Kandidaten füllen", command=self.fill_blocklist_from_candidates, style="Accent.TButton").grid(row=0, column=0, sticky="ew", padx=(0, 4), pady=(0, 4))
        ttk.Button(list_bar2, text="Allowlist aus Kandidaten füllen", command=self.fill_allowlist_from_candidates, style="Accent.TButton").grid(row=0, column=1, sticky="ew", padx=4, pady=(0, 4))
        ttk.Button(list_bar2, text="?", width=3, command=lambda: self._show_info("Namenslisten und Regeln", "Blocklist und Allowlist werden wie bisher gepflegt. Die Allowlist hat bei der Auswertung Vorrang." )).grid(row=0, column=2, sticky="e", padx=(4, 0), pady=(0, 4))
        ttk.Button(list_bar2, text="Blocklist leeren", command=self.clear_blocklist).grid(row=1, column=0, sticky="ew", padx=(0, 4))
        ttk.Button(list_bar2, text="Allowlist leeren", command=self.clear_allowlist).grid(row=1, column=1, sticky="ew", padx=4)
        ttk.Button(list_bar2, text="Listen speichern", command=self.save_lists, style="Accent.TButton").grid(row=1, column=2, sticky="ew", padx=(4, 0))
        cand = self._make_bold_labelframe(top, "3) Kandidaten prüfen")
        cand.grid(row=0, column=2, sticky="nsew", padx=(6, 0))
        cand.grid_columnconfigure(1, weight=1)
        ttk.Label(cand, text="Kandidaten-Datei").grid(row=0, column=0, sticky="w", padx=8, pady=(8, 4))
        self.candidate_combo = ttk.Combobox(cand, textvariable=self.candidate_var, state="readonly", width=26)
        self.candidate_combo.grid(row=0, column=1, sticky="we", padx=4, pady=(8, 4))
        ttk.Button(cand, text="Datei laden", command=self.choose_candidate, style="Accent.TButton").grid(row=0, column=2, padx=8, pady=(8, 4))
        ttk.Button(cand, text="?", width=3, command=lambda: self._show_info("Kandidaten prüfen", "Die Auswertung verwendet die vorhandene Bleeping-Logik und lädt das Ergebnis direkt in den unteren Prüfbereich." )).grid(row=1, column=2, sticky="e", padx=8, pady=(0, 4))
        ttk.Label(cand, text="Blocklist-Fuzzy %").grid(row=2, column=0, sticky="w", padx=8, pady=4)
        ttk.Spinbox(cand, from_=50, to=100, textvariable=self.block_thr, width=5).grid(row=2, column=1, sticky="w", padx=4)
        ttk.Label(cand, text="Allowlist-Fuzzy %").grid(row=3, column=0, sticky="w", padx=8, pady=4)
        ttk.Spinbox(cand, from_=50, to=100, textvariable=self.allow_thr, width=5).grid(row=3, column=1, sticky="w", padx=4)
        ttk.Button(cand, text="Auswertung starten", command=self.evaluate_into_review, style="Accent.TButton").grid(row=4, column=0, columnspan=3, sticky="we", padx=8, pady=(8, 4))
        ttk.Button(cand, text="Schnell-Nachbleepen", command=self.quick, style="Accent.TButton").grid(row=5, column=0, columnspan=3, sticky="we", padx=8, pady=4)
        ttk.Button(cand, text="Liste aktualisieren", command=self.refresh, style="Accent.TButton").grid(row=6, column=0, columnspan=3, sticky="we", padx=8, pady=(4, 8))
        main = ttk.Frame(self)
        main.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)
        left = ttk.Frame(main)
        left.grid(row=0, column=0, sticky="nsew")
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)
        timing_box = self._make_bold_labelframe(left, "4) Trefferliste und Feinprüfung")
        timing_box.configure(padding=10)
        timing_box.grid(row=0, column=0, sticky="nsew")
        timing_box.columnconfigure(0, weight=1)
        timing_box.columnconfigure(1, weight=0)
        timing_box.rowconfigure(1, weight=1)
        ctrl = ttk.Frame(timing_box)
        ctrl.grid(row=0, column=0, sticky="ew")
        for i in range(6):
            ctrl.columnconfigure(i, weight=0)
        ctrl.columnconfigure(6, weight=1)
        ttk.Label(ctrl, text="Medium:").grid(row=0, column=0, sticky="w")
        self.media_combo = ttk.Combobox(ctrl, textvariable=self.media_var, state="readonly", width=28)
        self.media_combo.grid(row=0, column=1, sticky="w", padx=(4, 12))
        self.media_combo.bind("<<ComboboxSelected>>", self._on_media_changed)
        ttk.Label(ctrl, text="Filter:").grid(row=0, column=2, sticky="w")
        filter_combo = ttk.Combobox(ctrl, textvariable=self.filter_var, state="readonly", values=["offen / prüfen / bleepen", "nur offene"], width=18)
        filter_combo.grid(row=0, column=3, sticky="w", padx=(4, 12))
        filter_combo.bind("<<ComboboxSelected>>", lambda *_: self._rebuild_tree())
        ttk.Label(ctrl, text="Prüf-Vorlauf (s):").grid(row=0, column=4, sticky="w")
        ttk.Spinbox(ctrl, from_=1, to=30, textvariable=self.preview_preroll_var, width=5, command=self._invalidate_preview).grid(row=0, column=5, sticky="w", padx=(4, 8))
        ttk.Label(ctrl, text="Prüf-Nachlauf (s):").grid(row=0, column=6, sticky="e")
        ttk.Spinbox(ctrl, from_=1, to=20, textvariable=self.preview_postroll_var, width=5, command=self._invalidate_preview).grid(row=0, column=7, sticky="e", padx=(4, 0))
        self.hit_tree = ttk.Treeview(timing_box, columns=("nr", "beginn", "ende", "treffer", "ergebnis", "regel"), show="headings", height=16, selectmode="extended")
        for col, text, width in [
            ("nr", "#", 46),
            ("beginn", "Beginn", 100),
            ("ende", "Ende", 100),
            ("treffer", "Treffer", 180),
            ("ergebnis", "Ergebnis", 100),
            ("regel", "Regel", 260),
        ]:
            self.hit_tree.heading(col, text=text)
            self.hit_tree.column(col, width=width, anchor="w", stretch=(col in {"treffer", "regel"}))
        self.hit_tree.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        self.hit_tree.bind("<<TreeviewSelect>>", self._on_hit_selected)
        self.hit_tree.bind("<Control-a>", self._select_all_hits)
        self.hit_tree.bind("<Control-A>", self._select_all_hits)
        self.hit_tree.bind("<Shift-Down>", lambda e: self._extend_selection_by(1))
        self.hit_tree.bind("<Shift-Up>", lambda e: self._extend_selection_by(-1))
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
        detail_box = self._make_bold_labelframe(left, "Aktiver Treffer")
        detail_box.configure(padding=10)
        detail_box.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        detail_box.columnconfigure(0, weight=1)
        self.info_text = tk.Text(detail_box, height=4, wrap="word", relief="flat", borderwidth=0)
        self.info_text.grid(row=0, column=0, sticky="ew")
        self.info_text.tag_configure("bold", font=("Segoe UI", 9, "bold"))
        self.info_text.configure(state="disabled")
        ttk.Label(detail_box, textvariable=self.bleep_summary_var, wraplength=760, justify="left").grid(row=1, column=0, sticky="w", pady=(6, 0))
        right = self._make_bold_labelframe(main, "5) Audio-Vorschau und Aktionen")
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        right.columnconfigure(0, weight=1)
        right.rowconfigure(3, weight=1)
        ttk.Label(right, textvariable=self.audio_status_var).grid(row=0, column=0, sticky="w", padx=10, pady=(8, 8))
        hint_box = ttk.LabelFrame(right, text="Hinweis / Kontext", padding=10)
        hint_box.grid(row=1, column=0, sticky="ew", padx=10)
        ttk.Label(hint_box, textvariable=self.preview_hint_var, wraplength=520, justify="left").grid(row=0, column=0, sticky="w")
        bleepf = ttk.LabelFrame(right, text="Bleep-Parameter", padding=10)
        bleepf.grid(row=2, column=0, sticky="ew", padx=10, pady=(10, 0))
        ttk.Label(bleepf, text="Frequenz (Hz)").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(bleepf, from_=100, to=3000, increment=10, textvariable=self.bleep_freq_var, width=8).grid(row=0, column=1, sticky="w", padx=(6, 16))
        ttk.Label(bleepf, text="Lautstärke").grid(row=0, column=2, sticky="w")
        ttk.Spinbox(bleepf, from_=0.0, to=2.0, increment=0.05, textvariable=self.bleep_gain_var, width=8).grid(row=0, column=3, sticky="w", padx=(6, 16))
        ttk.Label(bleepf, text="Vorlauf (ms)").grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Spinbox(bleepf, from_=0, to=2000, increment=10, textvariable=self.bleep_pre_ms_var, width=8).grid(row=1, column=1, sticky="w", padx=(6, 16), pady=(6, 0))
        ttk.Label(bleepf, text="Nachlauf (ms)").grid(row=1, column=2, sticky="w", pady=(6, 0))
        ttk.Spinbox(bleepf, from_=0, to=2000, increment=10, textvariable=self.bleep_post_ms_var, width=8).grid(row=1, column=3, sticky="w", padx=(6, 16), pady=(6, 0))
        ttk.Button(bleepf, text="Anwenden", style="Accent.TButton", command=self._apply_bleep_params).grid(row=0, column=4, rowspan=2, sticky="ns", padx=(0, 6))
        ttk.Button(bleepf, text="?", width=3, command=lambda: self._show_info("Bleep-Parameter", "Diese Werte sind die globalen Grundparameter für die Prüfung im Reiter und für das spätere Rendern. Vorlauf und Nachlauf gelten zunächst für alle Treffer. Die Tasten im Bereich Feintuning ändern zusätzlich den Beginn oder das Ende des jeweils aktiven einzelnen Treffers. Individuelle Korrekturen pro Treffer bleiben erhalten, wenn die globalen Bleep-Parameter neu angewendet werden." )).grid(row=0, column=5, rowspan=2, sticky="ne")
        player_box = ttk.LabelFrame(right, text="Audio-Vorschau", padding=10)
        player_box.grid(row=3, column=0, sticky="nsew", padx=10, pady=(10, 10))
        player_box.columnconfigure(0, weight=1)
        player_box.rowconfigure(3, weight=1)
        ttk.Label(player_box, textvariable=self.position_var).grid(row=0, column=0, sticky="w")
        self.progress = ttk.Scale(player_box, from_=0, to=1000, orient="horizontal")
        self.progress.grid(row=1, column=0, sticky="ew", pady=(8, 4))
        transport = ttk.Frame(player_box)
        transport.grid(row=2, column=0, sticky="w", pady=(0, 6))
        for ix, (txt, cmd, width) in enumerate([
            ("▶ Prüf", self.play_preview_clip, 7),
            ("Zum Treffer", self.jump_to_hit, 10),
            ("▶", self.play, 3),
            ("⏸", self.pause, 3),
            ("■", self.stop, 3),
            ("Nächster", self.select_next_hit, 8),
            ("−5s", lambda: self._relative_seek(-5.0), 4),
        ]):
            ttk.Button(transport, text=txt, width=width, command=cmd).grid(row=0, column=ix, padx=(0, 4))
        bird_frame = ttk.Frame(player_box)
        bird_frame.grid(row=3, column=0, sticky="nsew")
        bird_frame.columnconfigure(0, weight=1)
        bird_frame.rowconfigure(0, weight=1)
        self._create_bird_label(bird_frame).grid(row=0, column=0)
        actions = ttk.Frame(player_box)
        actions.grid(row=4, column=0, sticky="ew", pady=(8, 0))
        for col in range(3):
            actions.columnconfigure(col, weight=1, uniform="combined_actions")
        ttk.Button(actions, text="Bleepen", command=lambda: self._set_active_status("bleepen")).grid(row=0, column=0, padx=(0, 6), pady=(0, 6), sticky="ew")
        ttk.Button(actions, text="Verwerfen", command=lambda: self._set_active_status("verworfen")).grid(row=0, column=1, padx=3, pady=(0, 6), sticky="ew")
        ttk.Button(actions, text="Offen lassen", command=lambda: self._set_active_status("offen")).grid(row=0, column=2, padx=(6, 0), pady=(0, 6), sticky="ew")
        ttk.Button(actions, text="In Blocklist", command=self.add_selected_to_blocklist, style="Accent.TButton").grid(row=1, column=0, padx=(0, 6), pady=(0, 6), sticky="ew")
        ttk.Button(actions, text="In Allowlist", command=self.add_selected_to_allowlist, style="Accent.TButton").grid(row=1, column=1, padx=3, pady=(0, 6), sticky="ew")
        ttk.Button(actions, text="Prüfstand speichern", command=self.save_reviewed_and_times, style="Accent.TButton").grid(row=1, column=2, padx=(6, 0), pady=(0, 6), sticky="ew")
        tk.Button(
            actions,
            text="Times ableiten",
            command=self.write_times_only,
            bg="#c62828",
            fg="white",
            activebackground="#b71c1c",
            activeforeground="white",
            relief="solid",
            bd=2,
            highlightthickness=0,
            font=("Segoe UI", 10, "bold"),
            padx=8,
            pady=4,
        ).grid(row=2, column=2, padx=(6, 0), sticky="ew", ipady=2)
    def _select_all_hits(self, _event=None):
        children = self.hit_tree.get_children()
        if not children:
            return "break"
        self._suppress_anchor_update = True
        try:
            self.hit_tree.selection_set(children)
            self._selection_anchor_iid = children[0]
            self._selection_cursor_iid = children[-1]
            self._preserve_selection_state = (children[0], children[-1])
            self.hit_tree.focus(children[-1])
            self.hit_tree.see(children[-1])
        finally:
            self._suppress_anchor_update = False
        return "break"
    def _extend_selection_by(self, delta: int):
        children = list(self.hit_tree.get_children())
        if not children:
            return "break"
        selected = [iid for iid in self.hit_tree.selection() if iid in children]
        if not selected:
            focus_iid = self.hit_tree.focus() or children[0]
            self._suppress_anchor_update = True
            try:
                self.hit_tree.selection_set((focus_iid,))
                self._selection_anchor_iid = focus_iid
                self._selection_cursor_iid = focus_iid
                self.hit_tree.focus(focus_iid)
                self.hit_tree.see(focus_iid)
            finally:
                self._suppress_anchor_update = False
            return "break"

        anchor_iid = getattr(self, "_selection_anchor_iid", None)
        cursor_iid = getattr(self, "_selection_cursor_iid", None)
        focus_iid = self.hit_tree.focus()

        if anchor_iid not in children:
            anchor_iid = selected[0]
        if cursor_iid not in children:
            cursor_iid = focus_iid if focus_iid in children else selected[-1]

        anchor_idx = children.index(anchor_iid)
        cursor_idx = children.index(cursor_iid)
        new_cursor_idx = max(0, min(len(children) - 1, cursor_idx + delta))

        start_idx = min(anchor_idx, new_cursor_idx)
        end_idx = max(anchor_idx, new_cursor_idx)
        new_cursor_iid = children[new_cursor_idx]
        rng = children[start_idx:end_idx + 1]

        self._suppress_anchor_update = True
        try:
            self.hit_tree.selection_set(rng)
            self._selection_anchor_iid = anchor_iid
            self._selection_cursor_iid = new_cursor_iid
            self._preserve_selection_state = (anchor_iid, new_cursor_iid)
            self.hit_tree.focus(new_cursor_iid)
            self.hit_tree.see(new_cursor_iid)
        finally:
            self._suppress_anchor_update = False
        return "break"

    def _on_hit_selected(self, event=None):
        selection = self.hit_tree.selection()
        preserved = getattr(self, "_preserve_selection_state", None)
        if preserved and selection:
            self._selection_anchor_iid, self._selection_cursor_iid = preserved
            self._preserve_selection_state = None
            return super()._on_hit_selected(event)
        if selection and not getattr(self, "_suppress_anchor_update", False):
            self._selection_anchor_iid = selection[0]
            focus_iid = self.hit_tree.focus()
            self._selection_cursor_iid = focus_iid if focus_iid in selection else selection[-1]
        return super()._on_hit_selected(event)
    def _set_info_text(self, label: str, begin_ts: str, end_ts: str, source_decision: str, review_status: str, reason: str, context: str):
        if not hasattr(self, "info_text"):
            self.info_var.set(
                f"Aktiver Treffer: {label} | Beginn: {begin_ts} | Ende: {end_ts}\n"
                f"Quelle: {source_decision} | Status: {review_status}\n"
                f"Begründung: {reason or '-'}\nKontext: {context or '-'}"
            )
            return
        self.info_text.configure(state="normal")
        self.info_text.delete("1.0", "end")
        self.info_text.insert("end", f"Aktiver Treffer: {label} | Beginn: {begin_ts} | Ende: {end_ts}\n")
        self.info_text.insert("end", f"Quelle: {source_decision} | Status: {review_status}\n")
        self.info_text.insert("end", f"Begründung: {reason or '-'}\n")
        self.info_text.insert("end", "Kontext: ", ("bold",))
        self.info_text.insert("end", f"{context or '-'}", ("bold",))
        self.info_text.configure(state="disabled")

    def _activate_hit(self, index: int):
        super()._activate_hit(index)
        if index < 0 or index >= len(self.hits):
            return
        hit = self.hits[index]
        self._set_info_text(
            str(hit.get("label", "-")),
            str(hit.get("begin_ts", hit.get("timestamp", "-"))),
            str(hit.get("end_ts", hit.get("timestamp", "-"))),
            str(hit.get("source_decision", "-")),
            str(hit.get("review_status", "-")),
            str(hit.get("reason", "") or "-"),
            str(hit.get("context", "") or "-"),
        )

    def _project(self):
        return getattr(self.app, "project", None)

    def _bleeping_bridge(self):
        bridge = getattr(self, "_bleeping_tab_bridge", None)
        if bridge is None:
            bridge = _BleepingTabBridge(self)
            self._bleeping_tab_bridge = bridge
        return bridge

    def _ffmpeg_bridge(self):
        bridge = getattr(self, "_ffmpeg_tab_bridge", None)
        if bridge is None:
            bridge = _FFmpegTabBridge(self)
            self._ffmpeg_tab_bridge = bridge
        return bridge

    def _hit_list_helper(self):
        helper = getattr(self, "_combined_hit_list_helper", None)
        if helper is None:
            helper = _CombinedHitListHelper(self)
            self._combined_hit_list_helper = helper
        return helper

    def _bleeping(self):
        return self._bleeping_bridge().tab()

    def _show_info(self, title: str, text: str):
        show_help_dialog(self, title, text)
    def _sync_to_bleeping(self):
        self._bleeping_bridge().sync_to_tab()

    def _sync_from_bleeping(self):
        self._bleeping_bridge().sync_from_tab()

    def make_wav(self):
        bt = self._bleeping_bridge().sync_to_tab()
        if bt is None:
            return
        bt.make_wav()
        self.refresh()

    def make_words_json_stub(self):
        bt = self._bleeping_bridge().sync_to_tab()
        if bt is None:
            return
        bt.make_words_json_stub()
        self.refresh()

    def make_candidates(self):
        bt = self._bleeping_bridge().sync_to_tab()
        if bt is None:
            return
        bt.make_candidates()
        self.refresh()

    def import_participant_list(self):
        bt = self._bleeping_bridge().sync_to_tab()
        if bt is None:
            return
        bt.import_participant_list()
        self.refresh()

    def fill_blocklist_from_candidates(self):
        bt = self._bleeping_bridge().sync_to_tab()
        if bt is None:
            return
        bt.fill_blocklist_from_candidates()
        self._bleeping_bridge().sync_from_tab()
        self._set_status("Blocklist aus Kandidaten-Datei übernommen.")

    def clear_blocklist(self):
        self.block_text.delete("1.0", "end")
        self._sync_to_bleeping()
        self._set_status("Blocklist geleert.")

    def clear_allowlist(self):
        self.allow_text.delete("1.0", "end")
        self._sync_to_bleeping()
        self._set_status("Allowlist geleert.")

    def fill_allowlist_from_candidates(self):
        if not self._project() or not self.candidate_var.get():
            self._set_status("Bitte zuerst eine Kandidaten-Datei wählen.")
            return
        path = self._project().candidates_raw_dir / self.candidate_var.get()
        names = []
        for line in _safe_read_lines(path):
            parts = [p.strip() for p in line.split("|", 2)]
            if len(parts) >= 3 and parts[1]:
                names.append(parts[1])
        names = sorted(set(names))
        self.allow_text.delete("1.0", "end")
        self.allow_text.insert("1.0", "\n".join(names[:200]))
        self._sync_to_bleeping()
        self._set_status(f"Allowlist aus Kandidaten-Datei gefüllt. Übernommen: {min(len(names), 200)} Einträge.")


    def _apply_bleep_params(self):
        self._sync_bleep_params()
        self._recompute_all_hit_windows()
        self._set_status("Bleep-Parameter übernommen.")

    def _sync_bleep_params(self, *_):
        self._ffmpeg_bridge().push_bleep_params()
        self._invalidate_preview()

    def _pull_bleep_params_from_ffmpeg(self):
        self._ffmpeg_bridge().pull_bleep_params()
        if int(self.bleep_pre_ms_var.get()) == 600:
            self.bleep_pre_ms_var.set(100)
        if int(self.bleep_post_ms_var.get()) in {200, 1000}:
            self.bleep_post_ms_var.set(300)
        self._sync_bleep_params()

    def _get_ffmpeg_bleep_settings(self) -> dict[str, float | int]:
        return {"freq": int(self.bleep_freq_var.get()), "gain": float(self.bleep_gain_var.get())}

    def _recompute_all_hit_windows(self):
        if not getattr(self, "hits", None):
            self._invalidate_preview()
            return
        for hit in self.hits:
            try:
                meta = self._compute_preview_window(hit)
                hit["begin_ts"] = _format_timestamp(meta["bleep_start"])
                hit["end_ts"] = _format_timestamp(meta["bleep_end"])
            except Exception:
                start = hit.get("detected_start")
                end = hit.get("detected_end")
                if start is not None:
                    hit["begin_ts"] = _format_timestamp(float(start))
                    hit["end_ts"] = _format_timestamp(float(end if end is not None else start))
                else:
                    hit["begin_ts"] = hit.get("timestamp", "")
                    hit["end_ts"] = hit.get("timestamp", "")
        selected = list(self.hit_tree.selection()) if hasattr(self, "hit_tree") else []
        active = self.active_hit_index
        self._rebuild_tree()
        if selected and hasattr(self, "hit_tree"):
            keep = [iid for iid in selected if iid in self.hit_tree.get_children()]
            if keep:
                self.hit_tree.selection_set(keep)
        if active is not None:
            try:
                self._activate_hit(active)
            except Exception:
                pass
        self._write_preview_review_file()
        self._invalidate_preview()

    def _compute_preview_window(self, hit: dict) -> dict[str, float]:
        base_start = hit.get("detected_start")
        base_end = hit.get("detected_end")
        if base_start is None or base_end is None:
            ts = self._parse_timestamp_fallback(hit.get("timestamp", ""))
            if ts is None:
                raise RuntimeError("Ungültiger Zeitstempel im aktiven Treffer.")
            base_start = base_end = ts

        start_offset = float(hit.get("start_offset_ms", 0)) / 1000.0
        end_offset = float(hit.get("end_offset_ms", 0)) / 1000.0
        global_pre = max(0.0, float(self.bleep_pre_ms_var.get()) / 1000.0)
        global_post = max(0.0, float(self.bleep_post_ms_var.get()) / 1000.0)

        bleep_start = max(0.0, float(base_start) - global_pre + start_offset)
        bleep_end = max(
            bleep_start + 0.03,
            float(base_end) + global_post + end_offset,
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

    def _parse_timestamp_fallback(self, value: str):
        point = parse_time_point(value)
        return None if point is None else point.seconds

    def save_lists(self):
        bt = self._bleeping_bridge().sync_to_tab()
        if bt is None:
            return
        bt.save_lists()
        self._set_status("Projektlisten gespeichert.")

    def choose_candidate(self):
        bt = self._bleeping_bridge().sync_to_tab()
        if bt is None:
            return
        bt.choose_candidate()
        self._bleeping_bridge().sync_from_tab()
        self.refresh()

    def refresh(self):
        p = self._project()
        bt = self._bleeping_bridge().tab()
        if p is None or bt is None:
            return
        bt.refresh()
        self._bleeping_bridge().sync_from_tab()
        self.video_combo["values"] = _list_files(p.input_video_dir, VIDEO_EXTS)
        self.wav_combo["values"] = _list_files(p.transcription_wav_dir, {".wav"})
        self.json_combo["values"] = _list_files(p.transcription_json_dir, {".json"})
        self.candidate_combo["values"] = _list_files(p.candidates_raw_dir, {".txt"})
        self.media_map = self._preferred_review_media_map()
        self.words_map = self._available_words_json_paths()
        self.source_map = self._available_source_paths()
        self.media_combo["values"] = list(self.media_map.keys())
        default_medium = self._choose_default_review_medium()
        if default_medium:
            self.media_var.set(default_medium)
        self._pull_bleep_params_from_ffmpeg()
    def _build_hits_from_preview_rows(self, rows):
        return self._hit_list_helper().build_hits_from_preview_rows(rows)
    # Archiviert: frühere _rebuild_tree-Variante war weiter unten in derselben
    # Klasse vollständig überschrieben und wurde daher nie ausgeführt.
    def _refresh_hit_row(self, index: int):
        if 0 <= index < len(self.hits):
            hit = self.hits[index]
            iid = str(index)
            if iid in self.hit_tree.get_children():
                self.hit_tree.item(iid, values=(hit.get("line_number", index + 1), hit["begin_ts"], hit["end_ts"], hit["label"], hit["review_status"], hit.get("reason", "") or hit["source_decision"]))
    def evaluate_into_review(self):
        bt = self._bleeping_bridge().sync_to_tab()
        if bt is None:
            return
        self.save_lists()
        bt.evaluate()
        rows = bt._current_preview_rows()
        self.hits = self._build_hits_from_preview_rows(rows)
        default_medium = self._choose_default_review_medium()
        if default_medium:
            self.media_var.set(default_medium)
        self._resolve_hit_spans()
        self._recompute_all_hit_windows()
        visible = len(self.hit_tree.get_children())
        self._write_preview_review_file()
        self._set_status(f"Auswertung in neuen Prüfbereich geladen: {visible} Treffer sichtbar.")
    def _write_preview_review_file(self):
        p = self._project()
        if p is None or not self.candidate_var.get():
            return None
        stem = Path(self.candidate_var.get()).stem
        reviewed_path = p.candidates_reviewed_dir / f"{stem}.merged_preview.reviewed.txt"
        lines = []
        for hit in self.hits:
            lines.append(f"{hit['timestamp']} | {hit['label']} | {hit['review_status']} | {hit.get('reason', '')} | {hit.get('context', '')}")
        _safe_write_lines(reviewed_path, lines)
        return reviewed_path
    def add_selected_to_blocklist(self):
        selected = self.hit_tree.selection()
        if not selected:
            self._set_status("Keine Treffer markiert.")
            return
        existing = [x.strip() for x in self.block_text.get("1.0", "end").splitlines() if x.strip()]
        added = 0
        for iid in selected:
            try:
                index = int(iid)
            except Exception:
                continue
            if 0 <= index < len(self.hits):
                cand = str(self.hits[index].get("label", "")).strip()
                if cand and cand not in existing:
                    existing.append(cand)
                    added += 1
        self.block_text.delete("1.0", "end")
        self.block_text.insert("1.0", "\n".join(existing))
        self._sync_to_bleeping()
        self._set_status(f"Markierte Treffer in Blocklist übernommen: {added}")
    def add_selected_to_allowlist(self):
        selected = self.hit_tree.selection()
        if not selected:
            self._set_status("Keine Treffer markiert.")
            return
        existing = [x.strip() for x in self.allow_text.get("1.0", "end").splitlines() if x.strip()]
        added = 0
        for iid in selected:
            try:
                index = int(iid)
            except Exception:
                continue
            if 0 <= index < len(self.hits):
                cand = str(self.hits[index].get("label", "")).strip()
                if cand and cand not in existing:
                    existing.append(cand)
                    added += 1
        self.allow_text.delete("1.0", "end")
        self.allow_text.insert("1.0", "\n".join(existing))
        self._sync_to_bleeping()
        self._set_status(f"Markierte Treffer in Allowlist übernommen: {added}")
    def save_reviewed_and_times(self):
        self._sync_bleep_params()
        self._recompute_all_hit_windows()
        p = self._project()
        if p is None or not self.candidate_var.get():
            self._set_status("Bitte zuerst eine Kandidaten-Datei auswerten.")
            return
        stem = Path(self.candidate_var.get()).stem
        reviewed_path = p.candidates_reviewed_dir / f"{stem}.reviewed.txt"
        times_path = p.times_dir / f"{stem}.times.txt"
        reviewed_lines = []
        times_lines = []
        for hit in self.hits:
            reviewed_lines.append(f"{hit['timestamp']} | {hit['label']} | {hit['review_status']} | {hit.get('reason', '')} | {hit.get('context', '')}")
            if str(hit['review_status']).strip().lower() in {'bleepen', 'übernommen'}:
                times_lines.append(f"{hit['begin_ts']} --> {hit['end_ts']}")
        _safe_write_lines(reviewed_path, reviewed_lines)
        _write_range_times_lines(times_path, times_lines)
        self._set_status(f"Prüfstand gespeichert: {reviewed_path.name} | Times: {times_path.name}")

    def write_range_times_only(self):
        self._sync_bleep_params()
        self._recompute_all_hit_windows()
        p = self._project()
        if p is None or not self.candidate_var.get():
            self._set_status("Bitte zuerst eine Kandidaten-Datei auswerten.")
            return
        stem = Path(self.candidate_var.get()).stem
        times_path = p.times_dir / f"{stem}.times.txt"
        times_lines = [f"{hit['begin_ts']} --> {hit['end_ts']}" for hit in self.hits if str(hit['review_status']).strip().lower() in {'bleepen', 'übernommen'}]
        _write_range_times_lines(times_path, times_lines)
        self._set_status(f"Times-Datei mit Intervallen aktualisiert: {times_path.name}")

    def write_times_only(self):
        # Transitional compatibility wrapper: this review path still writes
        # range-based .times.txt files for the merged review workflow.
        self.write_range_times_only()

    def _load_preview_file(self, path: Path, kind: str, meta: dict[str, float], autoplay_from_ms: int | None = None):
        try:
            self.player.load(path)
            self._preview_meta = {**meta, "path": str(path), "kind": kind}
            self._update_position_label(0)
            self.player.play(from_ms=0 if autoplay_from_ms is None else autoplay_from_ms)
            label = "Prüfclip bereit." if kind == "beep" else "Originalclip bereit."
            self._set_status(label)
        except Exception as exc:
            self._set_status(f"Preview konnte nicht geladen werden: {exc}")
    def quick(self):
        bt = self._bleeping_bridge().sync_to_tab()
        if bt is None:
            return
        bt.quick()
        self._set_status("Schnell-Nachbleepen vorbereitet.")
    def _selected_indices(self) -> list[int]:
        return self._hit_list_helper().selected_indices()

    def _rebuild_tree(self):
        return self._hit_list_helper().rebuild_tree()
    def _set_active_status(self, new_status: str):
        indices = self._selected_indices()
        if not indices and self.active_hit_index is not None:
            indices = [self.active_hit_index]
        if not indices:
            self._set_status("Kein Treffer ausgewählt.")
            return
        changed = self._set_indices_status(indices, new_status)
        if changed:
            self._rebuild_tree()
            self._write_preview_review_file()
            label = "Bleepen" if new_status == "bleepen" else ("verworfen" if new_status == "verworfen" else "offen")
            self._set_status(f"{changed} Treffer auf {label} gesetzt.")
    def _set_selected_status(self, new_status: str):
        indices = self._selected_indices()
        if not indices:
            self._set_status("Keine Treffer markiert.")
            return
        changed = self._set_indices_status(indices, new_status)
        if changed:
            self._rebuild_tree()
            self._write_preview_review_file()
            label = "Bleepen" if new_status == "bleepen" else ("verworfen" if new_status == "verworfen" else "offen")
            self._set_status(f"{changed} markierte Treffer auf {label} gesetzt.")

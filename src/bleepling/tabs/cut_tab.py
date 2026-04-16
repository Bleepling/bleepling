from __future__ import annotations

import queue
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import ttk

try:
    import vlc  # type: ignore
except Exception:
    vlc = None

try:
    from PIL import Image, ImageTk  # type: ignore
except Exception:
    Image = None
    ImageTk = None

from bleepling.services.cut_service import CutService
from bleepling.utils.help_dialog import show_help_dialog
from bleepling.utils.file_types import VIDEO_EXTENSIONS


def _list_files(directory: Path, exts: set[str]):
    if not directory.exists():
        return []
    return sorted([p.name for p in directory.iterdir() if p.is_file() and p.suffix.lower() in exts], key=str.lower)


class CutWindow(tk.Toplevel):
    def __init__(self, master, tab: "CutTab"):
        super().__init__(master)
        self.tab = tab
        self.title("Schnittfenster")
        self.geometry("1700x1040")
        self.minsize(1360, 860)
        self.transient(master.winfo_toplevel())
        self.player_frame = None
        self.player_status_var = tk.StringVar(value="Bereit.")
        self._build()
        self.after(120, self._init_player)
        self.protocol("WM_DELETE_WINDOW", self._close)

    def _build(self):
        outer = ttk.Frame(self, padding=12)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=4)
        outer.columnconfigure(1, weight=2)
        outer.rowconfigure(1, weight=1)

        top = ttk.LabelFrame(outer, text="Arbeitsvideo und Zielordner", padding=10)
        top.grid(row=0, column=0, columnspan=2, sticky="ew")
        top.columnconfigure(1, weight=1)
        ttk.Label(top, text="Arbeitsvideo:").grid(row=0, column=0, sticky="w")
        ttk.Label(top, textvariable=self.tab.working_video_path_var, wraplength=1200).grid(row=0, column=1, sticky="w")
        ttk.Label(top, text="Clip-Zielordner:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Label(top, textvariable=self.tab.clip_output_dir_var, wraplength=1200).grid(row=1, column=1, sticky="w", pady=(6, 0))
        ttk.Button(top, text="?", width=3, command=self.tab.show_help_cutwindow_work, style="Accent.TButton").grid(row=0, column=2, rowspan=2, sticky="ne", padx=(0, 8), pady=(0, 0))

        left = ttk.LabelFrame(outer, text="Vorschau und Markensetzen", padding=10)
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=(10, 0))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)

        self.player_frame = tk.Frame(left, bg="black", height=620)
        self.player_frame.grid(row=0, column=0, sticky="nsew")
        self.player_frame.grid_propagate(False)

        seek_wrap = ttk.Frame(left)
        seek_wrap.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        seek_wrap.columnconfigure(0, weight=1)
        self.seek_scale = tk.Scale(
            seek_wrap,
            orient="horizontal",
            from_=0,
            to=1000,
            showvalue=False,
            variable=self.tab.seek_var,
            resolution=1,
            command=self._on_seek_command,
        )
        self.seek_scale.grid(row=0, column=0, sticky="ew")
        self.seek_scale.bind("<ButtonPress-1>", self._on_seek_press)
        self.seek_scale.bind("<ButtonRelease-1>", self._on_seek_release)

        transport = ttk.Frame(left)
        transport.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        for c in range(7):
            transport.columnconfigure(c, weight=1, uniform="transport")
        btnw = 15
        # Reihe 1
        ttk.Button(transport, text="Play", width=btnw, command=self.tab.player_play, style="Accent.TButton").grid(row=0, column=0, padx=3, pady=2, sticky="ew")
        ttk.Button(transport, text="Pause", width=btnw, command=self.tab.player_pause, style="Accent.TButton").grid(row=0, column=1, padx=3, pady=2, sticky="ew")
        ttk.Button(transport, text="Stopp", width=btnw, command=self.tab.player_stop, style="Accent.TButton").grid(row=0, column=2, padx=3, pady=2, sticky="ew")
        ttk.Button(transport, text="|< Anfang", width=btnw, command=self.tab.player_to_start, style="Accent.TButton").grid(row=0, column=3, padx=3, pady=2, sticky="ew")
        ttk.Button(transport, text="Ende >|", width=btnw, command=self.tab.player_to_end, style="Accent.TButton").grid(row=0, column=4, padx=3, pady=2, sticky="ew")
        ttk.Button(transport, text="Zur Startmarke", width=btnw, command=self.tab.player_to_start_mark, style="Accent.TButton").grid(row=0, column=5, padx=3, pady=2, sticky="ew")
        ttk.Button(transport, text="Zur Endmarke", width=btnw, command=self.tab.player_to_end_mark, style="Accent.TButton").grid(row=0, column=6, padx=3, pady=2, sticky="ew")
        # Reihe 2
        ttk.Button(transport, text="-100 ms", width=btnw, command=lambda: self.tab.player_seek_ms(-100), style="Accent.TButton").grid(row=1, column=0, padx=3, pady=2, sticky="ew")
        ttk.Button(transport, text="-50 ms", width=btnw, command=lambda: self.tab.player_seek_ms(-50), style="Accent.TButton").grid(row=1, column=1, padx=3, pady=2, sticky="ew")
        ttk.Button(transport, text="+50 ms", width=btnw, command=lambda: self.tab.player_seek_ms(50), style="Accent.TButton").grid(row=1, column=2, padx=3, pady=2, sticky="ew")
        ttk.Button(transport, text="+100 ms", width=btnw, command=lambda: self.tab.player_seek_ms(100), style="Accent.TButton").grid(row=1, column=3, padx=3, pady=2, sticky="ew")
        ttk.Button(transport, text="Startmarke setzen", width=btnw, command=self.tab.set_start_from_current_position, style="Accent.TButton").grid(row=1, column=4, padx=3, pady=2, sticky="ew")
        ttk.Button(transport, text="Endmarke setzen", width=btnw, command=self.tab.set_end_from_current_position, style="Accent.TButton").grid(row=1, column=5, padx=3, pady=2, sticky="ew")
        # Reihe 3
        ttk.Button(transport, text="-10 s", width=btnw, command=lambda: self.tab.player_seek_ms(-10000), style="Accent.TButton").grid(row=2, column=0, padx=3, pady=2, sticky="ew")
        ttk.Button(transport, text="-5 s", width=btnw, command=lambda: self.tab.player_seek_ms(-5000), style="Accent.TButton").grid(row=2, column=1, padx=3, pady=2, sticky="ew")
        ttk.Button(transport, text="+5 s", width=btnw, command=lambda: self.tab.player_seek_ms(5000), style="Accent.TButton").grid(row=2, column=2, padx=3, pady=2, sticky="ew")
        ttk.Button(transport, text="+10 s", width=btnw, command=lambda: self.tab.player_seek_ms(10000), style="Accent.TButton").grid(row=2, column=3, padx=3, pady=2, sticky="ew")
        ttk.Button(transport, text="Marken zurücksetzen", width=btnw, command=self.tab.reset_marks, style="Accent.TButton").grid(row=2, column=4, padx=3, pady=2, sticky="ew")
        ttk.Button(transport, text="Startmarke = Anfang", width=btnw, command=self.tab.set_start_to_absolute_start, style="Accent.TButton").grid(row=2, column=5, padx=3, pady=2, sticky="ew")
        ttk.Button(transport, text="Endmarke = Ende", width=btnw, command=self.tab.set_end_to_absolute_end, style="Accent.TButton").grid(row=2, column=6, padx=3, pady=2, sticky="ew")

        ttk.Button(left, text="?", width=3, command=self.tab.show_help_cutwindow_preview, style="Accent.TButton").grid(row=4, column=0, sticky="se", padx=(0, 8), pady=(8, 0))

        pos = ttk.LabelFrame(left, text="Position und Marken", padding=10)
        pos.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        ttk.Label(pos, text="Aktuelle Position").grid(row=0, column=0, sticky="w")
        ttk.Entry(pos, textvariable=self.tab.current_position_var, width=18).grid(row=0, column=1, sticky="w", padx=(8, 12))
        ttk.Label(pos, text="Startmarke").grid(row=0, column=2, sticky="w")
        ttk.Entry(pos, textvariable=self.tab.start_mark_var, width=18).grid(row=0, column=3, sticky="w", padx=(8, 12))
        ttk.Label(pos, text="Endmarke").grid(row=0, column=4, sticky="w")
        ttk.Entry(pos, textvariable=self.tab.end_mark_var, width=18).grid(row=0, column=5, sticky="w", padx=(8, 0))
        ttk.Label(pos, textvariable=self.player_status_var, wraplength=900, justify="left").grid(row=1, column=0, columnspan=6, sticky="w", pady=(8, 0))

        right = ttk.LabelFrame(outer, text="Aktueller Clip", padding=10)
        right.grid(row=1, column=1, sticky="nsew", pady=(10, 0))
        right.columnconfigure(1, weight=1)
        right.rowconfigure(4, weight=1)
        ttk.Label(right, text="Titel / Dateiname").grid(row=0, column=0, sticky="w")
        ttk.Entry(right, textvariable=self.tab.clip_title_var).grid(row=0, column=1, sticky="ew", padx=(8, 0))
        ttk.Button(right, text="Clip aus Marken anlegen", command=self.tab.add_clip, style="Accent.TButton").grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 4))
        ttk.Button(right, text="Clip aktualisieren", command=self.tab.update_clip, style="Accent.TButton").grid(row=2, column=0, columnspan=2, sticky="ew", pady=4)
        ttk.Button(right, text="Clip löschen", command=self.tab.delete_clip, style="Accent.TButton").grid(row=3, column=0, columnspan=2, sticky="ew", pady=4)
        self.hint_label = tk.Label(
            right,
            textvariable=self.tab.cut_window_hint_var,
            wraplength=420,
            justify="left",
            anchor="w",
            relief="flat",
            bd=0,
            padx=8,
            pady=6,
        )
        self.hint_label.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        self.tab.register_cut_window_hint_label(self.hint_label)
        ttk.Button(right, text="?", width=3, command=self.tab.show_help_cutwindow_clip, style="Accent.TButton").grid(row=5, column=1, sticky="se", padx=(0, 8), pady=(10, 0))

        bottom = ttk.Frame(outer)
        bottom.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ttk.Button(bottom, text="Schließen", command=self._close, style="Accent.TButton").pack(side="right")

    def _init_player(self):
        self.tab.attach_player_host(self.player_frame)
        self.tab.ensure_player_loaded()
        if vlc is None:
            self.player_status_var.set("python-vlc / VLC ist nicht verfügbar. Bitte im Reiter Einstellungen / Logs prüfen.")
            self.tab._set_cut_window_hint("python-vlc / VLC ist nicht verfügbar. Bitte im Reiter Einstellungen / Logs prüfen.", is_error=True)
        else:
            self.tab._set_cut_window_hint(
                "Interne Vorschau aktiv. Mit Regler, Sprüngen und Marken arbeitest du direkt auf dem Arbeitsvideo.",
                is_error=False,
            )
            self.player_status_var.set("Interne Vorschau aktiv. Mit Regler, Sprüngen und Marken arbeitest du direkt auf dem Arbeitsvideo.")

    def _on_seek_press(self, _event=None):
        self.tab.seek_dragging = True

    def _on_seek_release(self, _event=None):
        self.tab.seek_dragging = False
        self.tab.player_seek_to_ms(int(round(self.tab.seek_var.get())))

    def _on_seek_command(self, _value):
        if self.tab.seek_dragging:
            self.tab.current_position_var.set(self.tab.cut_service.seconds_to_ts(self.tab.seek_var.get() / 1000.0))

    def sync_ui(self):
        try:
            self.seek_scale.configure(to=max(self.tab.player_duration_ms, 1000))
        except Exception:
            pass

    def _close(self):
        self.tab.close_cut_window()
        self.destroy()


class CutTab(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.cut_service = CutService()
        self.source_items: list[str] = []
        self.clip_rows: list[dict] = []
        self.working_video_path: Path | None = None
        self.cut_window: CutWindow | None = None
        self.player_frame = None
        self.vlc_instance = None
        self.player = None
        self.player_loaded_path: Path | None = None
        self._poll_job = None
        self.seek_var = tk.DoubleVar(value=0.0)
        self.seek_dragging = False
        self.player_duration_ms = 0
        self._last_suggested_title = ""

        self.working_video_name_var = tk.StringVar(value="Noch kein Arbeitsvideo erzeugt.")
        self.working_video_path_var = tk.StringVar(value="-")
        self.working_video_dir_var = tk.StringVar(value="-")
        self.clip_output_dir_var = tk.StringVar(value="-")
        self.current_position_var = tk.StringVar(value="00:00:00.000")
        self.start_mark_var = tk.StringVar(value="00:00:00.000")
        self.end_mark_var = tk.StringVar(value="00:00:00.000")
        self.clip_title_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Bereit.")
        self.cut_window_hint_var = tk.StringVar(value="")
        self.cut_window_hint_label = None

        self.progress_win = None
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_text_var = tk.StringVar(value="0 %")
        self.progress_img = None
        self._progress_queue: queue.Queue = queue.Queue()
        self._build()



    def _show_help_dialog(self, title: str, body: str):
        show_help_dialog(self, title, body)

    def show_help_sources(self):
        self._show_help_dialog(
            "Hilfe – Quellvideos und Reihenfolge",
            "Hier stellst du die Quellvideos in die gewünschte Reihenfolge. "
            "Diese Reihenfolge ist die Grundlage für das spätere Arbeitsvideo.\n\n"
            "Üblicher Ablauf:\n"
            "1. Projektvideos hinzufügen\n"
            "2. Reihenfolge prüfen\n"
            "3. Danach das Arbeitsvideo bilden\n\n"
            "Achte darauf, dass du nur die Videos auswählst, die wirklich in denselben Arbeitsgang gehören."
        )

    def show_help_working_video(self):
        self._show_help_dialog(
            "Hilfe – Arbeitsvideo und Zielordner",
            "Hier erzeugst oder übernimmst du das Arbeitsvideo als Schnittgrundlage. "
            "Außerdem siehst du sofort, wo das Arbeitsvideo und die späteren Clips gespeichert werden.\n\n"
            "Die Buttons in diesem Bereich werden vor allem dann wichtig, wenn du mit mehreren Quellvideos, "
            "unterschiedlichen Reihenfolgen oder verschiedenen Arbeitsständen arbeitest. Dann kann es im Projekt "
            "mehrere passende Arbeitsvideos geben.\n\n"
            "Üblicher Ablauf:\n"
            "1. Quellvideos festlegen\n"
            "2. Arbeitsvideo aus Auswahl bilden\n"
            "3. Nur bei Bedarf ein vorhandenes Arbeitsvideo wählen oder das Arbeitsvideo erneut bilden\n"
            "4. Danach das Schnittfenster öffnen\n\n"
            "Wenn bereits ein passendes Arbeitsvideo vorhanden ist, kann es wiederverwendet werden. "
            "Das ist besonders hilfreich, wenn du später im selben Projekt eine andere Videozusammenstellung "
            "oder einen früheren Arbeitsstand weiterbearbeiten möchtest."
        )

    def show_help_marks_main(self):
        self._show_help_dialog(
            "Hilfe – Vorschau, Position und Marken",
            "Dieser Bereich zeigt die aktuellen Positions- und Markenwerte zusätzlich im Hauptreiter. "
            "Das präzise Setzen der Marken erfolgt im Schnittfenster.\n\n"
            "Üblicher Ablauf:\n"
            "1. Schnittfenster öffnen\n"
            "2. Start- und Endmarke dort setzen\n"
            "3. Werte hier kontrollieren\n\n"
            "Die Anzeige hier ist vor allem zur Kontrolle und für schnelle Nachjustierungen gedacht."
        )

    def show_help_clip_main(self):
        self._show_help_dialog(
            "Hilfe – Clip anlegen und benennen",
            "Hier gibst du dem Clip seinen Namen und legst ihn aus Start- und Endmarke an. "
            "Bestehende Clip-Einträge können auch aktualisiert oder gelöscht werden.\n\n"
            "Üblicher Ablauf:\n"
            "1. Marken setzen\n"
            "2. Titel prüfen oder anpassen\n"
            "3. Clip anlegen\n"
            "4. Bei Bedarf später aktualisieren oder löschen"
        )

    def show_help_clip_list(self):
        self._show_help_dialog(
            "Hilfe – Clip-Liste und Erzeugung",
            "Hier siehst du alle im aktuellen Arbeitsgang definierten Clips. "
            "Von hier aus kannst du einzelne oder alle Clips als echte Videodateien erzeugen.\n\n"
            "Üblicher Ablauf:\n"
            "1. Clips anlegen\n"
            "2. Einträge in der Liste kontrollieren\n"
            "3. Ausgewählten Clip oder alle Clips erzeugen\n\n"
            "Die erzeugten Clips landen im Clip-Zielordner des Projekts."
        )

    def show_help_cutwindow_work(self):
        self._show_help_dialog(
            "Hilfe – Arbeitsvideo und Zielordner",
            "Oben siehst du, mit welchem Arbeitsvideo du gerade arbeitest und in welchen Ordner die fertigen Clips geschrieben werden.\n\n"
            "Das Schnittfenster bezieht sich immer auf dieses Arbeitsvideo."
        )

    def show_help_cutwindow_preview(self):
        self._show_help_dialog(
            "Hilfe – Vorschau und Markensetzen",
            "Hier erfolgt das präzise Arbeiten am Arbeitsvideo. "
            "Mit Regler, Sprüngen und den Buttons zum Setzen der Marken bestimmst du den Clipbereich.\n\n"
            "Üblicher Ablauf:\n"
            "1. Zur gewünschten Stelle navigieren\n"
            "2. Startmarke setzen\n"
            "3. Zur Endstelle navigieren\n"
            "4. Endmarke setzen\n"
            "5. Danach rechts den Clip anlegen"
        )

    def show_help_cutwindow_clip(self):
        self._show_help_dialog(
            "Hilfe – Aktueller Clip",
            "Rechts benennst du den aktuellen Clip und legst ihn aus den gesetzten Marken an. "
            "Außerdem kannst du vorhandene Clip-Einträge aktualisieren oder löschen.\n\n"
            "Wenn ein sinnvoller Dateiname vorgeschlagen wird, kannst du ihn übernehmen oder anpassen."
        )
    def _asset(self, name: str) -> Path:
        return Path(__file__).resolve().parents[3] / "assets" / name

    def _project(self):
        return getattr(self.app, "project", None)

    def _set_status(self, msg: str):
        self.status_var.set(msg)
        try:
            self.app.set_status(msg)
        except Exception:
            pass

    def _make_bold_labelframe(self, parent, title: str):
        lbl = tk.Label(parent, text=title, font=("Segoe UI", 10, "bold"))
        return ttk.LabelFrame(parent, labelwidget=lbl)

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        top = ttk.Frame(self)
        top.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        top.columnconfigure(0, weight=24)
        top.columnconfigure(1, weight=26)

        src_box = self._make_bold_labelframe(top, "1) Quellvideos und Reihenfolge")
        src_box.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        src_box.columnconfigure(0, weight=1)
        src_box.rowconfigure(0, weight=1)
        self.source_list = tk.Listbox(src_box, height=8, exportselection=False)
        self.source_list.grid(row=0, column=0, rowspan=5, sticky="nsew", padx=(8, 6), pady=8)
        ttk.Button(src_box, text="Video hinzufügen", command=self.add_source_video, style="Accent.TButton").grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=(8, 4))
        ttk.Button(src_box, text="?", width=3, command=self.show_help_sources, style="Accent.TButton").grid(row=0, column=2, sticky="e", padx=(0, 8), pady=(8, 4))
        ttk.Button(src_box, text="Entfernen", command=self.remove_source_video, style="Accent.TButton").grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=4)
        ttk.Button(src_box, text="Nach oben", command=lambda: self.move_source(-1), style="Accent.TButton").grid(row=2, column=1, sticky="ew", padx=(0, 8), pady=4)
        ttk.Button(src_box, text="Nach unten", command=lambda: self.move_source(1), style="Accent.TButton").grid(row=3, column=1, sticky="ew", padx=(0, 8), pady=4)
        ttk.Button(src_box, text="Quellvideo-Ordner öffnen", command=self.open_source_video_dir, style="Accent.TButton").grid(row=4, column=1, sticky="ew", padx=(0, 8), pady=(4, 8))

        work_box = self._make_bold_labelframe(top, "2) Arbeitsvideo und Zielordner")
        work_box.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        work_box.columnconfigure(1, weight=1)
        ttk.Label(work_box, text="Arbeitsvideo").grid(row=0, column=0, sticky="w", padx=8, pady=(8, 4))
        ttk.Label(work_box, textvariable=self.working_video_name_var).grid(row=0, column=1, sticky="w", padx=(0, 8), pady=(8, 4))
        ttk.Label(work_box, text="Arbeitsvideo-Pfad").grid(row=1, column=0, sticky="nw", padx=8, pady=4)
        ttk.Label(work_box, textvariable=self.working_video_path_var, wraplength=680, justify="left").grid(row=1, column=1, sticky="w", padx=(0, 8), pady=4)
        ttk.Label(work_box, text="Arbeitsvideo-Ordner").grid(row=2, column=0, sticky="nw", padx=8, pady=4)
        ttk.Label(work_box, textvariable=self.working_video_dir_var, wraplength=680, justify="left").grid(row=2, column=1, sticky="w", padx=(0, 8), pady=4)
        ttk.Label(work_box, text="Clip-Zielordner").grid(row=3, column=0, sticky="nw", padx=8, pady=4)
        ttk.Label(work_box, textvariable=self.clip_output_dir_var, wraplength=680, justify="left").grid(row=3, column=1, sticky="w", padx=(0, 8), pady=4)
        ttk.Button(work_box, text="?", width=3, command=self.show_help_working_video, style="Accent.TButton").grid(row=0, column=2, rowspan=4, sticky="ne", padx=(0, 8), pady=(8, 0))
        btnrow = ttk.Frame(work_box)
        btnrow.grid(row=4, column=0, columnspan=2, sticky="ew", padx=8, pady=(8, 8))
        ttk.Button(btnrow, text="Arbeitsvideo aus Auswahl bilden", command=self.build_working_video, style="Accent.TButton").pack(side="left")
        ttk.Button(btnrow, text="Arbeitsvideo aus Auswahl erneut bilden", command=self.rebuild_working_video, style="Accent.TButton").pack(side="left", padx=6)
        ttk.Button(btnrow, text="Vorhandenes Arbeitsvideo wählen", command=self.choose_existing_working_video, style="Accent.TButton").pack(side="left")
        ttk.Button(btnrow, text="Schnittfenster öffnen", command=self.open_cut_window, style="Accent.TButton").pack(side="left", padx=6)
        ttk.Button(btnrow, text="Arbeitsvideo öffnen", command=self.open_working_video, style="Accent.TButton").pack(side="left")
        ttk.Button(btnrow, text="Arbeitsvideo-Ordner öffnen", command=self.open_working_video_dir, style="Accent.TButton").pack(side="left", padx=6)
        ttk.Button(btnrow, text="Clip-Ordner öffnen", command=self.open_clip_output_dir, style="Accent.TButton").pack(side="left")

        middle = ttk.Frame(self)
        middle.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        middle.columnconfigure(0, weight=3)
        middle.columnconfigure(1, weight=2)
        middle.rowconfigure(0, weight=1)

        marks_box = self._make_bold_labelframe(middle, "3) Vorschau, Position und Marken")
        marks_box.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        marks_box.columnconfigure(1, weight=1)
        ttk.Label(marks_box, text="Aktuelle Position").grid(row=0, column=0, sticky="w", padx=8, pady=(8, 4))
        ttk.Entry(marks_box, textvariable=self.current_position_var, width=18).grid(row=0, column=1, sticky="w", padx=(0, 8), pady=(8, 4))
        ttk.Button(marks_box, text="Startmarke aus Position", command=self.set_start_from_current_position, style="Accent.TButton").grid(row=0, column=2, sticky="w", padx=(0, 8), pady=(8, 4))
        ttk.Button(marks_box, text="Endmarke aus Position", command=self.set_end_from_current_position, style="Accent.TButton").grid(row=0, column=3, sticky="w", padx=(0, 8), pady=(8, 4))
        ttk.Label(marks_box, text="Startmarke").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        ttk.Entry(marks_box, textvariable=self.start_mark_var, width=18).grid(row=1, column=1, sticky="w", padx=(0, 8), pady=4)
        ttk.Label(marks_box, text="Endmarke").grid(row=1, column=2, sticky="w", padx=(0, 8), pady=4)
        ttk.Entry(marks_box, textvariable=self.end_mark_var, width=18).grid(row=1, column=3, sticky="w", padx=(0, 8), pady=4)
        ttk.Label(marks_box, text="Hinweis: Präzises Markensetzen erfolgt direkt im Schnittfenster; hier siehst und bearbeitest du die Werte zusätzlich im Hauptreiter.", wraplength=760, justify="left").grid(row=2, column=0, columnspan=4, sticky="w", padx=8, pady=(8, 8))
        ttk.Button(marks_box, text="?", width=3, command=self.show_help_marks_main, style="Accent.TButton").grid(row=3, column=3, sticky="se", padx=(0, 8), pady=(0, 8))

        clip_box = self._make_bold_labelframe(middle, "4) Clip anlegen und benennen")
        clip_box.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        clip_box.columnconfigure(1, weight=1)
        ttk.Label(clip_box, text="Aktuelle Position").grid(row=0, column=0, sticky="w", padx=8, pady=(8, 4))
        ttk.Entry(clip_box, textvariable=self.current_position_var, width=18).grid(row=0, column=1, sticky="w", padx=(0, 8), pady=(8, 4))
        ttk.Label(clip_box, text="Startmarke").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        ttk.Entry(clip_box, textvariable=self.start_mark_var, width=18).grid(row=1, column=1, sticky="w", padx=(0, 8), pady=4)
        ttk.Label(clip_box, text="Endmarke").grid(row=2, column=0, sticky="w", padx=8, pady=4)
        ttk.Entry(clip_box, textvariable=self.end_mark_var, width=18).grid(row=2, column=1, sticky="w", padx=(0, 8), pady=4)
        ttk.Label(clip_box, text="Titel / Dateiname").grid(row=3, column=0, sticky="w", padx=8, pady=(10, 4))
        ttk.Entry(clip_box, textvariable=self.clip_title_var).grid(row=3, column=1, sticky="ew", padx=(0, 8), pady=(10, 4))
        ttk.Button(clip_box, text="Clip aus Marken anlegen", command=self.add_clip, style="Accent.TButton").grid(row=4, column=0, columnspan=2, sticky="ew", padx=8, pady=4)
        ttk.Button(clip_box, text="Clip aktualisieren", command=self.update_clip, style="Accent.TButton").grid(row=5, column=0, columnspan=2, sticky="ew", padx=8, pady=4)
        ttk.Button(clip_box, text="Clip löschen", command=self.delete_clip, style="Accent.TButton").grid(row=6, column=0, columnspan=2, sticky="ew", padx=8, pady=4)
        ttk.Button(clip_box, text="Schnittfenster öffnen", command=self.open_cut_window, style="Accent.TButton").grid(row=7, column=0, columnspan=2, sticky="ew", padx=8, pady=4)
        ttk.Button(clip_box, text="?", width=3, command=self.show_help_clip_main, style="Accent.TButton").grid(row=8, column=1, sticky="se", padx=(0, 8), pady=(8, 8))

        bottom = ttk.Frame(self)
        bottom.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 8))
        bottom.columnconfigure(0, weight=1)
        bottom.rowconfigure(0, weight=1)

        list_box = self._make_bold_labelframe(bottom, "5) Clip-Liste und Erzeugung")
        list_box.grid(row=0, column=0, sticky="nsew")
        list_box.columnconfigure(0, weight=1)
        list_box.rowconfigure(0, weight=1)
        self.clip_tree = ttk.Treeview(list_box, columns=("nr", "beginn", "ende", "titel"), show="headings", height=10)
        for col, text, width in [("nr", "#", 48), ("beginn", "Beginn", 110), ("ende", "Ende", 110), ("titel", "Titel / Dateiname", 420)]:
            self.clip_tree.heading(col, text=text)
            self.clip_tree.column(col, width=width, anchor="w", stretch=(col == "titel"))
        self.clip_tree.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=8)
        self.clip_tree.bind("<<TreeviewSelect>>", self._on_clip_selected)
        scroll = ttk.Scrollbar(list_box, orient="vertical", command=self.clip_tree.yview)
        scroll.grid(row=0, column=1, sticky="ns", padx=(0, 8), pady=8)
        self.clip_tree.configure(yscrollcommand=scroll.set)
        actions = ttk.Frame(list_box)
        actions.grid(row=1, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 8))
        ttk.Button(actions, text="Ausgewählten Clip erzeugen", command=self.create_selected_clip, style="Accent.TButton").pack(side="left")
        ttk.Button(actions, text="Alle Clips erzeugen", command=self.create_all_clips, style="Accent.TButton").pack(side="left", padx=6)
        ttk.Button(actions, text="Clip-Ordner öffnen", command=self.open_clip_output_dir, style="Accent.TButton").pack(side="left")
        ttk.Button(actions, text="?", width=3, command=self.show_help_clip_list, style="Accent.TButton").pack(side="left", padx=6)
        ttk.Label(actions, textvariable=self.status_var, wraplength=900, justify="left").pack(side="right")

    def register_cut_window_hint_label(self, label):
        self.cut_window_hint_label = label
        self._set_cut_window_hint(self.cut_window_hint_var.get() or "", is_error=False)

    def _set_cut_window_hint(self, message: str, is_error: bool = False):
        self.cut_window_hint_var.set(message)
        label = self.cut_window_hint_label
        if label is None:
            return
        try:
            if is_error and message:
                label.configure(
                    fg="#a40000",
                    bg="#fff2f2",
                    highlightbackground="#c62828",
                    highlightcolor="#c62828",
                    highlightthickness=1,
                    font=("Segoe UI", 9, "bold"),
                )
            else:
                label.configure(
                    fg="black",
                    bg=self.cget("background"),
                    highlightthickness=0,
                    font=("Segoe UI", 9),
                )
        except Exception:
            pass

    def refresh(self):
        p = self._project()
        if not p:
            return
        self.working_video_dir_var.set(str(self.cut_service.working_video_dir(p)))
        self.clip_output_dir_var.set(str(self.cut_service.clips_output_dir(p)))
        self._try_load_existing_working_video()
        if self._should_poll_player() and self.player_loaded_path is not None and self._poll_job is None:
            self._poll_position()
        self._set_status("Bereit.")

    def _project_videos(self) -> list[str]:
        p = self._project()
        if not p:
            return []
        return _list_files(p.input_video_dir, VIDEO_EXTENSIONS)

    def _maybe_update_suggested_title(self, force: bool = False):
        current = (self.clip_title_var.get() or "").strip()
        if force or not current or current == self._last_suggested_title:
            suggested = self._suggest_clip_title()
            self._last_suggested_title = suggested
            self.clip_title_var.set(suggested)

    def _base_clip_name(self) -> str:
        base = "clip"
        if self.working_video_path:
            stem = self.working_video_path.stem
            for suffix in ("_arbeitsvideo", "_working_video", "_working"):
                if stem.lower().endswith(suffix):
                    stem = stem[: -len(suffix)]
                    break
            base = self.cut_service.sanitize_filename(stem, "clip")
        return base

    def _existing_clip_titles(self, exclude_index: int | None = None) -> set[str]:
        titles: set[str] = set()
        for idx, row in enumerate(self.clip_rows):
            if exclude_index is not None and idx == exclude_index:
                continue
            title = (row.get("title") or "").strip()
            if title:
                titles.add(title.lower())
        p = self._project()
        if p:
            clip_dir = self.cut_service.clips_output_dir(p)
            if clip_dir.exists():
                for f in clip_dir.iterdir():
                    if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS:
                        titles.add(f.stem.strip().lower())
        return titles

    def _suggest_clip_title(self) -> str:
        base = self._base_clip_name()
        existing = self._existing_clip_titles()
        idx = 1
        while True:
            candidate = f"{base}_clip_{idx:02d}"
            if candidate.lower() not in existing:
                return candidate
            idx += 1

    def add_source_video(self):
        p = self._project()
        if not p:
            self._set_status("Bitte zuerst ein Projekt laden.")
            return
        available = [n for n in self._project_videos() if n not in self.source_items]
        if not available:
            self._set_status("Keine weiteren Projektvideos zum Hinzufügen verfügbar.")
            return
        win = tk.Toplevel(self)
        win.title("Projektvideo hinzufügen")
        win.transient(self.winfo_toplevel())
        frame = ttk.Frame(win, padding=12)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Projektvideos auswählen").pack(anchor="w")
        lb = tk.Listbox(frame, selectmode="extended", width=72, height=14, exportselection=False)
        lb.pack(fill="both", expand=True, pady=(8, 8))
        for name in available:
            lb.insert("end", name)

        def accept():
            picked = [available[i] for i in lb.curselection()]
            if not picked:
                return
            self.source_items.extend(picked)
            self._refresh_source_list()
            self._set_status(f"Quellvideos ergänzt: {', '.join(picked)}")
            win.destroy()

        btns = ttk.Frame(frame)
        btns.pack(fill="x")
        ttk.Button(btns, text="Übernehmen", command=accept, style="Accent.TButton").pack(side="right")
        ttk.Button(btns, text="Abbrechen", command=win.destroy, style="Accent.TButton").pack(side="right", padx=(0, 6))

    def remove_source_video(self):
        sel = self.source_list.curselection()
        if not sel:
            self._set_status("Kein Quellvideo ausgewählt.")
            return
        idx = sel[0]
        removed = self.source_items.pop(idx)
        self._refresh_source_list()
        self._set_status(f"Quellvideo entfernt: {removed}")

    def move_source(self, delta: int):
        sel = self.source_list.curselection()
        if not sel:
            self._set_status("Kein Quellvideo ausgewählt.")
            return
        idx = sel[0]
        new = idx + delta
        if new < 0 or new >= len(self.source_items):
            return
        self.source_items[idx], self.source_items[new] = self.source_items[new], self.source_items[idx]
        self._refresh_source_list(select_index=new)

    def _refresh_source_list(self, select_index: int | None = None):
        self.source_list.delete(0, "end")
        for name in self.source_items:
            self.source_list.insert("end", name)
        if select_index is not None and 0 <= select_index < len(self.source_items):
            self.source_list.selection_set(select_index)
            self.source_list.activate(select_index)
        self._try_load_existing_working_video()
        self._maybe_update_suggested_title(force=True)

    def _set_working_video(self, path: Path | None, note: str | None = None):
        self.working_video_path = path if path and path.exists() else None
        if self.working_video_path:
            self.working_video_name_var.set(self.working_video_path.name)
            self.working_video_path_var.set(str(self.working_video_path))
            self.working_video_dir_var.set(str(self.working_video_path.parent))
            self.player_loaded_path = None
            self._maybe_update_suggested_title(force=True)
            if note:
                self._set_status(note)
        else:
            self.working_video_name_var.set("Noch kein Arbeitsvideo erzeugt.")
            self.working_video_path_var.set("-")
            p = self._project()
            self.working_video_dir_var.set(str(self.cut_service.working_video_dir(p)) if p else "-")

    def _try_load_existing_working_video(self):
        p = self._project()
        if not p or not self.source_items:
            if not self.source_items:
                self._set_working_video(None)
            return
        source_files = [p.input_video_dir / name for name in self.source_items]
        match = self.cut_service.find_matching_working_video(p, source_files)
        if match:
            self._set_working_video(match)
        elif self.working_video_path and not self.working_video_path.exists():
            self._set_working_video(None)

    def choose_existing_working_video(self):
        p = self._project()
        if not p:
            self._set_status("Bitte zuerst ein Projekt laden.")
            return
        available = self.cut_service.list_working_videos(p)
        if not available:
            self._set_status("Keine vorhandenen Arbeitsvideos gefunden.")
            return
        win = tk.Toplevel(self)
        win.title("Vorhandenes Arbeitsvideo wählen")
        win.transient(self.winfo_toplevel())
        frame = ttk.Frame(win, padding=12)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Vorhandene Arbeitsvideos auswählen").pack(anchor="w")
        lb = tk.Listbox(frame, selectmode="browse", width=72, height=12, exportselection=False)
        lb.pack(fill="both", expand=True, pady=(8, 8))
        for path in available:
            lb.insert("end", path.name)

        def accept():
            sel = lb.curselection()
            if not sel:
                return
            picked = available[sel[0]]
            self._set_working_video(picked, f"Vorhandenes Arbeitsvideo übernommen: {picked}")
            win.destroy()

        btns = ttk.Frame(frame)
        btns.pack(fill="x")
        ttk.Button(btns, text="Übernehmen", command=accept, style="Accent.TButton").pack(side="right")
        ttk.Button(btns, text="Abbrechen", command=win.destroy, style="Accent.TButton").pack(side="right", padx=(0, 6))

    def rebuild_working_video(self):
        self.build_working_video(force=True)

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
        bar = ttk.Progressbar(frame, maximum=100, mode="indeterminate", length=360)
        bar.pack(pady=(0, 6))
        bar.start(10)
        self.progress_bar = bar
        ttk.Button(frame, text="Rendern abbrechen", command=lambda: None, style="Accent.TButton").pack(pady=(12, 0))
        win.update_idletasks()
        root = self.winfo_toplevel()
        rx, ry, rw, rh = root.winfo_rootx(), root.winfo_rooty(), root.winfo_width(), root.winfo_height()
        ww, wh = win.winfo_width(), win.winfo_height()
        win.geometry(f"+{rx + max(0, (rw-ww)//2)}+{ry + max(0, (rh-wh)//2)}")
        self.progress_win = win

    def _hide_progress_window(self):
        try:
            if self.progress_bar is not None:
                self.progress_bar.stop()
        except Exception:
            pass
        try:
            if self.progress_win is not None:
                self.progress_win.destroy()
        except Exception:
            pass
        self.progress_win = None
        self.progress_bar = None

    def _poll_progress_queue(self):
        try:
            while True:
                item = self._progress_queue.get_nowait()
                kind = item.get("kind")
                if kind == "done":
                    self._hide_progress_window()
                    target = item.get("target")
                    if target:
                        self._set_working_video(Path(target), f"Arbeitsvideo gespeichert: {target}")
                    else:
                        self._set_status(item.get("message", "Arbeitsvideo erstellt."))
                    return
                if kind == "done_selected_clip":
                    self._hide_progress_window()
                    out = item.get("target")
                    if out:
                        self._set_status(f"Clip gespeichert: {out}")
                    else:
                        self._set_status(item.get("message", "Clip gespeichert."))
                    self._refresh_other_tabs()
                    return
                if kind == "done_all_clips":
                    self._hide_progress_window()
                    self._set_status(item.get("message", "Alle Clips gespeichert."))
                    self._refresh_other_tabs()
                    return
                if kind == "error":
                    self._hide_progress_window()
                    self._set_status(item.get("message", "Arbeitsvideo konnte nicht erzeugt werden."))
                    return
        except queue.Empty:
            pass
        if self.progress_win is not None:
            self.after(150, self._poll_progress_queue)

    def build_working_video(self, force: bool = False):
        p = self._project()
        if not p:
            self._set_status("Bitte zuerst ein Projekt laden.")
            return
        if not self.source_items:
            self._set_status("Bitte zuerst Quellvideos auswählen.")
            return
        paths = [p.input_video_dir / name for name in self.source_items]
        if not force:
            existing = self.cut_service.find_matching_working_video(p, paths)
            if existing:
                self._set_working_video(existing, f"Vorhandenes Arbeitsvideo erkannt: {existing}")
                return
        self._show_progress_window()

        def worker():
            try:
                target = self.cut_service.build_working_video(p, paths)
                self._progress_queue.put({"kind": "done", "target": str(target)})
            except Exception as exc:
                self._progress_queue.put({"kind": "error", "message": str(exc)})

        threading.Thread(target=worker, daemon=True).start()
        self.after(150, self._poll_progress_queue)

    def open_source_video_dir(self):
        p = self._project()
        if not p:
            return
        try:
            self.cut_service.open_in_system(p.input_video_dir)
            self._set_status(f"Quellvideo-Ordner geöffnet: {p.input_video_dir}")
        except Exception as exc:
            self._set_status(str(exc))

    def open_working_video_dir(self):
        p = self._project()
        if not p:
            return
        try:
            target = self.cut_service.working_video_dir(p)
            self.cut_service.open_in_system(target)
            self._set_status(f"Arbeitsvideo-Ordner geöffnet: {target}")
        except Exception as exc:
            self._set_status(str(exc))

    def open_clip_output_dir(self):
        p = self._project()
        if not p:
            return
        try:
            target = self.cut_service.clips_output_dir(p)
            self.cut_service.open_in_system(target)
            self._set_status(f"Clip-Zielordner geöffnet: {target}")
        except Exception as exc:
            self._set_status(str(exc))

    def open_working_video(self):
        if not self.working_video_path or not self.working_video_path.exists():
            self._set_status("Es ist noch kein Arbeitsvideo vorhanden.")
            return
        try:
            self.cut_service.open_in_system(self.working_video_path)
            self._set_status(f"Arbeitsvideo geöffnet: {self.working_video_path}")
        except Exception as exc:
            self._set_status(str(exc))

    def open_cut_window(self):
        if not self.working_video_path or not self.working_video_path.exists():
            self._set_status("Bitte zuerst ein Arbeitsvideo erzeugen.")
            return
        if self.cut_window and self.cut_window.winfo_exists():
            self.cut_window.lift()
            self.cut_window.focus_set()
            return
        self.cut_window = CutWindow(self, self)

    def attach_player_host(self, host):
        self.player_frame = host
        if vlc is None:
            return
        try:
            if self.vlc_instance is None:
                self.vlc_instance = vlc.Instance("--no-video-title-show")
            if self.player is None:
                self.player = self.vlc_instance.media_player_new()
            host.update_idletasks()
            wid = host.winfo_id()
            if hasattr(self.player, "set_hwnd"):
                self.player.set_hwnd(wid)
            elif hasattr(self.player, "set_xwindow"):
                self.player.set_xwindow(wid)
            elif hasattr(self.player, "set_nsobject"):
                self.player.set_nsobject(wid)
        except Exception as exc:
            self._set_status(f"VLC-Player konnte nicht eingebunden werden: {exc}")

    def close_cut_window(self):
        try:
            if self._poll_job is not None:
                self.after_cancel(self._poll_job)
                self._poll_job = None
        except Exception:
            self._poll_job = None
        try:
            if self.player is not None:
                self.player.stop()
                try:
                    self.player.set_pause(1)
                except Exception:
                    pass
                try:
                    self.player.set_media(None)
                except Exception:
                    pass
        except Exception:
            pass
        self.player_loaded_path = None
        self.player_frame = None
        self.seek_dragging = False
        self.current_position_var.set("00:00:00.000")
        self.seek_var.set(0.0)

    def detach_player_host(self):
        self.player_frame = None

    def ensure_player_loaded(self):
        if vlc is None:
            return
        if not self.working_video_path or not self.working_video_path.exists():
            return
        if self.player is None:
            self.attach_player_host(self.player_frame)
        if self.player is None:
            return
        if self.player_loaded_path == self.working_video_path:
            return
        media = self.vlc_instance.media_new(str(self.working_video_path))
        self.player.set_media(media)
        self.player_loaded_path = self.working_video_path
        self.player.stop()
        self.current_position_var.set("00:00:00.000")
        duration = self.cut_service.probe_duration(self.working_video_path) or 0.0
        self.player_duration_ms = int(round(duration * 1000))
        self.seek_var.set(0.0)
        if self._poll_job is None and self._should_poll_player():
            self._poll_position()
        self._redraw_cut_window()

    def _should_poll_player(self) -> bool:
        if self.player is None or self.player_loaded_path is None:
            return False
        try:
            if self.cut_window is not None and self.cut_window.winfo_exists():
                return True
        except Exception:
            pass
        try:
            notebook = getattr(self.app, "notebook", None)
            if notebook is not None:
                selected = self.nametowidget(notebook.select())
                if selected is self:
                    return True
        except Exception:
            pass
        return False

    def _poll_position(self):
        self._poll_job = None
        if not self._should_poll_player():
            return
        try:
            if self.player is not None:
                ms = int(self.player.get_time())
                if ms >= 0:
                    self.current_position_var.set(self.cut_service.seconds_to_ts(ms / 1000.0))
                    if not self.seek_dragging:
                        self.seek_var.set(ms)
                length = int(self.player.get_length())
                if length > 0:
                    self.player_duration_ms = length
        except Exception:
            pass
        self._redraw_cut_window()
        self._poll_job = self.after(100, self._poll_position)

    def _sync_player_time(self):
        try:
            ms = int(round(self.cut_service.ts_to_seconds(self.current_position_var.get()) * 1000))
        except Exception:
            ms = 0
        if ms < 0:
            ms = 0
        if self.player_duration_ms > 0 and ms > self.player_duration_ms:
            ms = self.player_duration_ms
        self.seek_var.set(ms)
        return ms

    def _player_state_name(self):
        try:
            if self.player is None or vlc is None:
                return None
            state = self.player.get_state()
            return str(state)
        except Exception:
            return None

    def _revive_player_after_end(self):
        try:
            if self.player is None or vlc is None:
                return
            name = (self._player_state_name() or '').lower()
            if 'ended' in name:
                self.player.stop()
                self.player.play()
                time.sleep(0.08)
                self.player.pause()
                time.sleep(0.03)
        except Exception:
            pass

    def player_seek_to_ms(self, ms: int):
        self.ensure_player_loaded()
        try:
            target = max(0, int(ms))
            if self.player_duration_ms > 0 and target > self.player_duration_ms:
                target = self.player_duration_ms
            self._revive_player_after_end()
            if self.player is not None:
                seek_target = target
                if self.player_duration_ms > 0 and target >= self.player_duration_ms:
                    seek_target = max(self.player_duration_ms - 80, 0)
                self.player.set_time(seek_target)
            self.current_position_var.set(self.cut_service.seconds_to_ts(target / 1000.0))
            self.seek_var.set(target)
        except Exception as exc:
            self._set_status(str(exc))
        self._redraw_cut_window()

    def player_play(self):
        self.ensure_player_loaded()
        try:
            ms = self._sync_player_time()
            self._revive_player_after_end()
            if self.player is not None:
                seek_target = ms
                if self.player_duration_ms > 0 and ms >= self.player_duration_ms:
                    seek_target = max(self.player_duration_ms - 80, 0)
                self.player.set_time(seek_target)
                self.player.play()
        except Exception as exc:
            self._set_status(str(exc))

    def player_pause(self):
        try:
            if self.player is not None:
                self.player.pause()
        except Exception as exc:
            self._set_status(str(exc))

    def player_stop(self):
        try:
            if self.player is not None:
                self.player.stop()
            self.current_position_var.set("00:00:00.000")
            self.seek_var.set(0.0)
        except Exception as exc:
            self._set_status(str(exc))
        self._redraw_cut_window()

    def player_seek_ms(self, delta_ms: int):
        self.player_seek_to_ms(self._sync_player_time() + int(delta_ms))

    def player_to_start(self):
        self.player_seek_to_ms(0)

    def player_to_end(self):
        if self.player_duration_ms > 0:
            self.player_seek_to_ms(max(self.player_duration_ms - 80, 0))
        else:
            self.player_seek_to_ms(self.player_duration_ms)

    def player_to_start_mark(self):
        try:
            ms = int(round(self.cut_service.ts_to_seconds(self.start_mark_var.get()) * 1000))
        except Exception:
            ms = 0
        self.player_seek_to_ms(ms)

    def player_to_end_mark(self):
        try:
            ms = int(round(self.cut_service.ts_to_seconds(self.end_mark_var.get()) * 1000))
        except Exception:
            ms = 0
        self.player_seek_to_ms(ms)

    def set_start_to_absolute_start(self):
        self.start_mark_var.set("00:00:00.000")
        self._set_status("Startmarke auf den Anfang des Videos gesetzt.")
        self._redraw_cut_window()

    def set_end_to_absolute_end(self):
        end_ms = max(self.player_duration_ms, 0)
        self.end_mark_var.set(self.cut_service.seconds_to_ts(end_ms / 1000.0))
        self._set_status("Endmarke auf das Ende des Videos gesetzt.")
        self._redraw_cut_window()

    def set_start_from_current_position(self):
        self.start_mark_var.set(self.current_position_var.get().strip() or "00:00:00.000")
        self._set_status(f"Startmarke gesetzt: {self.start_mark_var.get()}")
        self._maybe_update_suggested_title()
        self._redraw_cut_window()

    def set_end_from_current_position(self):
        self.end_mark_var.set(self.current_position_var.get().strip() or "00:00:00.000")
        self._set_status(f"Endmarke gesetzt: {self.end_mark_var.get()}")
        self._maybe_update_suggested_title()
        self._redraw_cut_window()

    def reset_marks(self):
        self.start_mark_var.set("00:00:00.000")
        self.end_mark_var.set("00:00:00.000")
        self.current_position_var.set("00:00:00.000")
        self.seek_var.set(0.0)
        self._set_status("Marken zurückgesetzt.")
        self._maybe_update_suggested_title(force=True)
        self._redraw_cut_window()

    def _redraw_cut_window(self):
        if self.cut_window and self.cut_window.winfo_exists():
            self.cut_window.sync_ui()

    def add_clip(self):
        try:
            begin = self.start_mark_var.get().strip()
            end = self.end_mark_var.get().strip()
            begin_s = self.cut_service.ts_to_seconds(begin)
            end_s = self.cut_service.ts_to_seconds(end)
            if end_s <= begin_s:
                raise ValueError("Die Endmarke muss zeitlich nach der Startmarke liegen.")
        except Exception as exc:
            msg = f"Clip konnte nicht angelegt werden: {exc}"
            self._set_status(msg)
            self._set_cut_window_hint(msg, is_error=True)
            return
        title = (self.clip_title_var.get() or "").strip()
        if not title:
            msg = "Bitte einen Titel / Dateinamen eingeben."
            self._set_status(msg)
            self._set_cut_window_hint(msg, is_error=True)
            return
        if title.lower() in self._existing_clip_titles():
            self._set_status(f"Clipname bereits vorhanden: {title}")
            self._maybe_update_suggested_title(force=True)
            return
        row = {"begin": begin, "end": end, "title": title}
        self.clip_rows.append(row)
        self._rebuild_clip_tree(select_index=None)
        try:
            self.clip_tree.selection_remove(*self.clip_tree.selection())
        except Exception:
            pass
        self._set_status(f"Clip angelegt: {title}")
        self._set_cut_window_hint(f"Clip angelegt: {title}", is_error=False)
        self._maybe_update_suggested_title(force=True)

    def update_clip(self):
        sel = self.clip_tree.selection()
        if not sel:
            self._set_status("Bitte zuerst einen Clip auswählen.")
            return
        idx = int(sel[0])
        try:
            begin = self.start_mark_var.get().strip()
            end = self.end_mark_var.get().strip()
            begin_s = self.cut_service.ts_to_seconds(begin)
            end_s = self.cut_service.ts_to_seconds(end)
            if end_s <= begin_s:
                raise ValueError("Die Endmarke muss zeitlich nach der Startmarke liegen.")
        except Exception as exc:
            msg = f"Clip konnte nicht aktualisiert werden: {exc}"
            self._set_status(msg)
            self._set_cut_window_hint(msg, is_error=True)
            return
        title = (self.clip_title_var.get() or "").strip()
        if not title:
            msg = "Bitte einen Titel / Dateinamen eingeben."
            self._set_status(msg)
            self._set_cut_window_hint(msg, is_error=True)
            return
        if title.lower() in self._existing_clip_titles(exclude_index=idx):
            self._set_status(f"Clipname bereits vorhanden: {title}")
            return
        self.clip_rows[idx] = {"begin": begin, "end": end, "title": title}
        self._rebuild_clip_tree(select_index=idx)
        self._set_status(f"Clip aktualisiert: {title}")
        self._set_cut_window_hint(f"Clip aktualisiert: {title}", is_error=False)

    def delete_clip(self):
        sel = self.clip_tree.selection()
        if not sel:
            self._set_status("Bitte zuerst einen Clip auswählen.")
            return
        idx = int(sel[0])
        removed = self.clip_rows.pop(idx)
        self._rebuild_clip_tree(select_index=min(idx, len(self.clip_rows) - 1))
        self._set_status(f"Clip gelöscht: {removed['title']}")
        self._set_cut_window_hint(f"Clip gelöscht: {removed['title']}", is_error=False)
        self._maybe_update_suggested_title(force=True)

    def _rebuild_clip_tree(self, select_index: int | None = None):
        self.clip_tree.delete(*self.clip_tree.get_children())
        for idx, row in enumerate(self.clip_rows):
            self.clip_tree.insert("", "end", iid=str(idx), values=(idx + 1, row["begin"], row["end"], row["title"]))
        if select_index is not None and 0 <= select_index < len(self.clip_rows):
            self.clip_tree.selection_set(str(select_index))
            self.clip_tree.focus(str(select_index))

    def _on_clip_selected(self, _event=None):
        sel = self.clip_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        row = self.clip_rows[idx]
        self.start_mark_var.set(row["begin"])
        self.end_mark_var.set(row["end"])
        self.clip_title_var.set(row["title"])
        self._redraw_cut_window()

    def create_selected_clip(self):
        p = self._project()
        if not p:
            self._set_status("Bitte zuerst ein Projekt laden.")
            return
        if not self.working_video_path or not self.working_video_path.exists():
            self._set_status("Bitte zuerst ein Arbeitsvideo erzeugen.")
            return
        sel = self.clip_tree.selection()
        if not sel:
            self._set_status("Bitte zuerst einen Clip auswählen.")
            return
        idx = int(sel[0])
        row = dict(self.clip_rows[idx])
        self._show_progress_window()

        def worker():
            try:
                out = self.cut_service.create_clip(
                    p,
                    self.working_video_path,
                    self.cut_service.ts_to_seconds(row["begin"]),
                    self.cut_service.ts_to_seconds(row["end"]),
                    row["title"],
                )
                self._progress_queue.put({"kind": "done_selected_clip", "target": str(out)})
            except Exception as exc:
                self._progress_queue.put({"kind": "error", "message": str(exc)})

        threading.Thread(target=worker, daemon=True).start()
        self.after(150, self._poll_progress_queue)

    def create_all_clips(self):
        p = self._project()
        if not p:
            self._set_status("Bitte zuerst ein Projekt laden.")
            return
        if not self.working_video_path or not self.working_video_path.exists():
            self._set_status("Bitte zuerst ein Arbeitsvideo erzeugen.")
            return
        if not self.clip_rows:
            self._set_status("Es sind keine Clips angelegt.")
            return
        rows = [dict(r) for r in self.clip_rows]
        self._show_progress_window()

        def worker():
            try:
                for row in rows:
                    self.cut_service.create_clip(
                        p,
                        self.working_video_path,
                        self.cut_service.ts_to_seconds(row["begin"]),
                        self.cut_service.ts_to_seconds(row["end"]),
                        row["title"],
                    )
                self._progress_queue.put({
                    "kind": "done_all_clips",
                    "message": f"Alle Clips gespeichert im Zielordner: {self.cut_service.clips_output_dir(p)}",
                })
            except Exception as exc:
                self._progress_queue.put({"kind": "error", "message": str(exc)})

        threading.Thread(target=worker, daemon=True).start()
        self.after(150, self._poll_progress_queue)

    def _refresh_other_tabs(self):
        for attr in ("media_tab", "combined_review_tab", "ffmpeg_tab", "targeted_edit_tab"):
            try:
                getattr(self.app, attr).refresh()
            except Exception:
                pass

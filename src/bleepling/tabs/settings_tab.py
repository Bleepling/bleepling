from __future__ import annotations
import tkinter as tk
import subprocess
from tkinter import ttk, filedialog

try:
    from PIL import Image, ImageTk  # type: ignore
except Exception:
    Image = None
    ImageTk = None

from bleepling.services.environment_service import EnvironmentService

HELP = {
    "Whisper-Modell": "Schnell = kleineres Modell und flotter. Ausgewogen = guter Standard. Genauer = größeres Modell, langsamer, oft bessere Erkennung. Für die meisten Fälle ist 'Ausgewogen' sinnvoll.",
    "Compute-Type": "Das ist die Rechenart auf GPU oder CPU. float16 ist für moderne NVIDIA-GPUs meist die beste Standardwahl. Nur ändern, wenn es Stabilitäts- oder Speicherprobleme gibt.",
    "Zusätzliche CUDA-Pfade": "Hier können Sie Ordner eintragen, in denen CUDA- oder cuDNN-Dateien liegen. Das hilft, wenn die GPU vorhanden ist, Bleepling die nötigen Dateien aber nicht automatisch findet.",
    "Transkriptionsmodus": "Auto versucht zuerst GPU und danach CPU. GPU versucht nur die Grafikkarte. CPU nutzt nur den Prozessor.",
    "Theme": "Hell = heller Hintergrund, dunkle Schrift. Dunkel = dunkler Hintergrund, weiße Schrift.",
    "Render-Backend": "Legt fest, womit Video gerendert wird.\n\nAuto: nutzt GPU, wenn ein NVIDIA-Encoder gefunden wird, sonst CPU.\nGPU: versucht den NVIDIA-Encoder zu nutzen; wenn keiner verfügbar ist, fällt Bleepling sicherheitshalber auf CPU zurück.\nCPU: rendert immer mit dem Prozessor. Das ist meist langsamer, aber sehr kompatibel.",
    "Textgröße": "Normal ist die Standardgröße. Etwas größer und Groß vergrößern Schriften moderat, ohne den Seitenaufbau unnötig zu zerstören.",
    "Render-Qualität": "Legt die Videoqualität für Render-Ausgaben fest.\n\n18 bis 23: höhere Qualität, größere Dateien.\n24 bis 30: guter Alltagsbereich.\n31 bis 38: kleinere Dateien, sichtbar stärkere Kompression.\n\n30 ist der bisherige Standard für die gezielte Nachbearbeitung.",
    "Render-Preset": "Legt fest, wie viel Zeit FFmpeg für die Kompression verwenden darf.\n\nultrafast, superfast, veryfast: schneller, aber meist größere Dateien.\nfast, medium: guter Standardbereich.\nslow, veryslow: langsamer, dafür oft effizientere Kompression.\n\nBei NVIDIA-GPU werden diese Stufen intern auf passende NVENC-Presets übertragen.",
    "Render-Audio-Bitrate": "Legt die AAC-Audioqualität fest.\n\n64k: sehr klein, eher sparsam.\n96k: bisheriger Standard und für Sprache meist ausreichend.\n128k: guter allgemeiner Standard.\n160k oder 192k: besser für Musik oder allgemeinen Ton, aber größere Dateien.",
    "Render-Skalierung": "Legt die Ausgabeauflösung fest.\n\nOriginalgröße beibehalten: verändert die Auflösung nicht; sicherer Standard für gezielte Nachbearbeitung.\n1280 px Breite: kleinere Web-Dateien, bei großen Quellen weniger Details.\n1920 px Breite: Full-HD-orientiert; kann kleine Quellen unnötig hochskalieren.",
}

RENDER_SCALE_OPTIONS = [
    "Originalgröße beibehalten",
    "1280 px Breite (kleiner für Web)",
    "1920 px Breite (größer / Full HD)",
]

RENDER_PRESET_OPTIONS = ["ultrafast", "superfast", "veryfast", "fast", "medium", "slow", "veryslow"]

MODEL_MAP = {
    "Schnell": "small",
    "Ausgewogen": "medium",
    "Genauer": "large-v3",
}
MODEL_MAP_REVERSE = {v: k for k, v in MODEL_MAP.items()}

class SettingsTab(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.environment_service = EnvironmentService()
        self._details = {}
        self._suspend_live_updates = False
        self._checks_wait_win = None
        self._checks_wait_img = None
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        frm = ttk.LabelFrame(self, text="")
        frm.grid(row=0, column=0, sticky="ew", padx=12, pady=12)
        frm.columnconfigure(0, weight=1)
        ttk.Label(frm, text="Transkription, GPU, VLC und Darstellung", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 8))

        self.mode = tk.StringVar(value="auto")
        self.model_display = tk.StringVar(value="Ausgewogen")
        self.compute = tk.StringVar(value="float16")
        self.paths = tk.StringVar(value="")
        self.theme = tk.StringVar(value="light")
        self.render_backend = tk.StringVar(value="auto")
        self.ui_scale = tk.StringVar(value="normal")
        self.render_quality = tk.IntVar(value=30)
        self.render_preset = tk.StringVar(value="medium")
        self.render_audio_bitrate = tk.StringVar(value="96k")
        self.render_scale = tk.StringVar(value="Originalgröße beibehalten")

        controls = ttk.Frame(frm)
        controls.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))
        controls.columnconfigure(0, weight=1)
        controls.columnconfigure(1, weight=1)

        left = ttk.Frame(controls)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.columnconfigure(1, weight=1)

        right = ttk.Frame(controls)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(1, weight=1)

        self._add_setting_row(left, 0, "Transkriptionsmodus", self.mode, ["auto", "gpu", "cpu"], 10, "Transkriptionsmodus")
        self._add_setting_row(left, 1, "Whisper-Modell", self.model_display, list(MODEL_MAP.keys()), 12, "Whisper-Modell")
        self._add_setting_row(left, 2, "Compute-Type", self.compute, ["float16", "int8_float16", "int8", "float32"], 12, "Compute-Type")

        self._add_setting_row(right, 0, "Theme", self.theme, ["light", "dark"], 10, "Theme")
        self._add_setting_row(right, 1, "Textgröße", self.ui_scale, ["normal", "etwas größer", "groß"], 14, "Textgröße")

        paths_row = ttk.Frame(frm)
        paths_row.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 8))
        paths_row.columnconfigure(1, weight=1)
        ttk.Label(paths_row, text="Zusätzliche CUDA-Pfade").grid(row=0, column=0, sticky="w")
        ttk.Entry(paths_row, textvariable=self.paths, width=60).grid(row=0, column=1, sticky="ew", padx=(10, 8))
        ttk.Button(paths_row, text="Ordner hinzufügen", command=self.add_folder).grid(row=0, column=2, padx=(0, 8))
        ttk.Button(paths_row, text="?", width=3, command=lambda: self.show_help("Zusätzliche CUDA-Pfade")).grid(row=0, column=3)

        render_box = ttk.LabelFrame(frm, text="")
        render_box.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 10))
        render_box.columnconfigure(1, weight=1)
        render_box.columnconfigure(4, weight=1)
        ttk.Label(render_box, text="Rendern / Ausgabe", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=6, sticky="w", pady=(8, 4))
        self._add_setting_row(render_box, 1, "Backend", self.render_backend, ["auto", "gpu", "cpu"], 10, "Render-Backend")
        self._add_spin_setting_row(render_box, 2, "Qualität (CQ/CRF)", self.render_quality, 18, 38, 5, "Render-Qualität")
        self._add_setting_row(render_box, 3, "Preset", self.render_preset, RENDER_PRESET_OPTIONS, 12, "Render-Preset")
        ttk.Label(render_box, text="Audio-Bitrate").grid(row=1, column=3, sticky="w", padx=(24, 0), pady=4)
        ttk.Combobox(render_box, textvariable=self.render_audio_bitrate, values=["64k", "96k", "128k", "160k", "192k"], width=12, state="readonly").grid(row=1, column=4, sticky="ew", padx=(10, 8), pady=4)
        ttk.Button(render_box, text="?", width=3, command=lambda: self.show_help("Render-Audio-Bitrate")).grid(row=1, column=5, sticky="w", pady=4)
        ttk.Label(render_box, text="Skalierung").grid(row=2, column=3, sticky="w", padx=(24, 0), pady=4)
        ttk.Combobox(render_box, textvariable=self.render_scale, values=RENDER_SCALE_OPTIONS, width=30, state="readonly").grid(row=2, column=4, sticky="ew", padx=(10, 8), pady=4)
        ttk.Button(render_box, text="?", width=3, command=lambda: self.show_help("Render-Skalierung")).grid(row=2, column=5, sticky="w", pady=4)

        row3 = ttk.Frame(frm)
        row3.grid(row=4, column=0, sticky="ew", padx=12, pady=(0, 10))
        for txt, cmd in [
            ("Projekt speichern", self.save_settings),
            ("Prüfung ausführen", self.run_checks),
            ("Installations-CMD kopieren", self.copy_install),
            ("Installations-CMD ausführen", self.run_install_cmd),
            ("CUDA-/PATH-CMD kopieren", self.copy_path),
        ]:
            ttk.Button(row3, text=txt, command=cmd, style="Accent.TButton").pack(side="left", padx=(0, 8))

        self.tree = ttk.Treeview(self, columns=("pruefpunkt", "status"), show="headings", height=16)
        self.tree.heading("pruefpunkt", text="Prüfpunkt")
        self.tree.heading("status", text="Status")
        self.tree.column("pruefpunkt", width=320, anchor="w")
        self.tree.column("status", width=100, anchor="center")
        self.tree.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.tree.bind("<<TreeviewSelect>>", self.show_detail)

        info_wrap = ttk.Frame(self)
        info_wrap.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))
        info_wrap.columnconfigure(0, weight=1)
        info_wrap.columnconfigure(1, weight=1)
        info_wrap.rowconfigure(0, weight=1)

        detail_wrap = ttk.LabelFrame(info_wrap, text="")
        detail_wrap.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        detail_wrap.columnconfigure(0, weight=1)
        detail_wrap.rowconfigure(1, weight=1)
        ttk.Label(detail_wrap, text="Details zum gewählten Prüfpunkt", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", padx=8, pady=(8, 0))
        self.detail = tk.Text(detail_wrap, height=10, wrap="word")
        self.detail.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)

        help_wrap = ttk.LabelFrame(info_wrap, text="")
        help_wrap.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        help_wrap.columnconfigure(0, weight=1)
        help_wrap.rowconfigure(1, weight=1)
        ttk.Label(help_wrap, text="Einfache Erklärungen und nächste Schritte", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", padx=8, pady=(8, 0))
        self.helpbox = tk.Text(help_wrap, height=10, wrap="word")
        self.helpbox.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        self.helpbox.insert("1.0", "Hier erscheinen einfache Erklärungen und konkrete Hinweise.")
        self.helpbox.config(state="disabled")
        self._set_general_commands_text(resolve_cuda_paths=False)
        self._bind_live_updates()

    def _apply_preview(self, *_):
        if self._suspend_live_updates:
            return
        try:
            self.app.apply_theme(self.theme.get())
        except Exception:
            pass
        try:
            if hasattr(self.app, "apply_ui_scale"):
                self.app.apply_ui_scale(self.ui_scale.get())
        except Exception:
            pass
        try:
            if hasattr(self.app, "save_ui_prefs"):
                self.app.save_ui_prefs(theme=self.theme.get(), ui_scale=self.ui_scale.get())
        except Exception:
            pass
        try:
            self.app.set_status("Darstellung sofort angewendet.")
        except Exception:
            pass

    def _bind_live_updates(self):
        self.theme.trace_add("write", self._apply_preview)
        self.ui_scale.trace_add("write", self._apply_preview)

    def _add_setting_row(self, parent, row, label, variable, values, width, help_key):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=4)
        ttk.Combobox(parent, textvariable=variable, values=values, width=width, state="readonly").grid(row=row, column=1, sticky="ew", padx=(10, 8), pady=4)
        ttk.Button(parent, text="?", width=3, command=lambda k=help_key: self.show_help(k)).grid(row=row, column=2, sticky="w", pady=4)

    def _add_spin_setting_row(self, parent, row, label, variable, from_, to, width, help_key):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=4)
        ttk.Spinbox(parent, from_=from_, to=to, textvariable=variable, width=width).grid(row=row, column=1, sticky="w", padx=(10, 8), pady=4)
        ttk.Button(parent, text="?", width=3, command=lambda k=help_key: self.show_help(k)).grid(row=row, column=2, sticky="w", pady=4)

    def _set_general_commands_text(self, resolve_cuda_paths: bool = False):
        install_cmd = self.environment_service.get_install_command()
        extra_paths = [p.strip() for p in self.paths.get().split(";") if p.strip()]
        if resolve_cuda_paths:
            path_cmd = self.environment_service.get_path_command(extra_paths)
        elif extra_paths:
            path_cmd = f"set PATH={';'.join(extra_paths)};%PATH%"
        else:
            path_cmd = (
                "Wird bei Bedarf ermittelt. Für die vollständige automatische Pfadsuche bitte "
                "'Prüfung ausführen' oder 'CUDA-/PATH-CMD kopieren' verwenden."
            )
        text = (
            "Hilfreiche Befehle für die Einrichtung:\n\n"
            "Installations-CMD:\n"
            f"{install_cmd}\n\n"
            "CUDA-/PATH-CMD:\n"
            f"{path_cmd}\n\n"
            "Hinweis:\n"
            "Der CUDA-/PATH-Befehl ergänzt erkannte CUDA-Ordner im aktuellen Kommandozeilen-Kontext. "
            "Das ist vor allem hilfreich, wenn GPU-Dateien vorhanden sind, aber von der Anwendung nicht gefunden werden."
        )
        self.detail.delete("1.0", "end")
        self.detail.insert("1.0", text)

    def refresh(self):
        if not self.app.project:
            return
        s = self.app.project.read_settings()
        self._suspend_live_updates = True
        try:
            self.mode.set(s.get("transcription_mode", "auto"))
            self.model_display.set(MODEL_MAP_REVERSE.get(s.get("whisper_model", "medium"), "Ausgewogen"))
            self.compute.set(s.get("compute_type", "float16"))
            self.paths.set(s.get("extra_cuda_paths", ""))
            self.theme.set(s.get("theme", getattr(self.app, "current_theme", "light")))
            self.render_backend.set(s.get("render_backend", "auto"))
            self.ui_scale.set(s.get("ui_scale", getattr(self.app, "ui_scale", "normal")))
            self.render_quality.set(int(s.get("render_quality", 30)))
            self.render_preset.set(s.get("render_preset", "medium"))
            self.render_audio_bitrate.set(s.get("render_audio_bitrate", "96k"))
            self.render_scale.set(s.get("render_scale", "Originalgröße beibehalten"))
        finally:
            self._suspend_live_updates = False
        self._set_general_commands_text(resolve_cuda_paths=False)

    def _show_checks_wait_window(self):
        if self._checks_wait_win is not None:
            return
        win = tk.Toplevel(self)
        win.title("Prüfung läuft")
        win.transient(self.winfo_toplevel())
        try:
            win.attributes("-topmost", True)
        except Exception:
            pass
        win.resizable(False, False)
        frame = ttk.Frame(win, padding=18)
        frame.pack(fill="both", expand=True)

        bird_path = None
        try:
            bird_path = self.app._asset("vogel2_light_512_fixed.png")
        except Exception:
            bird_path = None
        if Image is not None and ImageTk is not None and bird_path and bird_path.exists():
            img = Image.open(bird_path).resize((180, 180))
            self._checks_wait_img = ImageTk.PhotoImage(img)
            ttk.Label(frame, image=self._checks_wait_img).pack(pady=(0, 10))
        else:
            ttk.Label(frame, text="🐤", font=("Segoe UI Emoji", 36)).pack(pady=(0, 10))

        ttk.Label(frame, text="Prüfung läuft gerade ... bitte warten", justify="center").pack(pady=(0, 10))
        ttk.Label(
            frame,
            text="Die Prüfpunkte erscheinen schrittweise in der Liste.",
            justify="center",
            wraplength=420,
        ).pack(pady=(6, 0))

        win.update_idletasks()
        root = self.winfo_toplevel()
        rx, ry, rw, rh = root.winfo_rootx(), root.winfo_rooty(), root.winfo_width(), root.winfo_height()
        ww, wh = win.winfo_width(), win.winfo_height()
        win.geometry(f"+{rx + max(0, (rw - ww) // 2)}+{ry + max(0, (rh - wh) // 2)}")
        self._checks_wait_win = win
        try:
            win.update()
        except Exception:
            pass

    def _hide_checks_wait_window(self):
        try:
            if self._checks_wait_win is not None:
                self._checks_wait_win.destroy()
        except Exception:
            pass
        self._checks_wait_win = None
        self._checks_wait_img = None

    def save_settings(self):
        if not self.app.project:
            return
        self.app.project.write_settings({
            "transcription_mode": self.mode.get(),
            "whisper_model": MODEL_MAP.get(self.model_display.get(), "medium"),
            "compute_type": self.compute.get(),
            "extra_cuda_paths": self.paths.get(),
            "theme": self.theme.get(),
            "render_backend": self.render_backend.get(),
            "ui_scale": self.ui_scale.get(),
            "render_quality": int(self.render_quality.get()),
            "render_preset": self.render_preset.get(),
            "render_audio_bitrate": self.render_audio_bitrate.get(),
            "render_scale": self.render_scale.get(),
        })
        if hasattr(self.app, "save_ui_prefs"):
            self.app.save_ui_prefs(theme=self.theme.get(), ui_scale=self.ui_scale.get())
        self.app.apply_theme(self.theme.get())
        if hasattr(self.app, "apply_ui_scale"):
            self.app.apply_ui_scale(self.ui_scale.get())
        self.app.set_status("Projekt gespeichert: Einstellungen wurden gesichert. Darstellung wirkt auch ohne Speichern sofort.")

    def add_folder(self):
        path = filedialog.askdirectory(title="CUDA- oder cuDNN-Ordner auswählen")
        if not path:
            return
        current = [p.strip() for p in self.paths.get().split(";") if p.strip()]
        if path not in current:
            current.append(path)
        self.paths.set(";".join(current))
        self._set_general_commands_text(resolve_cuda_paths=False)
        self.show_help("Zusätzliche CUDA-Pfade")

    def run_checks(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        self._details = {}
        extra_paths = [p.strip() for p in self.paths.get().split(";") if p.strip()]
        self._show_checks_wait_window()

        def add_item(item):
            iid = self.tree.insert("", "end", values=(item.name, item.status))
            self._details[iid] = item.details
            self.update_idletasks()
            try:
                if self._checks_wait_win is not None:
                    self._checks_wait_win.update()
            except Exception:
                pass

        try:
            self.environment_service.diagnose(self.app.project, extra_paths, progress_callback=add_item)
        finally:
            self._hide_checks_wait_window()
        self._set_help(
            "So gehen Sie am einfachsten vor:\n"
            "1) Klicken Sie auf 'Prüfung ausführen'.\n"
            "2) Wählen Sie in der Liste den fehlenden oder problematischen Punkt an.\n"
            "3) Lesen Sie unten die Details.\n"
            "4) Fehlen Bausteine, kopieren Sie den Installationsbefehl und fügen ihn in CMD ein.\n"
            "5) Fehlt VLC, installieren Sie die normale VLC-Desktop-App und danach die passende Anbindung.\n"
            "6) Fehlen GPU-Dateien, tragen Sie den passenden Ordner bei 'Zusätzliche CUDA-Pfade' ein.\n"
            "7) Wenn Sie die Prüfung später noch einmal brauchen, klicken Sie einfach erneut auf 'Prüfung ausführen'.\n\n"
            "Für die sichtbaren Prüf- und Entscheidungsreiter sollten mindestens diese Punkte auf ok stehen:\n"
            "- VLC-Anbindung\n"
            "- VLC Desktop-App\n"
            "- Laufzeitbibliothek\n"
            "- VLC-Plugins\n"
            "- VLC-Probe\n\n"
            "Empfehlung für Ihren Rechner:\n"
            "- Transkriptionsmodus: auto oder gpu\n"
            "- Whisper-Modell: Ausgewogen\n"
            "- Compute-Type: float16\n"
            "- Render-Backend: auto oder gpu\n"
            "- Textgröße: normal oder etwas größer"
        )
        self._set_general_commands_text(resolve_cuda_paths=True)
        self.app.set_status("Prüfung für Transkription, GPU und VLC aktualisiert.")

    def show_detail(self, event=None):
        sel = self.tree.selection()
        if not sel:
            self._set_general_commands_text(resolve_cuda_paths=False)
            return
        text = self._details.get(sel[0], "")
        self.detail.delete("1.0", "end")
        self.detail.insert("1.0", text)

    def show_help(self, key):
        self._set_help(HELP[key])

    def _set_help(self, text):
        self.helpbox.config(state="normal")
        self.helpbox.delete("1.0", "end")
        self.helpbox.insert("1.0", text)
        self.helpbox.config(state="disabled")

    def run_install_cmd(self):
        cmd = self.environment_service.get_install_command()
        try:
            subprocess.Popen(f'cmd.exe /k {cmd}', shell=True)
            self._set_general_commands_text(resolve_cuda_paths=False)
            self._set_help(
                "Ein neues CMD-Fenster wurde geöffnet und der Installationsbefehl wurde dort gestartet. "
                "Das Fenster bleibt offen, damit Sie die Ausgabe und eventuelle Fehlermeldungen lesen können."
            )
            self.app.set_status("Installations-CMD in neuem Fenster gestartet.")
        except Exception as exc:
            self._set_help(
                "Der Installationsbefehl konnte nicht automatisch gestartet werden. "
                f"Fehler: {exc}"
            )
            self.app.set_status(f"Installations-CMD konnte nicht gestartet werden: {exc}")

    def copy_install(self):
        self.clipboard_clear()
        self.clipboard_append(self.environment_service.get_install_command())
        self._set_general_commands_text(resolve_cuda_paths=False)
        self._set_help(
            "Der Installationsbefehl wurde kopiert. Sie sehen ihn zusätzlich links im Detailbereich und können ihn dort direkt prüfen."
        )

    def copy_path(self):
        self.clipboard_clear()
        extra_paths = [p.strip() for p in self.paths.get().split(";") if p.strip()]
        self.clipboard_append(self.environment_service.get_path_command(extra_paths))
        self._set_general_commands_text(resolve_cuda_paths=True)
        self._set_help(
            "Der CUDA-/PATH-Befehl wurde kopiert. Damit können erkannte CUDA-Ordner für die aktuelle Kommandozeile in den Pfad gesetzt werden, "
            "damit GPU-Dateien leichter gefunden werden."
        )

from __future__ import annotations
import tkinter as tk
import subprocess
from tkinter import ttk, filedialog
from bleepling.services.environment_service import EnvironmentService

HELP = {
    "Whisper-Modell": "Schnell = kleineres Modell und flotter. Ausgewogen = guter Standard. Genauer = größeres Modell, langsamer, oft bessere Erkennung. Für die meisten Fälle ist 'Ausgewogen' sinnvoll.",
    "Compute-Type": "Das ist die Rechenart auf GPU oder CPU. float16 ist für moderne NVIDIA-GPUs meist die beste Standardwahl. Nur ändern, wenn es Stabilitäts- oder Speicherprobleme gibt.",
    "Zusätzliche CUDA-Pfade": "Hier können Sie Ordner eintragen, in denen CUDA- oder cuDNN-Dateien liegen. Das hilft, wenn die GPU vorhanden ist, Bleepling die nötigen Dateien aber nicht automatisch findet.",
    "Transkriptionsmodus": "Auto versucht zuerst GPU und danach CPU. GPU versucht nur die Grafikkarte. CPU nutzt nur den Prozessor.",
    "Theme": "Hell = heller Hintergrund, dunkle Schrift. Dunkel = dunkler Hintergrund, weiße Schrift.",
    "Render-Backend": "Auto nutzt bevorzugt GPU, wenn ein NVIDIA-Encoder verfügbar ist. GPU erzwingt den GPU-Encoder. CPU erzwingt CPU-Encoding. Das wirkt sich auf die Profile im Reiter Video & Audio / FFmpeg aus.",
    "Textgröße": "Normal ist die Standardgröße. Etwas größer und Groß vergrößern Schriften moderat, ohne den Seitenaufbau unnötig zu zerstören.",
}

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

        frm = ttk.LabelFrame(self, text="Transkription, GPU und Darstellung")
        frm.pack(fill="x", padx=12, pady=12)

        self.mode = tk.StringVar(value="auto")
        self.model_display = tk.StringVar(value="Ausgewogen")
        self.compute = tk.StringVar(value="float16")
        self.paths = tk.StringVar(value="")
        self.theme = tk.StringVar(value="light")
        self.render_backend = tk.StringVar(value="auto")
        self.ui_scale = tk.StringVar(value="normal")

        row1 = ttk.Frame(frm)
        row1.pack(fill="x", padx=12, pady=6)
        ttk.Label(row1, text="Transkriptionsmodus").grid(row=0, column=0, sticky="w")
        ttk.Combobox(row1, textvariable=self.mode, values=["auto", "gpu", "cpu"], width=10, state="readonly").grid(row=0, column=1, sticky="w", padx=(8, 14))
        ttk.Button(row1, text="?", width=3, command=lambda: self.show_help("Transkriptionsmodus")).grid(row=0, column=2)
        ttk.Label(row1, text="Whisper-Modell").grid(row=0, column=3, sticky="w", padx=(20, 0))
        ttk.Combobox(row1, textvariable=self.model_display, values=list(MODEL_MAP.keys()), width=12, state="readonly").grid(row=0, column=4, sticky="w", padx=(8, 14))
        ttk.Button(row1, text="?", width=3, command=lambda: self.show_help("Whisper-Modell")).grid(row=0, column=5)
        ttk.Label(row1, text="Theme").grid(row=0, column=6, sticky="w", padx=(20, 0))
        ttk.Combobox(row1, textvariable=self.theme, values=["light", "dark"], width=10, state="readonly").grid(row=0, column=7, sticky="w", padx=(8, 14))
        ttk.Button(row1, text="?", width=3, command=lambda: self.show_help("Theme")).grid(row=0, column=8)

        row2 = ttk.Frame(frm)
        row2.pack(fill="x", padx=12, pady=6)
        ttk.Label(row2, text="Compute-Type").grid(row=0, column=0, sticky="w")
        ttk.Combobox(row2, textvariable=self.compute, values=["float16", "int8_float16", "int8", "float32"], width=12, state="readonly").grid(row=0, column=1, sticky="w", padx=(8, 14))
        ttk.Button(row2, text="?", width=3, command=lambda: self.show_help("Compute-Type")).grid(row=0, column=2)
        ttk.Label(row2, text="Zusätzliche CUDA-Pfade").grid(row=0, column=3, sticky="w", padx=(20, 0))
        ttk.Entry(row2, textvariable=self.paths, width=60).grid(row=0, column=4, sticky="we", padx=(8, 8))
        ttk.Button(row2, text="Ordner hinzufügen", command=self.add_folder).grid(row=0, column=5, padx=(0, 8))
        ttk.Button(row2, text="?", width=3, command=lambda: self.show_help("Zusätzliche CUDA-Pfade")).grid(row=0, column=6)

        row25 = ttk.Frame(frm)
        row25.pack(fill="x", padx=12, pady=6)
        ttk.Label(row25, text="Render-Backend").grid(row=0, column=0, sticky="w")
        ttk.Combobox(row25, textvariable=self.render_backend, values=["auto", "gpu", "cpu"], width=10, state="readonly").grid(row=0, column=1, sticky="w", padx=(8, 14))
        ttk.Button(row25, text="?", width=3, command=lambda: self.show_help("Render-Backend")).grid(row=0, column=2)
        ttk.Label(row25, text="Textgröße").grid(row=0, column=3, sticky="w", padx=(20, 0))
        ttk.Combobox(row25, textvariable=self.ui_scale, values=["normal", "etwas größer", "groß"], width=14, state="readonly").grid(row=0, column=4, sticky="w", padx=(8, 14))
        ttk.Button(row25, text="?", width=3, command=lambda: self.show_help("Textgröße")).grid(row=0, column=5)

        row3 = ttk.Frame(frm)
        row3.pack(fill="x", padx=12, pady=8)
        for txt, cmd in [
            ("Projekt speichern", self.save_settings),
            ("Prüfung ausführen", self.run_checks),
            ("Prüfung erneut ausführen", self.run_checks),
            ("Installations-CMD kopieren", self.copy_install),
            ("Installations-CMD ausführen", self.run_install_cmd),
            ("PATH-CMD kopieren", self.copy_path),
        ]:
            ttk.Button(row3, text=txt, command=cmd, style="Accent.TButton").pack(side="left", padx=(0, 8))

        self.tree = ttk.Treeview(self, columns=("pruefpunkt", "status"), show="headings", height=12)
        self.tree.heading("pruefpunkt", text="Prüfpunkt")
        self.tree.heading("status", text="Status")
        self.tree.column("pruefpunkt", width=280, anchor="w")
        self.tree.column("status", width=100, anchor="center")
        self.tree.pack(fill="both", expand=False, padx=12, pady=(0, 12))
        self.tree.bind("<<TreeviewSelect>>", self.show_detail)

        ttk.Label(self, text="Details zum gewählten Prüfpunkt").pack(anchor="w", padx=12)
        self.detail = tk.Text(self, height=8, wrap="word")
        self.detail.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        ttk.Label(self, text="Hilfe in normalem Deutsch").pack(anchor="w", padx=12)
        self.helpbox = tk.Text(self, height=8, wrap="word")
        self.helpbox.pack(fill="x", padx=12, pady=(0, 12))
        self.helpbox.insert("1.0", "Hier erscheinen einfache Erklärungen und konkrete Hinweise.")
        self.helpbox.config(state="disabled")
        self._bind_live_updates()


    def _apply_preview(self, *_):
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
    def refresh(self):
        if not self.app.project:
            return
        s = self.app.project.read_settings()
        self.mode.set(s.get("transcription_mode", "auto"))
        self.model_display.set(MODEL_MAP_REVERSE.get(s.get("whisper_model", "medium"), "Ausgewogen"))
        self.compute.set(s.get("compute_type", "float16"))
        self.paths.set(s.get("extra_cuda_paths", ""))
        self.theme.set(s.get("theme", getattr(self.app, "current_theme", "light")))
        self.render_backend.set(s.get("render_backend", "auto"))
        self.ui_scale.set(s.get("ui_scale", getattr(self.app, "ui_scale", "normal")))

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
        self.show_help("Zusätzliche CUDA-Pfade")

    def run_checks(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        self._details = {}
        extra_paths = [p.strip() for p in self.paths.get().split(";") if p.strip()]
        rows = self.environment_service.diagnose(self.app.project, extra_paths)
        for item in rows:
            iid = self.tree.insert("", "end", values=(item.name, item.status))
            self._details[iid] = item.details
        self._set_help(
            "So gehen Sie am einfachsten vor:\\n"
            "1) Klicken Sie auf 'Prüfung ausführen'.\\n"
            "2) Wählen Sie in der Liste den fehlenden oder problematischen Punkt an.\\n"
            "3) Lesen Sie unten die Details.\\n"
            "4) Fehlen Python-Bausteine, kopieren Sie den Installationsbefehl und fügen ihn dort in CMD ein.\\n"
            "5) Fehlen GPU-Dateien, tragen Sie den passenden Ordner bei 'Zusätzliche CUDA-Pfade' ein.\\n"
            "6) Klicken Sie danach auf 'Prüfung erneut ausführen'.\\n\\n"
            "Empfehlung für Ihren Rechner:\\n"
            "- Transkriptionsmodus: auto oder gpu\\n"
            "- Whisper-Modell: Ausgewogen\\n"
            "- Compute-Type: float16\\n"
            "- Render-Backend: auto oder gpu\\n"
            "- Textgröße: normal oder etwas größer"
        )
        self.app.set_status("Prüfung für Transkription und GPU aktualisiert.")

    def show_detail(self, event=None):
        sel = self.tree.selection()
        if not sel:
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
            # cmd.exe /k erwartet den Befehl am zuverlässigsten als zusammenhängende Zeichenkette.
            subprocess.Popen(f'cmd.exe /k {cmd}', shell=True)
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
        self._set_help("Der Installationsbefehl wurde kopiert. Öffnen Sie die Eingabeaufforderung und fügen Sie ihn dort ein.")

    def copy_path(self):
        self.clipboard_clear()
        extra_paths = [p.strip() for p in self.paths.get().split(";") if p.strip()]
        self.clipboard_append(self.environment_service.get_path_command(extra_paths))
        self._set_help("Der PATH-Befehl wurde kopiert. Damit können typische CUDA-Ordner dauerhaft in den Windows-Pfad aufgenommen werden.")

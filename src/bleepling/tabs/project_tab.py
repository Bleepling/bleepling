from __future__ import annotations
import json
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
from pathlib import Path
from bleepling.services.project_service import ProjectService

try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None


class ProjectTab(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.project_service = ProjectService()
        self.project_bird_img = None
        self.delete_bird_img = None

        top = ttk.Frame(self)
        top.pack(fill="x", padx=12, pady=12)

        ttk.Button(top, text="Neues Projekt anlegen", command=self.create_project).pack(side="left")
        ttk.Button(top, text="Bestehendes Projekt laden", command=self.open_project).pack(side="left", padx=8)
        ttk.Button(top, text="Bestehendes Projekt löschen", command=self.delete_project).pack(side="right")

        self.label = ttk.Label(self, text="Noch kein Projekt geladen.")
        self.label.pack(anchor="w", padx=12, pady=12)

        info = (
            "Neues Projekt anlegen: Zuerst einen bestehenden Zielordner wählen, danach einen Projektnamen eingeben.\n"
            "Bestehendes Projekt laden: Bereits vorhandenen Bleepling-Projektordner auswählen."
        )
        ttk.Label(self, text=info).pack(anchor="w", padx=12, pady=(0, 12))

        bird_wrap = ttk.Frame(self)
        bird_wrap.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        bird_wrap.columnconfigure(0, weight=1)
        bird_wrap.rowconfigure(0, weight=1)
        self.bird_label = ttk.Label(bird_wrap, anchor="center")
        self.bird_label.grid(row=0, column=0, sticky="nsew")
        self._refresh_bird()

    def _asset(self, name: str) -> Path:
        return Path(__file__).resolve().parents[3] / "assets" / name

    def _refresh_bird(self):
        bird_path = self._asset("vogel1_light_512.png")
        if Image is not None and ImageTk is not None and bird_path.exists():
            img = Image.open(bird_path).resize((420, 420))
            self.project_bird_img = ImageTk.PhotoImage(img)
            self.bird_label.configure(image=self.project_bird_img, text="")
        else:
            self.bird_label.configure(image="", text="🐤")

    def refresh(self):
        self._refresh_bird()
        if self.app.project:
            try:
                self.label.config(text=f"Projekt geladen: {self.app.project.root_path}")
            except Exception:
                self.label.config(text="Projekt geladen.")
        else:
            self.label.config(text="Noch kein Projekt geladen.")

    def _missing_project_parts(self, project_dir: Path) -> list[str]:
        missing = []
        for rel_dir in self.project_service.REQUIRED_DIRS:
            if not (project_dir / rel_dir).is_dir():
                missing.append(rel_dir)

        project_file = project_dir / "99_config" / "project.json"
        if not project_file.is_file():
            missing.append("99_config/project.json")
            return missing

        try:
            payload = json.loads(project_file.read_text(encoding="utf-8"))
            if not isinstance(payload, dict) or not payload.get("name") or not payload.get("root_path"):
                missing.append("99_config/project.json (ungültiger Inhalt)")
        except Exception:
            missing.append("99_config/project.json (nicht lesbar)")
        return missing

    def _confirm_delete_project(self, project_dir: Path) -> bool:
        result = {"delete": False}
        win = tk.Toplevel(self)
        win.title("Projekt löschen?")
        win.transient(self.winfo_toplevel())
        win.resizable(False, False)
        win.grab_set()

        frame = ttk.Frame(win, padding=18)
        frame.pack(fill="both", expand=True)

        content = ttk.Frame(frame)
        content.pack(fill="both", expand=True)

        bird_path = self._asset("vogel3_light_512.png")
        if Image is not None and ImageTk is not None and bird_path.exists():
            try:
                img = Image.open(bird_path).resize((96, 96))
                self.delete_bird_img = ImageTk.PhotoImage(img)
                ttk.Label(content, image=self.delete_bird_img).pack(side="left", padx=(0, 16), anchor="n")
            except Exception:
                pass

        text_box = ttk.Frame(content)
        text_box.pack(side="left", fill="both", expand=True)
        ttk.Label(
            text_box,
            text="Dieses Bleepling-Projekt wird vollständig gelöscht:",
            wraplength=460,
            justify="left",
        ).pack(anchor="w")
        ttk.Label(text_box, text=str(project_dir), font=("Segoe UI", 10, "bold"), wraplength=460).pack(anchor="w", pady=(8, 8))
        ttk.Label(
            text_box,
            text="Dabei werden alle Projektordner, Eingabedateien, Zwischenstände und Ausgaben in diesem Ordner entfernt. Möchten Sie wirklich fortfahren?",
            wraplength=460,
            justify="left",
        ).pack(anchor="w")

        btn_row = ttk.Frame(frame)
        btn_row.pack(fill="x", pady=(18, 0))

        def close(confirmed: bool):
            result["delete"] = confirmed
            win.destroy()

        ttk.Button(btn_row, text="Nein", command=lambda: close(False)).pack(side="right")
        ttk.Button(btn_row, text="Ja, Projekt löschen", command=lambda: close(True)).pack(side="right", padx=(0, 8))
        win.protocol("WM_DELETE_WINDOW", lambda: close(False))

        win.update_idletasks()
        root = self.winfo_toplevel()
        x = root.winfo_rootx() + max(0, (root.winfo_width() - win.winfo_width()) // 2)
        y = root.winfo_rooty() + max(0, (root.winfo_height() - win.winfo_height()) // 2)
        win.geometry(f"+{x}+{y}")
        win.wait_window()
        return result["delete"]

    def delete_project(self):
        try:
            recent = self.app.get_recent_project() if hasattr(self.app, "get_recent_project") else None
            initialdir = str(recent.parent) if recent and recent.exists() else None
            path = filedialog.askdirectory(
                parent=self.winfo_toplevel(),
                title="Zu löschendes Bleepling-Projekt auswählen",
                mustexist=True,
                initialdir=initialdir,
            )
            if not path:
                self.app.set_status("Projektlöschung abgebrochen.")
                return

            project_dir = Path(path).resolve()
            missing = self._missing_project_parts(project_dir)
            if missing:
                messagebox.showwarning(
                    "Projekt löschen",
                    "Der ausgewählte Ordner ist kein vollständiges Bleepling-Projekt und wird deshalb nicht gelöscht.\n\n"
                    "Fehlend oder ungültig:\n- " + "\n- ".join(missing),
                    parent=self.winfo_toplevel(),
                )
                self.app.set_status("Projektlöschung abgebrochen: kein vollständiges Bleepling-Projekt.")
                return

            if not self._confirm_delete_project(project_dir):
                self.app.set_status("Projektlöschung abgebrochen.")
                return

            current_project = getattr(self.app, "project", None)
            current_path = Path(current_project.root_path).resolve() if current_project else None
            shutil.rmtree(project_dir)

            if hasattr(self.app, "forget_recent_project"):
                self.app.forget_recent_project(project_dir)
            if current_path == project_dir:
                self.app.project = None
            self.refresh()
            self.app.set_status(f"Projekt gelöscht: {project_dir}")
        except Exception as e:
            messagebox.showerror("Projekt löschen", f"Projekt konnte nicht gelöscht werden:\n{e}", parent=self.winfo_toplevel())
            self.app.set_status("Projektlöschung fehlgeschlagen.")

    def create_project(self):
        try:
            parent = filedialog.askdirectory(
                parent=self.winfo_toplevel(),
                title="Übergeordneten Ordner für neues Bleepling-Projekt wählen",
                mustexist=True,
            )
            if not parent:
                self.app.set_status("Projektanlage abgebrochen.")
                return

            name = simpledialog.askstring(
                "Projektname",
                "Bitte Namen für das neue Projekt eingeben:",
                parent=self.winfo_toplevel(),
            )
            if not name or not name.strip():
                self.app.set_status("Projektanlage abgebrochen.")
                return

            project_dir = Path(parent) / name.strip()
            if project_dir.exists():
                answer = messagebox.askyesno(
                    "Projektordner vorhanden",
                    "Zu diesem Projektnamen existiert bereits ein Projektordner. Soll er als bestehendes Projekt geöffnet werden?",
                    parent=self.winfo_toplevel(),
                )
                if not answer:
                    self.app.set_status("Projektanlage abgebrochen.")
                    return

                missing = self.project_service.validate_project(project_dir)
                if missing:
                    messagebox.showerror(
                        "Projekt laden",
                        "Der vorhandene Ordner ist kein vollständiges Bleepling-Projekt.\n\nFehlend:\n- " + "\n- ".join(missing),
                        parent=self.winfo_toplevel(),
                    )
                    self.app.set_status("Projektladen fehlgeschlagen.")
                    return

                p = self.project_service.load_project(project_dir)
                self.app.set_project(p)
                return

            answer = messagebox.askyesno(
                "Projektordner anlegen",
                "Zu diesem Projektnamen wurde noch kein Projektordner angelegt. Soll dieser nun hier angelegt werden?",
                parent=self.winfo_toplevel(),
            )
            if not answer:
                self.app.set_status("Projektanlage abgebrochen.")
                return

            p = self.project_service.create_project(Path(parent), name.strip())
            self.app.set_project(p)
        except Exception as e:
            messagebox.showerror(
                "Projekt anlegen",
                f"Projekt konnte nicht angelegt oder geladen werden:\n{e}",
                parent=self.winfo_toplevel(),
            )
            self.app.set_status("Projektanlage fehlgeschlagen.")

    def open_project(self):
        try:
            recent = self.app.get_recent_project() if hasattr(self.app, "get_recent_project") else None
            if recent and recent.exists():
                answer = messagebox.askyesno(
                    "Bestehendes Projekt laden",
                    f"Zuletzt geöffnetes Projekt erneut laden?\n\n{recent}",
                    parent=self.winfo_toplevel(),
                )
                if answer:
                    missing = self.project_service.validate_project(recent)
                    if not missing:
                        p = self.project_service.load_project(recent)
                        self.app.set_project(p)
                        return

            initialdir = str(recent.parent) if recent and recent.exists() else None
            path = filedialog.askdirectory(
                parent=self.winfo_toplevel(),
                title="Bestehendes Bleepling-Projekt laden",
                mustexist=True,
                initialdir=initialdir,
            )
            if not path:
                self.app.set_status("Projektladen abgebrochen.")
                return

            missing = self.project_service.validate_project(Path(path))
            if missing:
                messagebox.showerror(
                    "Projekt laden",
                    "Der ausgewählte Ordner ist kein vollständiges Bleepling-Projekt.\n\nFehlend:\n- " + "\n- ".join(missing),
                    parent=self.winfo_toplevel(),
                )
                self.app.set_status("Projektladen fehlgeschlagen.")
                return

            p = self.project_service.load_project(Path(path))
            self.app.set_project(p)
        except Exception as e:
            messagebox.showerror("Projekt laden", f"Projekt konnte nicht geladen werden:\n{e}", parent=self.winfo_toplevel())
            self.app.set_status("Projektladen fehlgeschlagen.")

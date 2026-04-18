from __future__ import annotations
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

        top = ttk.Frame(self)
        top.pack(fill="x", padx=12, pady=12)

        ttk.Button(top, text="Neues Projekt anlegen", command=self.create_project).pack(side="left")
        ttk.Button(top, text="Bestehendes Projekt laden", command=self.open_project).pack(side="left", padx=8)

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

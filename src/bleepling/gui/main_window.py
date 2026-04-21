from __future__ import annotations
import ctypes
import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from bleepling.tabs.project_tab import ProjectTab
from bleepling.tabs.media_tab import MediaTab
from bleepling.tabs.cut_tab import CutTab
from bleepling.tabs.bleeping_tab import BleepingTab
from bleepling.tabs.ffmpeg_tab import FFmpegTab
from bleepling.tabs.targeted_edit_tab import TargetedEditTab
from bleepling.tabs.hit_review_tab import HitReviewTab
from bleepling.tabs.settings_tab import SettingsTab
from bleepling.tabs.titlecards_tab import TitleCardsTab
from bleepling.tabs.combined_review_tab import CombinedReviewTab
from PIL import Image, ImageTk


class BleeplingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bleepling – names out, privacy in")
        default_width = 1860
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        usable_y = 0
        usable_height = screen_height
        try:
            class RECT(ctypes.Structure):
                _fields_ = [
                    ("left", ctypes.c_long),
                    ("top", ctypes.c_long),
                    ("right", ctypes.c_long),
                    ("bottom", ctypes.c_long),
                ]

            rect = RECT()
            if ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0):
                usable_y = max(0, int(rect.top))
                usable_height = max(860, int(rect.bottom - rect.top) - 48)
        except Exception:
            pass
        width = min(default_width, screen_width)
        x = max(0, (screen_width - width) // 2)
        self.geometry(f"{width}x{usable_height}+{x}+{usable_y}")
        self.minsize(1200, 860)
        self.project = None
        self.logo_img = None
        self.current_theme = "light"
        self.ui_scale = "normal"
        self._build()
        self.apply_theme(self.current_theme)

    def _asset(self, name: str) -> Path:
        return Path(__file__).resolve().parents[3] / "assets" / name

    def _state_file(self) -> Path:
        path = Path.home() / ".bleepling"
        path.mkdir(parents=True, exist_ok=True)
        return path / "app_state.json"

    def _read_state(self) -> dict:
        try:
            path = self._state_file()
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
        return {}

    def remember_recent_project(self, project_path: Path):
        try:
            data = self._read_state()
            data["last_project"] = str(project_path)
            self._state_file().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def get_recent_project(self) -> Path | None:
        try:
            data = self._read_state()
            last = data.get("last_project")
            if last:
                p = Path(last)
                if p.exists():
                    return p
        except Exception:
            pass
        return None

    def forget_recent_project(self, project_path: Path):
        try:
            data = self._read_state()
            last = data.get("last_project")
            if last and Path(last).resolve() == Path(project_path).resolve():
                data.pop("last_project", None)
                self._state_file().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def save_ui_prefs(self, theme: str | None = None, ui_scale: str | None = None):
        try:
            data = self._read_state()
            if theme is not None:
                data["theme"] = theme
            if ui_scale is not None:
                data["ui_scale"] = ui_scale
            self._state_file().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def load_ui_prefs(self):
        data = self._read_state()
        self.current_theme = data.get("theme", "light")
        self.ui_scale = data.get("ui_scale", "normal")

    def _build(self):
        self.load_ui_prefs()
        self.style = ttk.Style(self)
        self.bind_all("<MouseWheel>", self._on_global_mousewheel, add="+")
        self.bind_all("<Shift-MouseWheel>", self._on_global_shift_mousewheel, add="+")
        self.bind_all("<Button-4>", self._on_global_mousewheel_linux, add="+")
        self.bind_all("<Button-5>", self._on_global_mousewheel_linux, add="+")
        self.bind_all("<Button-3>", self._on_text_context_menu, add="+")

        self.header = ttk.Frame(self, height=90)
        self.header.pack(fill="x", padx=10, pady=(6, 2))
        self.header.pack_propagate(False)

        left = ttk.Frame(self.header)
        left.pack(side="left", fill="x", expand=True)

        title_block = ttk.Frame(left)
        title_block.pack(side="left", anchor="nw")

        self.title_lbl = ttk.Label(title_block, text="Bleepling", font=("Segoe UI", 20, "bold"))
        self.title_lbl.pack(anchor="w")

        self.subtitle_lbl = ttk.Label(title_block, text="names out, privacy in", font=("Segoe UI", 10))
        self.subtitle_lbl.pack(anchor="w")

        right = ttk.Frame(self.header)
        right.pack(side="right", anchor="ne")

        self.save_btn = ttk.Button(
            right,
            text="Projekt speichern",
            command=self.save_project,
            style="Accent.TButton",
        )
        self.save_btn.pack(side="left", padx=(0, 110), pady=(60, 0), anchor="n")

        logo_path = self._asset("vogel1_logo_512.png")
        if logo_path.exists():
            img = Image.open(logo_path).resize((87, 87))
            self.logo_img = ImageTk.PhotoImage(img)
            self.logo_label = ttk.Label(self, image=self.logo_img, borderwidth=0)
            self.logo_label.place(relx=1.0, x=-18, y=12, anchor="ne")
        else:
            self.logo_label = ttk.Label(self, text="🐤")
            self.logo_label.place(relx=1.0, x=-18, y=12, anchor="ne")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        self.status = tk.StringVar(value="Bereit.")

        self.project_tab = ProjectTab(self.notebook, self)
        self.media_tab = MediaTab(self.notebook, self)
        self.cut_tab = CutTab(self.notebook, self)
        self.bleeping_tab = BleepingTab(self.notebook, self)
        self.ffmpeg_tab = FFmpegTab(self.notebook, self)
        self.targeted_edit_tab = TargetedEditTab(self.notebook, self)
        self.hit_review_tab = HitReviewTab(self.notebook, self)
        self.combined_review_tab = CombinedReviewTab(self.notebook, self)
        self.titlecards_tab = TitleCardsTab(self.notebook, self)
        self.settings_tab = SettingsTab(self.notebook, self)

        for txt, tab in [
            ("Projekt", self.project_tab),
            ("Medien", self.media_tab),
            ("Schnitt & Kapitel", self.cut_tab),
            ("Prüfen & Entscheiden", self.combined_review_tab),
            ("Video & Audio / FFmpeg", self.ffmpeg_tab),
            ("Gezielte Nachbearbeitung", self.targeted_edit_tab),
            ("Titelkarten", self.titlecards_tab),
            ("Einstellungen / Logs", self.settings_tab),
        ]:
            self.notebook.add(tab, text=txt)

        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        self.status_label = ttk.Label(self, textvariable=self.status)
        self.status_label.pack(fill="x", padx=10, pady=(0, 8))

    def _on_tab_changed(self, event=None):
        selected_tab = None
        try:
            selected_tab = self.nametowidget(self.notebook.select())
        except Exception:
            pass
        if selected_tab is not None:
            try:
                selected_tab.refresh()
            except Exception:
                pass

    def set_project(self, project):
        self.project = project
        self._on_tab_changed()
        try:
            self.remember_recent_project(project.root_path)
        except Exception:
            pass
        try:
            shown = project.root_path
        except Exception:
            shown = getattr(project, "root", "unbekannt")
        self.set_status(f"Projekt geladen: {shown}")

    def set_status(self, msg):
        self.status.set(msg)

    def _resolve_widget(self, widget):
        if isinstance(widget, str):
            try:
                return self.nametowidget(widget)
            except Exception:
                return None
        return widget

    def _is_text_context_widget(self, widget) -> bool:
        widget = self._resolve_widget(widget)
        if widget is None or not hasattr(widget, "winfo_class"):
            return False
        try:
            cls = widget.winfo_class()
        except Exception:
            return False
        return cls in {"Entry", "TEntry", "Text", "Spinbox", "TSpinbox", "Combobox", "TCombobox"}

    def _widget_state_value(self, widget) -> str:
        try:
            return str(widget.cget("state"))
        except Exception:
            return "normal"

    def _widget_has_selection(self, widget) -> bool:
        try:
            if widget.winfo_class() == "Text":
                return bool(widget.tag_ranges("sel"))
            return bool(widget.selection_present())
        except Exception:
            return False

    def _clipboard_has_text(self) -> bool:
        try:
            self.clipboard_get()
            return True
        except Exception:
            return False

    def _place_insert_at_pointer(self, widget, event):
        try:
            cls = widget.winfo_class()
            if cls == "Text":
                widget.mark_set("insert", f"@{event.x},{event.y}")
            elif cls in {"Entry", "TEntry", "Spinbox", "TSpinbox", "Combobox", "TCombobox"}:
                widget.icursor(f"@{event.x}")
        except Exception:
            pass

    def _on_text_context_menu(self, event):
        widget = self._resolve_widget(getattr(event, "widget", None))
        if not self._is_text_context_widget(widget):
            return

        try:
            widget.focus_set()
        except Exception:
            pass
        if not self._widget_has_selection(widget):
            self._place_insert_at_pointer(widget, event)

        state = self._widget_state_value(widget)
        can_edit = state not in {"disabled", "readonly"}
        has_selection = self._widget_has_selection(widget)
        has_clipboard = self._clipboard_has_text()

        menu = tk.Menu(self, tearoff=0)
        menu.add_command(
            label="Ausschneiden",
            command=lambda: widget.event_generate("<<Cut>>"),
            state="normal" if can_edit and has_selection else "disabled",
        )
        menu.add_command(
            label="Kopieren",
            command=lambda: widget.event_generate("<<Copy>>"),
            state="normal" if has_selection else "disabled",
        )
        menu.add_command(
            label="Einfügen",
            command=lambda: widget.event_generate("<<Paste>>"),
            state="normal" if can_edit and has_clipboard else "disabled",
        )
        menu.add_separator()
        menu.add_command(label="Alles auswählen", command=lambda: widget.event_generate("<<SelectAll>>"))

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            try:
                menu.grab_release()
            except Exception:
                pass
        return "break"

    def _find_scroll_target(self, widget, horizontal: bool = False):
        axis_method = "xview_scroll" if horizontal else "yview_scroll"
        while widget is not None:
            widget = self._resolve_widget(widget)
            if widget is None:
                return None
            if not hasattr(widget, "winfo_class"):
                return None
            cls = widget.winfo_class()
            if hasattr(widget, axis_method) and cls in {"Text", "Canvas", "Listbox", "Treeview"}:
                return widget
            widget = getattr(widget, "master", None)
        return None

    def _scroll_widget(self, widget, delta_units: int, horizontal: bool = False):
        if widget is None or delta_units == 0:
            return
        try:
            if horizontal:
                widget.xview_scroll(delta_units, "units")
            else:
                widget.yview_scroll(delta_units, "units")
        except Exception:
            pass

    def _widget_under_pointer(self):
        try:
            return self.winfo_containing(self.winfo_pointerx(), self.winfo_pointery())
        except Exception:
            return None

    def _on_global_mousewheel(self, event):
        widget = self._find_scroll_target(getattr(event, "widget", None) or self._widget_under_pointer(), horizontal=False)
        if widget is None:
            return
        delta = getattr(event, "delta", 0)
        units = -int(delta / 120) if delta else 0
        if units == 0 and delta:
            units = -1 if delta > 0 else 1
        self._scroll_widget(widget, units, horizontal=False)
        return "break"

    def _on_global_shift_mousewheel(self, event):
        widget = self._find_scroll_target(getattr(event, "widget", None) or self._widget_under_pointer(), horizontal=True)
        if widget is None:
            return
        delta = getattr(event, "delta", 0)
        units = -int(delta / 120) if delta else 0
        if units == 0 and delta:
            units = -1 if delta > 0 else 1
        self._scroll_widget(widget, units, horizontal=True)
        return "break"

    def _on_global_mousewheel_linux(self, event):
        widget = self._find_scroll_target(getattr(event, "widget", None) or self._widget_under_pointer(), horizontal=False)
        if widget is None:
            return
        num = getattr(event, "num", None)
        units = -1 if num == 4 else 1 if num == 5 else 0
        self._scroll_widget(widget, units, horizontal=False)
        return "break"

    def _is_danger_button(self, widget) -> bool:
        try:
            bg = str(widget.cget("bg")).lower()
        except Exception:
            bg = ""
        return bg in {"#c62828", "#b71c1c", "#b94a48", "#a53f3d", "#c85b57"}

    def _style_classic_button(self, widget):
        is_danger = self._is_danger_button(widget)
        normal_bg = "#c62828" if is_danger else self.btn_bg
        hover_bg = "#b71c1c" if is_danger else self.btn_active
        normal_fg = "white" if is_danger else self.fg
        hover_fg = "white"
        try:
            widget.configure(
                bg=normal_bg,
                fg=normal_fg,
                activebackground=hover_bg,
                activeforeground=hover_fg,
                highlightbackground=self.border,
                highlightcolor=self.border,
                disabledforeground=self.disabled_fg,
                relief="raised",
                bd=1,
                cursor="hand2",
            )
        except Exception:
            return

        def _enter(_event):
            try:
                widget.configure(bg=hover_bg, fg=hover_fg)
            except Exception:
                pass

        def _leave(_event):
            try:
                widget.configure(bg=normal_bg, fg=normal_fg)
            except Exception:
                pass

        try:
            widget.bind("<Enter>", _enter, add="+")
            widget.bind("<Leave>", _leave, add="+")
        except Exception:
            pass

    def save_project(self):
        if not self.project:
            self.set_status("Kein Projekt geladen.")
            return
        try:
            if hasattr(self.bleeping_tab, "save_lists"):
                self.bleeping_tab.save_lists()
            if hasattr(self.settings_tab, "save_settings"):
                self.settings_tab.save_settings()
            self.set_status("Projekt gespeichert.")
        except Exception as e:
            self.set_status(f"Projekt speichern fehlgeschlagen: {e}")

    def set_running(self, is_running: bool):
        if is_running:
            self.style.configure("Accent.TButton", background="#b94a48", foreground="white")
            self.style.map(
                "Accent.TButton",
                background=[("active", "#b94a48"), ("pressed", "#a53f3d")],
                foreground=[("active", "white")],
            )
        else:
            self.style.configure("Accent.TButton", background=self.btn_bg, foreground=self.fg)
            self.style.map(
                "Accent.TButton",
                background=[("active", self.btn_active), ("pressed", self.btn_active)],
                foreground=[("active", self.fg)],
            )

    def apply_ui_scale(self, ui_scale: str):
        self.ui_scale = ui_scale
        scale_map = {
            "normal": {"base": 10, "small": 9, "title": 20},
            "etwas größer": {"base": 11, "small": 10, "title": 22},
            "groß": {"base": 12, "small": 11, "title": 24},
        }
        vals = scale_map.get(ui_scale, scale_map["normal"])
        self.title_lbl.configure(font=("Segoe UI", vals["title"], "bold"))
        self.subtitle_lbl.configure(font=("Segoe UI", vals["small"]))
        try:
            self.style.configure(".", font=("Segoe UI", vals["base"]))
            self.style.configure("TButton", font=("Segoe UI", vals["base"]))
            self.style.configure("Accent.TButton", font=("Segoe UI", vals["base"]))
            self.style.configure("TLabel", font=("Segoe UI", vals["base"]))
            self.style.configure("TNotebook.Tab", font=("Segoe UI", vals["base"]))
            self.style.configure("Treeview", font=("Segoe UI", vals["base"]))
            self.style.configure("Treeview.Heading", font=("Segoe UI", vals["base"]))
            self.style.configure("TEntry", font=("Segoe UI", vals["base"]))
            self.style.configure("TCombobox", font=("Segoe UI", vals["base"]))
            self.style.configure("TLabelFrame.Label", font=("Segoe UI", vals["base"]))
        except Exception:
            pass

        def apply_fonts(widget):
            for child in widget.winfo_children():
                cls = child.winfo_class()
                try:
                    if cls in ("Text", "Entry", "Listbox"):
                        child.configure(font=("Segoe UI", vals["base"]))
                except Exception:
                    pass
                apply_fonts(child)

        apply_fonts(self)
        self.header.configure(height=98 if ui_scale == "normal" else 106 if ui_scale == "etwas größer" else 114)
        try:
            self.update_idletasks()
        except Exception:
            pass

    def apply_theme(self, theme_name: str):
        self.current_theme = theme_name
        if theme_name == "dark":
            bg = "#283442"
            fg = "#ffffff"
            fieldbg = "#324154"
            readonly_bg = "#3a495c"
            disabled_bg = "#425164"
            disabled_fg = "#d0d6df"
            select_bg = "#4f6580"
            border = "#455A75"
            btn_bg = "#3a495c"
            btn_active = "#b94a48"
        else:
            bg = "#ffffff"
            fg = "#000000"
            fieldbg = "#ffffff"
            readonly_bg = "#ffffff"
            disabled_bg = "#f0f0f0"
            disabled_fg = "#6a6a6a"
            select_bg = "#cfe8ff"
            border = "#000000"
            btn_bg = "#f0f0f0"
            btn_active = "#c85b57"

        self.btn_bg = btn_bg
        self.btn_active = btn_active
        self.fg = fg
        self.border = border
        self.disabled_fg = disabled_fg

        self.configure(bg=bg)
        self.style.theme_use("clam")
        self.style.configure(".", background=bg, foreground=fg, fieldbackground=fieldbg, bordercolor=border)
        self.style.configure("TFrame", background=bg)
        self.style.configure("TLabel", background=bg, foreground=fg)
        self.style.configure("TLabelFrame", background=bg, foreground=fg, bordercolor=border)
        self.style.configure("TLabelFrame.Label", background=bg, foreground=fg)
        self.style.configure("TNotebook", background=bg, bordercolor=border)
        self.style.configure("TNotebook.Tab", background=btn_bg, foreground=fg, bordercolor=border)
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", bg), ("active", btn_bg)],
            foreground=[("selected", fg)],
        )

        self.style.configure("TButton", background=btn_bg, foreground=fg, bordercolor=border, relief="solid")
        self.style.map(
            "TButton",
            background=[("active", btn_active), ("pressed", btn_active)],
            foreground=[("active", "white")],
        )
        self.style.configure("Accent.TButton", background=btn_bg, foreground=fg, bordercolor=border, relief="solid")
        self.style.map(
            "Accent.TButton",
            background=[("active", btn_active), ("pressed", btn_active)],
            foreground=[("active", "white")],
        )

        self.style.configure("TEntry", fieldbackground=fieldbg, foreground=fg, insertcolor=fg, bordercolor=border)
        self.style.configure("TCombobox", fieldbackground=fieldbg, foreground=fg, arrowcolor=fg, bordercolor=border)
        self.style.map(
            "TCombobox",
            fieldbackground=[("readonly", readonly_bg), ("disabled", disabled_bg)],
            foreground=[("readonly", fg), ("disabled", disabled_fg)],
            arrowcolor=[("readonly", fg), ("disabled", disabled_fg)],
        )

        self.style.configure("Treeview", background=fieldbg, foreground=fg, fieldbackground=fieldbg)
        self.style.configure("Treeview.Heading", background=btn_bg, foreground=fg)

        try:
            self.option_add("*TCombobox*Listbox.background", fieldbg)
            self.option_add("*TCombobox*Listbox.foreground", fg)
            self.option_add("*TCombobox*Listbox.selectBackground", select_bg)
            self.option_add("*TCombobox*Listbox.selectForeground", fg)
        except Exception:
            pass

        def apply_to_children(widget):
            for child in widget.winfo_children():
                cls = child.winfo_class()
                try:
                    if cls in ("Text", "Listbox"):
                        child.configure(
                            bg=fieldbg,
                            fg=fg,
                            insertbackground=fg,
                            highlightbackground=border,
                            highlightcolor=border,
                            selectbackground=select_bg,
                            selectforeground=fg,
                        )
                    elif cls == "Canvas":
                        child.configure(bg=bg, highlightbackground=border)
                    elif cls == "Entry":
                        child.configure(
                            bg=fieldbg,
                            fg=fg,
                            insertbackground=fg,
                            disabledbackground=disabled_bg,
                            disabledforeground=disabled_fg,
                            highlightbackground=border,
                            highlightcolor=border,
                        )
                    elif cls == "Button":
                        self._style_classic_button(child)
                except Exception:
                    pass
                apply_to_children(child)

        apply_to_children(self)
        self.apply_ui_scale(self.ui_scale)

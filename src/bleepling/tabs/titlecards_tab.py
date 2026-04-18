from __future__ import annotations

import json
import os
import re
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageDraw, ImageFont, ImageTk

CANVAS_W = 1920
CANVAS_H = 1080

COLORS = {
    "Weiß": "#FFFFFF",
    "Schwarz": "#111111",
    "Rot": "#B63A4C",
    "Dunkelgrau": "#374151",
    "Grün": "#007A4D",
    "Blau": "#1D4ED8",
    "Hellgrau": "#D1D5DB",
}

ALIGNMENTS = {
    "Linksbündig": "left",
    "Zentriert": "center",
    "Rechtsbündig": "right",
}

PREFERRED_FONTS = [
    "Arial",
    "Calibri",
    "Bahnschrift",
    "Segoe UI",
    "Verdana",
    "Tahoma",
    "Trebuchet MS",
    "Times New Roman",
    "Georgia",
    "Cambria",
]

TITLE_LINE_SPACING_FACTOR = 0.28


def sanitize_filename(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text.strip())
    cleaned = re.sub(r'[\\/:*?"<>|]', "", cleaned)
    cleaned = cleaned[:30].strip().replace(" ", "_")
    return f"{cleaned or 'titelkarte'}.png"


def fit_contain(src_w: int, src_h: int, dst_w: int, dst_h: int, padding: int = 0):
    inner_w = max(1, dst_w - 2 * padding)
    inner_h = max(1, dst_h - 2 * padding)
    scale = min(inner_w / src_w, inner_h / src_h)
    w = max(1, round(src_w * scale))
    h = max(1, round(src_h * scale))
    x = round((dst_w - w) / 2)
    y = round((dst_h - h) / 2)
    return x, y, w, h


def fit_cover(src_w: int, src_h: int, dst_w: int, dst_h: int):
    scale = max(dst_w / src_w, dst_h / src_h)
    w = max(1, round(src_w * scale))
    h = max(1, round(src_h * scale))
    x = round((dst_w - w) / 2)
    y = round((dst_h - h) / 2)
    return x, y, w, h


def normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def build_font_catalog(root: tk.Misc):
    fonts_dir = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    files = []
    if fonts_dir.exists():
        files = [p for p in fonts_dir.iterdir() if p.suffix.lower() in {".ttf", ".otf", ".ttc"}]

    file_index: dict[str, list[Path]] = {}
    for file in files:
        stem = normalize_name(file.stem)
        file_index.setdefault(stem, []).append(file)

    families = sorted(set(tkfont.families(root)))
    preferred = [f for f in PREFERRED_FONTS if f in families]
    others = [f for f in families if f not in preferred]
    ordered = preferred + sorted(others, key=str.lower)
    return ordered, file_index


def resolve_font_file(font_family: str, file_index: dict[str, list[Path]], bold: bool = False, italic: bool = False):
    normalized = normalize_name(font_family)
    candidates: list[Path] = []

    for stem, paths in file_index.items():
        if normalized and normalized in stem:
            candidates.extend(paths)

    if not candidates and normalized:
        prefix = normalized[:6]
        for stem, paths in file_index.items():
            if stem.startswith(prefix) or prefix.startswith(stem[:6]):
                candidates.extend(paths)

    if not candidates:
        return None

    def _is_bold_style(stem: str) -> bool:
        return any(x in stem for x in ["bold", "semibold", "demi"]) or stem.endswith(("bd", "b"))

    def _is_italic_style(stem: str) -> bool:
        return any(x in stem for x in ["italic", "oblique", "kursiv"]) or stem.endswith(("it", "i"))

    def score(path: Path):
        stem = normalize_name(path.stem)
        s = 0
        if normalized in stem:
            s += 10
        stem_is_bold = _is_bold_style(stem)
        stem_is_italic = _is_italic_style(stem)
        if bold:
            s += 8 if stem_is_bold else -4
        elif stem_is_bold:
            s -= 3
        if italic:
            s += 8 if stem_is_italic else -4
        elif stem_is_italic:
            s -= 3
        if not bold and not italic and not stem_is_bold and not stem_is_italic:
            s += 5
        return s

    candidates = sorted(candidates, key=score, reverse=True)
    return str(candidates[0])


def load_font(font_family: str, size: int, file_index: dict[str, list[Path]], bold: bool = False, italic: bool = False):
    try:
        font_path = resolve_font_file(font_family, file_index, bold=bold, italic=italic)
        if font_path:
            return ImageFont.truetype(font_path, size=size)
        return ImageFont.truetype(font_family, size=size)
    except Exception:
        try:
            return ImageFont.truetype("arial.ttf", size=size)
        except Exception:
            return ImageFont.load_default()


def draw_text_with_style(
    base_image: Image.Image,
    position: tuple[float, float],
    text: str,
    font,
    fill: str,
    italic: bool = False,
):
    x, y = position
    if not italic:
        ImageDraw.Draw(base_image).text((x, y), text, fill=fill, font=font)
        return

    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1), (0, 0, 0, 0)))
    bbox = probe.textbbox((0, 0), text, font=font)
    width = max(1, bbox[2] - bbox[0])
    height = max(1, bbox[3] - bbox[1])
    shear = 0.22
    pad = max(4, round(height * shear) + 6)
    layer = Image.new("RGBA", (width + pad * 2, height + pad * 2), (0, 0, 0, 0))
    layer_draw = ImageDraw.Draw(layer)
    layer_draw.text((pad - bbox[0], pad - bbox[1]), text, fill=fill, font=font)
    sheared = layer.transform(
        (layer.width + round(layer.height * shear), layer.height),
        Image.AFFINE,
        (1, shear, 0, 0, 1, 0),
        resample=Image.BICUBIC,
    )
    base_image.alpha_composite(
        sheared,
        (
            int(round(x + bbox[0] - pad)),
            int(round(y + bbox[1] - pad)),
        ),
    )


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int):
    if not text:
        return [""]
    paragraphs = text.splitlines()
    if not paragraphs:
        return [""]
    lines: list[str] = []
    for paragraph in paragraphs:
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            candidate = current + " " + word
            bbox = draw.textbbox((0, 0), candidate, font=font)
            width = bbox[2] - bbox[0]
            if width <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
    if not lines:
        return [""]
    return lines


def fit_text_block(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_family: str,
    file_index: dict[str, list[Path]],
    start_size: int,
    min_size: int,
    max_width: int,
    max_height: int,
    max_lines: int | None,
    bold: bool,
    italic: bool,
):
    for size in range(start_size, min_size - 1, -2):
        # Kursiv wird in diesem Reiter bewusst über die sichtbare Schrägstellung
        # beim Zeichnen erzeugt, nicht über wechselnde System-Fontvarianten.
        font = load_font(font_family, size, file_index, bold=bold, italic=False)
        lines = wrap_text(draw, text, font, max_width)
        if max_lines is not None and len(lines) > max_lines:
            continue
        line_heights = []
        max_line_width = 0
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            max_line_width = max(max_line_width, bbox[2] - bbox[0])
            line_heights.append(bbox[3] - bbox[1])
        total_height = sum(line_heights) + max(0, len(lines) - 1) * round(size * TITLE_LINE_SPACING_FACTOR)
        if max_line_width <= max_width and total_height <= max_height:
            return font, lines, size
    font = load_font(font_family, min_size, file_index, bold=bold, italic=False)
    lines = wrap_text(draw, text, font, max_width)
    if max_lines is not None:
        lines = lines[:max_lines]
    return font, lines, min_size


class TitleCardsTab(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self._suspend_preview_updates = False
        self.background_image = None
        self.background_image_path = ""
        self.left_logo = None
        self.left_logo_path = ""
        self.partner_logo = None
        self.partner_logo_path = ""
        self.preview_photo = None

        self.font_names, self.font_file_index = build_font_catalog(self.winfo_toplevel())
        default_font = "Arial" if "Arial" in self.font_names else (self.font_names[0] if self.font_names else "TkDefaultFont")

        self.reihe_var = tk.StringVar(value="")
        self.subtitle_var = tk.StringVar(value="")
        self.use_background_var = tk.BooleanVar(value=False)
        self.show_footer_var = tk.BooleanVar(value=True)
        self.show_title_box_var = tk.BooleanVar(value=True)

        self.title_size_var = tk.IntVar(value=64)
        self.header_size_var = tk.IntVar(value=42)
        self.subtitle_size_var = tk.IntVar(value=52)
        self.header_y_var = tk.IntVar(value=130)
        self.subtitle_y_var = tk.IntVar(value=220)
        self.title_box_y_var = tk.IntVar(value=360)
        self.title_box_width_var = tk.IntVar(value=1140)
        self.title_box_height_var = tk.IntVar(value=320)

        self.title_color_var = tk.StringVar(value="Weiß")
        self.header_color_var = tk.StringVar(value="Rot")
        self.subtitle_color_var = tk.StringVar(value="Rot")
        self.box_color_var = tk.StringVar(value="Rot")
        self.align_var = tk.StringVar(value="Zentriert")
        self.font_var = tk.StringVar(value=default_font)
        self.header_bold_var = tk.BooleanVar(value=False)
        self.header_italic_var = tk.BooleanVar(value=False)
        self.header_hidden_var = tk.BooleanVar(value=False)
        self.subtitle_bold_var = tk.BooleanVar(value=True)
        self.subtitle_italic_var = tk.BooleanVar(value=False)
        self.subtitle_hidden_var = tk.BooleanVar(value=False)
        self.bold_var = tk.BooleanVar(value=False)
        self.italic_var = tk.BooleanVar(value=False)
        self.export_name_var = tk.StringVar(value="titelkarte.png")
        self.status_var = tk.StringVar(value="Bereit.")

        self._build_ui()
        self._bind_events()
        self.reset_demo(initial=True)

    def _request_preview_update(self):
        if self._suspend_preview_updates:
            return
        self.update_preview()

    def _build_ui(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        left_wrap = ttk.Frame(self)
        left_wrap.grid(row=0, column=0, sticky="ns", padx=(12, 8), pady=12)
        right_wrap = ttk.Frame(self)
        right_wrap.grid(row=0, column=1, sticky="nsew", padx=(8, 12), pady=12)
        right_wrap.rowconfigure(1, weight=1)
        right_wrap.columnconfigure(0, weight=1)

        self.ctrl_canvas = tk.Canvas(left_wrap, width=560, highlightthickness=0)
        self.ctrl_scroll = ttk.Scrollbar(left_wrap, orient="vertical", command=self.ctrl_canvas.yview)
        self.ctrl_inner = ttk.Frame(self.ctrl_canvas)

        self.ctrl_inner.bind("<Configure>", lambda e: self.ctrl_canvas.configure(scrollregion=self.ctrl_canvas.bbox("all")))
        self.ctrl_canvas.create_window((0, 0), window=self.ctrl_inner, anchor="nw")
        self.ctrl_canvas.configure(yscrollcommand=self.ctrl_scroll.set)

        self.ctrl_canvas.pack(side="left", fill="y", expand=False)
        self.ctrl_scroll.pack(side="right", fill="y")

        ttk.Label(self.ctrl_inner, text="Titelkarten", font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(0, 6))

        self._add_file_section("Grundlayout", "Ganzflächiges Hintergrundbild", self.choose_background, self.clear_background)
        ttk.Checkbutton(self.ctrl_inner, text="Hintergrundbild als Grundlayout verwenden", variable=self.use_background_var, command=self.update_preview).pack(anchor="w", pady=(2, 2))
        ttk.Checkbutton(self.ctrl_inner, text="Generierte Logos unten zusätzlich anzeigen", variable=self.show_footer_var, command=self.update_preview).pack(anchor="w", pady=(0, 8))

        self._add_entry("Reihe / Dachzeile", self.reihe_var)
        header_style_row = ttk.Frame(self.ctrl_inner)
        header_style_row.pack(fill="x", pady=(4, 0))
        ttk.Checkbutton(header_style_row, text="Fett Dachzeile", variable=self.header_bold_var, command=self.update_preview).pack(side="left")
        ttk.Checkbutton(header_style_row, text="Kursiv Dachzeile", variable=self.header_italic_var, command=self.update_preview).pack(side="left", padx=(16, 0))
        ttk.Checkbutton(header_style_row, text="Dachzeile ausblenden", variable=self.header_hidden_var, command=self.update_preview).pack(side="left", padx=(16, 0))

        self._add_entry("Zweite Dachzeile / Untertitel", self.subtitle_var)
        subtitle_style_row = ttk.Frame(self.ctrl_inner)
        subtitle_style_row.pack(fill="x", pady=(4, 0))
        ttk.Checkbutton(subtitle_style_row, text="Fett 2. Dachzeile", variable=self.subtitle_bold_var, command=self.update_preview).pack(side="left")
        ttk.Checkbutton(subtitle_style_row, text="Kursiv 2. Dachzeile", variable=self.subtitle_italic_var, command=self.update_preview).pack(side="left", padx=(16, 0))
        ttk.Checkbutton(subtitle_style_row, text="2. Dachzeile ausblenden", variable=self.subtitle_hidden_var, command=self.update_preview).pack(side="left", padx=(16, 0))

        ttk.Label(self.ctrl_inner, text="Titel", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(8, 2))
        self.title_text = tk.Text(self.ctrl_inner, width=44, height=4, wrap="word")
        self.title_text.pack(fill="x")
        self.title_text.insert("1.0", "")
        self.title_text.bind("<KeyRelease>", lambda _e: self._sync_title_from_text())

        opt_row = ttk.Frame(self.ctrl_inner)
        opt_row.pack(fill="x", pady=(8, 4))
        ttk.Checkbutton(opt_row, text="Titelbox anzeigen", variable=self.show_title_box_var, command=self.update_preview).pack(side="left")
        ttk.Checkbutton(opt_row, text="Fett Titel", variable=self.bold_var, command=self.update_preview).pack(side="left", padx=(16, 0))
        ttk.Checkbutton(opt_row, text="Kursiv Titel", variable=self.italic_var, command=self.update_preview).pack(side="left", padx=(16, 0))

        grid = ttk.Frame(self.ctrl_inner)
        grid.pack(fill="x", pady=(4, 0))
        for i in range(3):
            grid.columnconfigure(i, weight=1)

        ttk.Label(grid, text="Reihe / Dachzeile", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=(0, 2))
        ttk.Label(grid, text="Zweite Dachzeile", font=("Segoe UI", 9, "bold")).grid(row=0, column=1, sticky="w", padx=(0, 8), pady=(0, 2))
        ttk.Label(grid, text="Titelbox", font=("Segoe UI", 9, "bold")).grid(row=0, column=2, sticky="w", pady=(0, 2))

        self._grid_stack_spinbox(grid, 1, 0, "Schriftgröße Dachzeile", self.header_size_var, 20, 90)
        self._grid_stack_spinbox(grid, 2, 0, "Y-Position Dachzeile", self.header_y_var, 60, 420)
        self._grid_stack_combo(grid, 3, 0, "Textfarbe Dachzeile", self.header_color_var, list(COLORS.keys()))
        self._grid_stack_combo(grid, 4, 0, "Ausrichtung Titel", self.align_var, list(ALIGNMENTS.keys()))

        self._grid_stack_spinbox(grid, 1, 1, "Schriftgröße 2. Dachzeile", self.subtitle_size_var, 16, 90)
        self._grid_stack_spinbox(grid, 2, 1, "Y-Position 2. Dachzeile", self.subtitle_y_var, 80, 520)
        self._grid_stack_combo(grid, 3, 1, "Textfarbe 2. Dachzeile", self.subtitle_color_var, list(COLORS.keys()))
        self._grid_stack_combo(grid, 4, 1, "Schriftart", self.font_var, self.font_names)

        self._grid_stack_spinbox(grid, 1, 2, "Schriftgröße Titel", self.title_size_var, 24, 120)
        self._grid_stack_spinbox(grid, 2, 2, "Y-Position Titelbox", self.title_box_y_var, 220, 700)
        self._grid_stack_spinbox(grid, 3, 2, "Breite Titelbox", self.title_box_width_var, 600, 1500)
        self._grid_stack_spinbox(grid, 4, 2, "Höhe Titelbox", self.title_box_height_var, 180, 620)
        self._grid_stack_combo(grid, 5, 0, "Textfarbe Titel", self.title_color_var, list(COLORS.keys()))
        self._grid_stack_combo(grid, 5, 1, "Farbe Titelbox", self.box_color_var, list(COLORS.keys()))

        self._add_file_section("Logos", "Logo links unten", self.choose_left_logo, self.clear_left_logo)
        self._add_file_section(None, "Partnerlogo rechts unten", self.choose_partner_logo, self.clear_partner_logo)

        ttk.Label(self.ctrl_inner, text="Export", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(8, 2))
        self._add_entry("Export-Dateiname", self.export_name_var, pady=(0, 2))
        ttk.Label(self.ctrl_inner, text="Vorschlag aus den ersten 30 Zeichen des Titels. Der Name bleibt frei editierbar.", wraplength=390, foreground="#4b5563").pack(anchor="w", pady=(0, 8))

        btn_row = ttk.Frame(self.ctrl_inner)
        btn_row.pack(fill="x", pady=(4, 4))
        ttk.Button(btn_row, text="In Projekt exportieren", command=self.export_to_project).pack(side="left")
        ttk.Button(btn_row, text="PNG exportieren unter …", command=self.export_png).pack(side="left", padx=(8, 0))
        ttk.Button(btn_row, text="Zurücksetzen", command=self.reset_demo).pack(side="left", padx=(8, 0))

        ttk.Label(self.ctrl_inner, textvariable=self.status_var, wraplength=390, foreground="#4b5563").pack(anchor="w", pady=(4, 8))

        ttk.Label(right_wrap, text="Live-Vorschau", font=("Segoe UI", 13, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.preview_canvas = tk.Canvas(right_wrap, highlightthickness=0, background="#f3f4f6")
        self.preview_canvas.grid(row=1, column=0, sticky="nsew")
        self.preview_canvas.bind("<Configure>", lambda _e: self._request_preview_update())
        ttk.Label(
            right_wrap,
            text="Es werden die lokal verfügbaren Systemschriftarten des jeweiligen Rechners angeboten. Schriftlizenzen sind vom Anwender selbst zu prüfen.",
            wraplength=1180,
            foreground="#7c2d12",
            justify="left",
        ).grid(row=2, column=0, sticky="w", pady=(8, 0))

    def _bind_events(self):
        self.reihe_var.trace_add("write", lambda *_: self._request_preview_update())
        self.subtitle_var.trace_add("write", lambda *_: self._request_preview_update())
        for var in (
            self.title_size_var,
            self.header_size_var,
            self.subtitle_size_var,
            self.header_y_var,
            self.subtitle_y_var,
            self.title_box_y_var,
            self.title_box_width_var,
            self.title_box_height_var,
            self.title_color_var,
            self.header_color_var,
            self.subtitle_color_var,
            self.box_color_var,
            self.align_var,
            self.font_var,
            self.header_bold_var,
            self.header_italic_var,
            self.header_hidden_var,
            self.subtitle_bold_var,
            self.subtitle_italic_var,
            self.subtitle_hidden_var,
            self.bold_var,
            self.italic_var,
            self.use_background_var,
            self.show_footer_var,
            self.show_title_box_var,
        ):
            var.trace_add("write", lambda *_: self._request_preview_update())

    def _add_entry(self, label, variable, pady=(8, 2)):
        ttk.Label(self.ctrl_inner, text=label).pack(anchor="w", pady=pady)
        ttk.Entry(self.ctrl_inner, textvariable=variable, width=44).pack(fill="x")

    def _add_file_section(self, section_title, label, choose_cmd, clear_cmd):
        if section_title:
            ttk.Label(self.ctrl_inner, text=section_title, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(12, 2))
        ttk.Label(self.ctrl_inner, text=label).pack(anchor="w", pady=(6, 2))
        row = ttk.Frame(self.ctrl_inner)
        row.pack(fill="x")
        ttk.Button(row, text="Bild wählen", command=choose_cmd).pack(side="left")
        ttk.Button(row, text="Entfernen", command=clear_cmd).pack(side="left", padx=(8, 0))

    def _grid_spinbox(self, parent, row, col, label, variable, minval, maxval):
        box = ttk.Frame(parent)
        box.grid(row=row, column=col, sticky="ew", padx=(0 if col == 0 else 8, 0), pady=4)
        ttk.Label(box, text=label).pack(anchor="w")
        ttk.Spinbox(box, from_=minval, to=maxval, textvariable=variable, width=12).pack(anchor="w")

    def _grid_combo(self, parent, row, col, label, variable, values):
        box = ttk.Frame(parent)
        box.grid(row=row, column=col, sticky="ew", padx=(0 if col == 0 else 8, 0), pady=4)
        ttk.Label(box, text=label).pack(anchor="w")
        ttk.Combobox(box, textvariable=variable, values=values, state="readonly", width=28).pack(anchor="w")

    def _grid_stack_spinbox(self, parent, row, col, label, variable, minval, maxval):
        box = ttk.Frame(parent)
        box.grid(row=row, column=col, sticky="ew", padx=(0 if col == 0 else 8, 0), pady=2)
        ttk.Label(box, text=label).pack(anchor="w")
        ttk.Spinbox(box, from_=minval, to=maxval, textvariable=variable, width=14).pack(anchor="w")

    def _grid_stack_combo(self, parent, row, col, label, variable, values):
        box = ttk.Frame(parent)
        box.grid(row=row, column=col, sticky="ew", padx=(0 if col == 0 else 8, 0), pady=2)
        ttk.Label(box, text=label).pack(anchor="w")
        ttk.Combobox(box, textvariable=variable, values=values, state="readonly", width=18).pack(anchor="w", fill="x")

    def _sync_title_from_text(self):
        title_value = self.title_text.get("1.0", "end-1c").strip()
        self.export_name_var.set(sanitize_filename(title_value) if title_value else "titelkarte.png")
        self._request_preview_update()

    def _state_path(self):
        project = getattr(self.app, "project", None)
        if not project:
            return None
        if hasattr(project, "config_dir"):
            return project.config_dir / "titlecards_state.json"
        root_path = Path(getattr(project, "root_path", ""))
        return root_path / "99_config" / "titlecards_state.json"

    def _output_dir(self):
        project = getattr(self.app, "project", None)
        if not project:
            return None
        root_path = Path(getattr(project, "root_path", ""))
        out_dir = root_path / "04_output" / "titlecards"
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir

    def _load_img(self, path: str):
        if path and Path(path).exists():
            return Image.open(path).convert("RGBA")
        return None

    def load_state(self):
        path = self._state_path()
        if not path or not path.exists():
            return
        try:
            self._suspend_preview_updates = True
            data = json.loads(path.read_text(encoding="utf-8"))
            self.reihe_var.set(data.get("reihe", ""))
            self.subtitle_var.set(data.get("subtitle", ""))
            self.title_text.delete("1.0", "end")
            self.title_text.insert("1.0", data.get("titel", ""))
            self.use_background_var.set(bool(data.get("use_background", False)))
            self.show_footer_var.set(bool(data.get("show_footer", True)))
            self.show_title_box_var.set(bool(data.get("show_title_box", True)))
            self.title_size_var.set(int(data.get("title_size", 64)))
            self.header_size_var.set(int(data.get("header_size", 42)))
            self.subtitle_size_var.set(int(data.get("subtitle_size", 52)))
            self.header_y_var.set(int(data.get("header_y", 130)))
            self.subtitle_y_var.set(int(data.get("subtitle_y", 220)))
            self.title_box_y_var.set(int(data.get("title_box_y", 360)))
            self.title_box_width_var.set(int(data.get("title_box_width", 1140)))
            self.title_box_height_var.set(int(data.get("title_box_height", 320)))
            self.title_color_var.set(data.get("title_color", "Weiß"))
            self.header_color_var.set(data.get("header_color", "Rot"))
            self.subtitle_color_var.set(data.get("subtitle_color", "Rot"))
            self.box_color_var.set(data.get("box_color", "Rot"))
            self.align_var.set(data.get("align", "Zentriert"))
            self.font_var.set(data.get("font", self.font_var.get()))
            self.header_bold_var.set(bool(data.get("header_bold", False)))
            self.header_italic_var.set(bool(data.get("header_italic", False)))
            self.header_hidden_var.set(bool(data.get("header_hidden", False)))
            self.subtitle_bold_var.set(bool(data.get("subtitle_bold", True)))
            self.subtitle_italic_var.set(bool(data.get("subtitle_italic", False)))
            self.subtitle_hidden_var.set(bool(data.get("subtitle_hidden", False)))
            self.bold_var.set(bool(data.get("bold", False)))
            self.italic_var.set(bool(data.get("italic", False)))
            self.background_image_path = data.get("background_image_path", "")
            self.left_logo_path = data.get("left_logo_path", "")
            self.partner_logo_path = data.get("partner_logo_path", "")
            self.background_image = self._load_img(self.background_image_path)
            self.left_logo = self._load_img(self.left_logo_path)
            self.partner_logo = self._load_img(self.partner_logo_path)
            title_value = self.title_text.get("1.0", "end-1c").strip()
            self.export_name_var.set(data.get("export_filename", sanitize_filename(title_value) if title_value else "titelkarte.png"))
            self.status_var.set("Titelkarten-Stand geladen.")
        except Exception as exc:
            self.status_var.set(f"Laden fehlgeschlagen: {exc}")
        finally:
            self._suspend_preview_updates = False
        if self.status_var.get() == "Titelkarten-Stand geladen.":
            self.update_preview()

    def save_state(self):
        path = self._state_path()
        if not path:
            return
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "reihe": self.reihe_var.get(),
                "subtitle": self.subtitle_var.get(),
                "titel": self.title_text.get("1.0", "end-1c"),
                "use_background": self.use_background_var.get(),
                "show_footer": self.show_footer_var.get(),
                "show_title_box": self.show_title_box_var.get(),
                "title_size": self.title_size_var.get(),
                "header_size": self.header_size_var.get(),
                "subtitle_size": self.subtitle_size_var.get(),
                "header_y": self.header_y_var.get(),
                "subtitle_y": self.subtitle_y_var.get(),
                "title_box_y": self.title_box_y_var.get(),
                "title_box_width": self.title_box_width_var.get(),
                "title_box_height": self.title_box_height_var.get(),
                "title_color": self.title_color_var.get(),
                "header_color": self.header_color_var.get(),
                "subtitle_color": self.subtitle_color_var.get(),
                "box_color": self.box_color_var.get(),
                "align": self.align_var.get(),
                "font": self.font_var.get(),
                "header_bold": self.header_bold_var.get(),
                "header_italic": self.header_italic_var.get(),
                "header_hidden": self.header_hidden_var.get(),
                "subtitle_bold": self.subtitle_bold_var.get(),
                "subtitle_italic": self.subtitle_italic_var.get(),
                "subtitle_hidden": self.subtitle_hidden_var.get(),
                "bold": self.bold_var.get(),
                "italic": self.italic_var.get(),
                "background_image_path": self.background_image_path,
                "left_logo_path": self.left_logo_path,
                "partner_logo_path": self.partner_logo_path,
                "export_filename": self.export_name_var.get(),
            }
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as exc:
            self.status_var.set(f"Speichern des Titelkarten-Status fehlgeschlagen: {exc}")

    def choose_background(self):
        path = filedialog.askopenfilename(filetypes=[("Bilddateien", "*.png *.jpg *.jpeg *.bmp *.webp")])
        if path:
            self.background_image_path = path
            self.background_image = Image.open(path).convert("RGBA")
            self._request_preview_update()

    def clear_background(self):
        self.background_image = None
        self.background_image_path = ""
        self._request_preview_update()

    def choose_left_logo(self):
        path = filedialog.askopenfilename(filetypes=[("Bilddateien", "*.png *.jpg *.jpeg *.bmp *.webp")])
        if path:
            self.left_logo_path = path
            self.left_logo = Image.open(path).convert("RGBA")
            self._request_preview_update()

    def clear_left_logo(self):
        self.left_logo = None
        self.left_logo_path = ""
        self._request_preview_update()

    def choose_partner_logo(self):
        path = filedialog.askopenfilename(filetypes=[("Bilddateien", "*.png *.jpg *.jpeg *.bmp *.webp")])
        if path:
            self.partner_logo_path = path
            self.partner_logo = Image.open(path).convert("RGBA")
            self._request_preview_update()

    def clear_partner_logo(self):
        self.partner_logo = None
        self.partner_logo_path = ""
        self._request_preview_update()

    def _draw_neutral_slot(self, draw: ImageDraw.ImageDraw, box, label: str):
        x1, y1, x2, y2 = box
        draw.rounded_rectangle(box, radius=10, outline="#CBD5E1", width=2, fill="#F8FAFC")
        slot_font = load_font(self.font_var.get(), 20, self.font_file_index)
        bbox = draw.textbbox((0, 0), label, font=slot_font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text((x1 + (x2 - x1 - tw) / 2, y1 + (y2 - y1 - th) / 2), label, fill="#94A3B8", font=slot_font)

    def _draw_neutral_text_slot(self, draw: ImageDraw.ImageDraw, box, label: str):
        x1, y1, x2, y2 = box
        draw.rounded_rectangle(box, radius=14, outline="#D1D5DB", width=2, fill="#F9FAFB")
        slot_font = load_font(self.font_var.get(), 20, self.font_file_index)
        bbox = draw.textbbox((0, 0), label, font=slot_font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text((x1 + (x2 - x1 - tw) / 2, y1 + (y2 - y1 - th) / 2), label, fill="#9CA3AF", font=slot_font)

    def render_image(self, show_placeholders: bool = True):
        img = Image.new("RGBA", (CANVAS_W, CANVAS_H), "#F3F4F6")
        draw = ImageDraw.Draw(img)

        title_box_w = self.title_box_width_var.get()
        title_box_h = self.title_box_height_var.get()
        title_box_x = int((CANVAS_W - title_box_w) / 2)
        title_box_y = self.title_box_y_var.get()
        title_box = (title_box_x, title_box_y, title_box_x + title_box_w, title_box_y + title_box_h)
        header_box = (420, self.header_y_var.get() - 22, CANVAS_W - 420, self.header_y_var.get() + 44)
        subtitle_box = (380, self.subtitle_y_var.get() - 24, CANVAS_W - 380, self.subtitle_y_var.get() + 52)

        title_margin_x = 60
        title_text_x = title_box_x + title_margin_x
        title_text_w = max(200, title_box_w - 2 * title_margin_x)
        title_text_y = title_box_y + 40
        title_text_h = max(80, title_box_h - 80)

        if self.background_image is not None:
            bg = self.background_image.copy()
            x, y, w, h = fit_contain(bg.width, bg.height, CANVAS_W, CANVAS_H)
            bg = bg.resize((w, h), Image.LANCZOS)
            draw.rectangle((0, 0, CANVAS_W, CANVAS_H), fill="#F3F4F6")
            img.alpha_composite(bg, (x, y))
        else:
            draw.rectangle((0, 0, CANVAS_W, CANVAS_H), fill="#F3F4F6")
            draw.rounded_rectangle((70, 70, CANVAS_W - 70, CANVAS_H - 70), radius=20, outline="#E5E7EB", width=2)
            if self.show_title_box_var.get():
                draw.rounded_rectangle(title_box, radius=18, outline="#E5E7EB", width=2, fill="#FAFAFA")

        header_text = self.reihe_var.get().strip()
        subtitle_text = self.subtitle_var.get().strip()
        title_text = self.title_text.get("1.0", "end-1c").strip()

        header_font = load_font(
            self.font_var.get(),
            self.header_size_var.get(),
            self.font_file_index,
            bold=self.header_bold_var.get(),
            italic=False,
        )
        subtitle_font = load_font(
            self.font_var.get(),
            self.subtitle_size_var.get(),
            self.font_file_index,
            bold=self.subtitle_bold_var.get(),
            italic=False,
        )
        header_color = COLORS[self.header_color_var.get()]
        subtitle_color = COLORS[self.subtitle_color_var.get()]
        title_color = COLORS[self.title_color_var.get()]
        box_color = COLORS[self.box_color_var.get()]
        align = ALIGNMENTS[self.align_var.get()]

        header_hidden = self.header_hidden_var.get()
        subtitle_hidden = self.subtitle_hidden_var.get()

        if header_text and not header_hidden:
            header_bbox = draw.textbbox((0, 0), header_text, font=header_font)
            header_w = header_bbox[2] - header_bbox[0]
            header_x = (CANVAS_W - header_w) / 2
            draw_text_with_style(
                img,
                (header_x, self.header_y_var.get() - header_bbox[1]),
                header_text,
                header_font,
                header_color,
                italic=self.header_italic_var.get(),
            )
        elif show_placeholders and not header_hidden:
            self._draw_neutral_text_slot(draw, header_box, "Reihe / Dachzeile")

        if subtitle_text and not subtitle_hidden:
            subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
            subtitle_w = subtitle_bbox[2] - subtitle_bbox[0]
            subtitle_x = (CANVAS_W - subtitle_w) / 2
            draw_text_with_style(
                img,
                (subtitle_x, self.subtitle_y_var.get() - subtitle_bbox[1]),
                subtitle_text,
                subtitle_font,
                subtitle_color,
                italic=self.subtitle_italic_var.get(),
            )
        elif show_placeholders and not subtitle_hidden:
            self._draw_neutral_text_slot(draw, subtitle_box, "Zweite Dachzeile / Untertitel")

        if self.show_title_box_var.get():
            draw.rounded_rectangle(title_box, radius=16, fill=box_color)

        if title_text:
            title_font, title_lines, fitted_size = fit_text_block(
                draw=draw,
                text=title_text,
                font_family=self.font_var.get(),
                file_index=self.font_file_index,
                start_size=self.title_size_var.get(),
                min_size=12,
                max_width=title_text_w,
                max_height=title_text_h,
                max_lines=None,
                bold=self.bold_var.get(),
                italic=self.italic_var.get(),
            )

            line_spacing = round(fitted_size * TITLE_LINE_SPACING_FACTOR)
            line_boxes = [draw.textbbox((0, 0), line, font=title_font) for line in title_lines]
            line_heights = [bbox[3] - bbox[1] for bbox in line_boxes]
            total_height = sum(line_heights) + max(0, len(title_lines) - 1) * line_spacing
            y_top = title_text_y + (title_text_h - total_height) / 2

            for line, bbox, h in zip(title_lines, line_boxes, line_heights):
                line_w = bbox[2] - bbox[0]
                if align == "left":
                    x = title_text_x
                elif align == "right":
                    x = title_text_x + title_text_w - line_w
                else:
                    x = title_text_x + (title_text_w - line_w) / 2
                draw_text_with_style(
                    img,
                    (x, y_top - bbox[1]),
                    line,
                    title_font,
                    title_color,
                    italic=self.italic_var.get(),
                )
                y_top += h + line_spacing

        if self.show_footer_var.get() and not self.use_background_var.get():
            left_box = (110, 860, 870, 1010)
            right_box = (1390, 835, 1750, 1000)

            if self.left_logo is not None:
                logo = self.left_logo.copy()
                x, y, w, h = fit_contain(logo.width, logo.height, 760, 150, 0)
                logo = logo.resize((w, h), Image.LANCZOS)
                img.alpha_composite(logo, (110 + x, 860 + y))
            else:
                self._draw_neutral_slot(draw, left_box, "Logo links unten")

            if self.partner_logo is not None:
                logo = self.partner_logo.copy()
                x, y, w, h = fit_contain(logo.width, logo.height, 360, 165, 18)
                logo = logo.resize((w, h), Image.LANCZOS)
                img.alpha_composite(logo, (1390 + x, 835 + y))
            else:
                self._draw_neutral_slot(draw, right_box, "Partnerlogo")

        return img

    def update_preview(self):
        try:
            img = self.render_image(show_placeholders=True).convert("RGB")
            canvas_w = max(400, self.preview_canvas.winfo_width())
            canvas_h = max(300, self.preview_canvas.winfo_height())
            scale = min((canvas_w - 24) / CANVAS_W, (canvas_h - 24) / CANVAS_H)
            scale = max(0.2, min(scale, 1.0))
            preview_w = max(1, int(CANVAS_W * scale))
            preview_h = max(1, int(CANVAS_H * scale))
            preview = img.resize((preview_w, preview_h), Image.LANCZOS)
            self.preview_photo = ImageTk.PhotoImage(preview)

            self.preview_canvas.delete("all")
            x = max(12, (canvas_w - preview_w) // 2)
            y = max(12, (canvas_h - preview_h) // 2)
            self.preview_canvas.create_image(x, y, image=self.preview_photo, anchor="nw")
            self.preview_canvas.configure(scrollregion=(0, 0, canvas_w, canvas_h))

            self.save_state()
            self.status_var.set("Vorschau aktualisiert.")
        except Exception as exc:
            self.status_var.set(f"Vorschaufehler: {exc}")

    def reset_demo(self, initial: bool = False):
        self.reihe_var.set("")
        self.subtitle_var.set("")
        self.title_text.delete("1.0", "end")
        self.background_image = None
        self.background_image_path = ""
        self.left_logo = None
        self.left_logo_path = ""
        self.partner_logo = None
        self.partner_logo_path = ""
        self.use_background_var.set(False)
        self.show_footer_var.set(True)
        self.show_title_box_var.set(True)
        self.title_size_var.set(64)
        self.header_size_var.set(42)
        self.subtitle_size_var.set(52)
        self.header_y_var.set(130)
        self.subtitle_y_var.set(220)
        self.title_box_y_var.set(360)
        self.title_box_width_var.set(1140)
        self.title_box_height_var.set(320)
        self.title_color_var.set("Weiß")
        self.header_color_var.set("Rot")
        self.subtitle_color_var.set("Rot")
        self.box_color_var.set("Rot")
        self.align_var.set("Zentriert")
        self.header_bold_var.set(False)
        self.header_italic_var.set(False)
        self.header_hidden_var.set(False)
        self.subtitle_bold_var.set(True)
        self.subtitle_italic_var.set(False)
        self.subtitle_hidden_var.set(False)
        if "Arial" in self.font_names:
            self.font_var.set("Arial")
        elif self.font_names:
            self.font_var.set(self.font_names[0])
        self.bold_var.set(False)
        self.italic_var.set(False)
        self.export_name_var.set("titelkarte.png")
        if not initial:
            self.status_var.set("Zurückgesetzt.")
        self.update_preview()

    def export_png(self):
        try:
            title_text = self.title_text.get("1.0", "end-1c").strip()
            filename = self.export_name_var.get().strip() or (sanitize_filename(title_text) if title_text else "titelkarte.png")
            if not filename.lower().endswith(".png"):
                filename += ".png"
            path = filedialog.asksaveasfilename(defaultextension=".png", initialfile=filename, filetypes=[("PNG-Datei", "*.png")])
            if not path:
                self.status_var.set("Export abgebrochen.")
                return
            img = self.render_image(show_placeholders=False).convert("RGB")
            img.save(path, format="PNG")
            self.status_var.set(f"PNG exportiert: {os.path.basename(path)}")
        except Exception as exc:
            self.status_var.set(f"Exportfehler: {exc}")
            messagebox.showerror("Exportfehler", str(exc))

    def export_to_project(self):
        out_dir = self._output_dir()
        project = getattr(self.app, "project", None)
        if not project or not out_dir:
            self.status_var.set("Kein Projekt geladen.")
            return
        try:
            title_text = self.title_text.get("1.0", "end-1c").strip()
            filename = self.export_name_var.get().strip() or (sanitize_filename(title_text) if title_text else "titelkarte.png")
            if not filename.lower().endswith(".png"):
                filename += ".png"
            target = out_dir / filename
            img = self.render_image(show_placeholders=False).convert("RGB")
            img.save(target, format="PNG")
            self.status_var.set(f"In Projekt exportiert: {target.name}")
        except Exception as exc:
            self.status_var.set(f"Export ins Projekt fehlgeschlagen: {exc}")
            messagebox.showerror("Exportfehler", str(exc))

    def refresh(self):
        if getattr(self.app, "project", None):
            self.load_state()
        else:
            self.status_var.set("Kein Projekt geladen.")

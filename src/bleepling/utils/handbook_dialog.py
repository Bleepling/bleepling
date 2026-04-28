from __future__ import annotations

import base64
import html
import mimetypes
import os
import re
import unicodedata
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
import tkinter as tk

try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None

try:
    import markdown as markdown_lib
except Exception:
    markdown_lib = None


def handbook_path() -> Path:
    return Path(__file__).resolve().parents[3] / "docs" / "Bleepling_Benutzerhandbuch.md"


def normalize_anchor(value: str) -> str:
    value = value.strip().lstrip("#").strip()
    value = value.replace("–", "-").replace("—", "-")
    value = value.replace("„", "").replace("“", "").replace('"', "")
    value = value.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = re.sub(r"[^\w\s.-]", "", value)
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-")


def _strip_leading_numbering(value: str) -> str:
    return re.sub(r"^\d+(?:\.\d+)*[a-z]?\s*", "", value.strip(), flags=re.IGNORECASE)


def _display_plain_text(value: str) -> str:
    value = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", value)
    value = value.replace("**", "").replace("__", "").replace("`", "")
    value = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", value)
    return value


def _normalize_local_anchor_links(markdown: str) -> str:
    def repl(match: re.Match[str]) -> str:
        label = match.group(1)
        target = match.group(2).strip()
        if not target.startswith("#"):
            return match.group(0)
        return f"[{label}](#{normalize_anchor(target)})"

    return re.sub(r"\[([^\]]+)\]\((#[^)]+)\)", repl, markdown)


def _inject_heading_ids(markdown: str) -> str:
    lines: list[str] = []
    for line in markdown.splitlines():
        match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if not match:
            lines.append(line)
            continue
        hashes, title = match.groups()
        anchor = normalize_anchor(title)
        level = min(len(hashes), 6)
        title_html = html.escape(title)
        lines.append(f'<h{level} id="{anchor}">{title_html}</h{level}>')
    return "\n".join(lines)


def _markdown_to_html_fallback(markdown: str, base_path: Path) -> str:
    body: list[str] = []
    lines = markdown.splitlines()
    idx = 0
    in_ul = False
    in_ol = False
    table_rows: list[list[str]] = []
    paragraph: list[str] = []

    def close_lists() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            body.append("</ul>")
            in_ul = False
        if in_ol:
            body.append("</ol>")
            in_ol = False

    def flush_paragraph() -> None:
        nonlocal paragraph
        if not paragraph:
            return
        text = " ".join(item.strip() for item in paragraph if item.strip())
        if text:
            body.append(f"<p>{_inline_markdown_to_html(text, base_path)}</p>")
        paragraph = []

    def flush_table() -> None:
        nonlocal table_rows
        if not table_rows:
            return
        if len(table_rows) >= 2 and all(re.fullmatch(r"[:\- ]+", cell or "") for cell in table_rows[1]):
            header = table_rows[0]
            rows = table_rows[2:]
        else:
            header = table_rows[0]
            rows = table_rows[1:]
        body.append("<table>")
        body.append("<thead><tr>" + "".join(f"<th>{_inline_markdown_to_html(cell, base_path)}</th>" for cell in header) + "</tr></thead>")
        if rows:
            body.append("<tbody>")
            for row in rows:
                body.append("<tr>" + "".join(f"<td>{_inline_markdown_to_html(cell, base_path)}</td>" for cell in row) + "</tr>")
            body.append("</tbody>")
        body.append("</table>")
        table_rows = []

    while idx < len(lines):
        line = lines[idx]
        stripped = line.strip()

        if stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2:
            flush_paragraph()
            close_lists()
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            table_rows.append(cells)
            idx += 1
            continue

        flush_table()

        if not stripped:
            flush_paragraph()
            close_lists()
            idx += 1
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading:
            flush_paragraph()
            close_lists()
            level = min(len(heading.group(1)), 6)
            title = heading.group(2).strip()
            anchor = normalize_anchor(title)
            body.append(f'<h{level} id="{html.escape(anchor)}">{_inline_markdown_to_html(title, base_path)}</h{level}>')
            idx += 1
            continue

        image_match = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", stripped)
        if image_match:
            flush_paragraph()
            close_lists()
            alt = html.escape(image_match.group(1).strip())
            src = _html_image_src(base_path, image_match.group(2).strip())
            body.append(f'<p class="image"><img src="{src}" alt="{alt}"></p>')
            idx += 1
            continue

        bullet = re.match(r"^[-*]\s+(.*)$", stripped)
        if bullet:
            flush_paragraph()
            if in_ol:
                body.append("</ol>")
                in_ol = False
            if not in_ul:
                body.append("<ul>")
                in_ul = True
            body.append(f"<li>{_inline_markdown_to_html(bullet.group(1), base_path)}</li>")
            idx += 1
            continue

        ordered = re.match(r"^\d+\.\s+(.*)$", stripped)
        if ordered:
            flush_paragraph()
            if in_ul:
                body.append("</ul>")
                in_ul = False
            if not in_ol:
                body.append("<ol>")
                in_ol = True
            body.append(f"<li>{_inline_markdown_to_html(ordered.group(1), base_path)}</li>")
            idx += 1
            continue

        if stripped.startswith(">"):
            flush_paragraph()
            close_lists()
            quote_lines = []
            while idx < len(lines) and lines[idx].strip().startswith(">"):
                quote_lines.append(lines[idx].strip().lstrip(">").strip())
                idx += 1
            body.append(f'<blockquote><p>{_inline_markdown_to_html(" ".join(quote_lines), base_path)}</p></blockquote>')
            continue

        paragraph.append(stripped)
        idx += 1

    flush_table()
    flush_paragraph()
    close_lists()
    return "\n".join(body)


def _inline_markdown_to_html(text: str, base_path: Path) -> str:
    placeholders: dict[str, str] = {}

    def stash(content: str) -> str:
        token = f"@@PLACEHOLDER_{len(placeholders)}@@"
        placeholders[token] = content
        return token

    def code_repl(match: re.Match[str]) -> str:
        return stash(f"<code>{html.escape(match.group(1))}</code>")

    def link_repl(match: re.Match[str]) -> str:
        label = html.escape(match.group(1))
        href = match.group(2).strip()
        if href.startswith("#"):
            target = "#" + normalize_anchor(href)
        else:
            resolved = _resolve_link_path(base_path, href)
            target = html.escape(resolved)
        return stash(f'<a href="{target}">{label}</a>')

    text = re.sub(r"`([^`]+)`", code_repl, text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_repl, text)
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    for token, content in placeholders.items():
        text = text.replace(token, content)
    return text


def _resolve_link_path(base_path: Path, href: str) -> str:
    href = href.strip()
    if re.match(r"^[a-z]+://", href, re.IGNORECASE):
        return href
    if href.startswith("#"):
        return "#" + normalize_anchor(href)
    path = (base_path.parent / href).resolve()
    return path.as_uri()


def _html_image_src(base_path: Path, href: str) -> str:
    href = href.strip()
    if re.match(r"^[a-z]+://", href, re.IGNORECASE):
        return href
    path = (base_path.parent / href).resolve()
    if not path.exists():
        return html.escape(href)
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def render_markdown_html(markdown: str, base_path: Path) -> str:
    markdown = _normalize_local_anchor_links(markdown)
    if markdown_lib is not None:
        prepared = _inject_heading_ids(markdown)
        prepared = re.sub(
            r"!\[([^\]]*)\]\(([^)]+)\)",
            lambda m: f'<p class="image"><img src="{_html_image_src(base_path, m.group(2))}" alt="{html.escape(m.group(1).strip())}"></p>',
            prepared,
        )
        body = markdown_lib.markdown(prepared, extensions=["tables", "sane_lists"])
    else:
        body = _markdown_to_html_fallback(markdown, base_path)
    return (
        "<!DOCTYPE html><html lang=\"de\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        "<title>Bleepling Benutzerhandbuch</title>"
        "<style>"
        "body{font-family:'Segoe UI',Arial,sans-serif;line-height:1.55;color:#1f2933;max-width:1100px;margin:0 auto;padding:32px 36px;background:#fff;}"
        "img{max-width:100%;height:auto;}h1,h2,h3,h4{color:#13293d;margin-top:1.5em;}h1{font-size:2rem;}h2{font-size:1.5rem;}h3{font-size:1.2rem;}"
        "table{border-collapse:collapse;width:100%;margin:1rem 0;}th,td{border:1px solid #c8d0d9;padding:8px;vertical-align:top;}th{background:#eef3f8;text-align:left;}"
        "blockquote{border-left:4px solid #7a9e7e;padding:0.2rem 1rem;margin:1rem 0;background:#f7fbf7;}"
        "code{background:#f2f4f7;padding:0.1rem 0.35rem;border-radius:4px;}a{color:#0b63ce;text-decoration:none;}a:hover{text-decoration:underline;}"
        ".image{text-align:center;margin:1.5rem 0;}"
        "</style></head><body>"
        f"{body}</body></html>"
    )


class HandbookDialog(tk.Toplevel):
    def __init__(self, owner, handbook_file: Path, anchor: str | None = None):
        super().__init__(owner.winfo_toplevel())
        self.owner = owner
        self.handbook_path = handbook_file
        self.title("Bleepling Benutzerhandbuch")
        self.geometry("1100x820")
        self.minsize(860, 620)
        self.transient(owner.winfo_toplevel())
        self._rendered_images: list[object] = []
        self._link_counter = 0
        self._heading_positions: dict[str, str] = {}
        self._heading_titles: dict[str, str] = {}
        self._heading_aliases: dict[str, str] = {}
        self._search_matches: list[tuple[str, str]] = []
        self._current_search_index = -1
        self._last_search_term = ""
        self._build()
        self._load_handbook()
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.after(0, lambda: self.jump_to_anchor(anchor) if anchor else None)

    def _build(self) -> None:
        outer = ttk.Frame(self, padding=12)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=1)

        ttk.Label(outer, text="Bleepling Benutzerhandbuch", font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 10)
        )

        search_row = ttk.Frame(outer)
        search_row.grid(row=0, column=0, sticky="e", pady=(0, 10))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_row, textvariable=self.search_var, width=36)
        self.search_entry.pack(side="left")
        ttk.Button(search_row, text="Suchen", command=self.find_next).pack(side="left", padx=(8, 4))
        ttk.Button(search_row, text="Zurück", command=self.find_previous).pack(side="left", padx=4)
        ttk.Button(search_row, text="Weiter", command=self.find_next).pack(side="left", padx=4)
        self.search_status_var = tk.StringVar(value="")
        ttk.Label(search_row, textvariable=self.search_status_var, width=12).pack(side="left", padx=(8, 0))

        viewer = ttk.Frame(outer)
        viewer.grid(row=1, column=0, sticky="nsew")
        viewer.columnconfigure(0, weight=1)
        viewer.rowconfigure(0, weight=1)

        self.text = tk.Text(viewer, wrap="word", padx=16, pady=16, undo=False, cursor="arrow")
        self.text.grid(row=0, column=0, sticky="nsew")
        yscroll = ttk.Scrollbar(viewer, orient="vertical", command=self.text.yview)
        yscroll.grid(row=0, column=1, sticky="ns")
        self.text.configure(yscrollcommand=yscroll.set)
        self.text.tag_configure("body", font=("Segoe UI", 10), spacing1=1, spacing3=6)
        self.text.tag_configure("h1", font=("Segoe UI", 17, "bold"), spacing1=14, spacing3=10)
        self.text.tag_configure("h2", font=("Segoe UI", 14, "bold"), spacing1=12, spacing3=8)
        self.text.tag_configure("h3", font=("Segoe UI", 12, "bold"), spacing1=10, spacing3=7)
        self.text.tag_configure("quote", lmargin1=22, lmargin2=22, foreground="#325b2b", spacing1=6, spacing3=6)
        self.text.tag_configure("bullet", lmargin1=18, lmargin2=34, spacing3=3)
        self.text.tag_configure("mono", font=("Consolas", 10))
        self.text.tag_configure("search_match", background="#FFF2B8")
        self.text.tag_configure("search_active", background="#F7E48B")

        button_row = ttk.Frame(outer)
        button_row.grid(row=2, column=0, sticky="e", pady=(10, 0))
        ttk.Button(button_row, text="HTML exportieren", command=self.export_html).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Schließen", command=self._close, style="Accent.TButton").pack(side="left")

        self.search_var.trace_add("write", lambda *_: self._reset_search())
        self.bind("<Control-f>", lambda _e: self._focus_search())
        self.bind("<F3>", lambda _e: self.find_next())
        self.bind("<Shift-F3>", lambda _e: self.find_previous())

    def _focus_search(self):
        try:
            self.search_entry.focus_set()
            self.search_entry.selection_range(0, "end")
        except Exception:
            self.focus_set()
        return "break"

    def _close(self) -> None:
        root = self.owner.winfo_toplevel()
        if getattr(root, "_bleepling_handbook_dialog", None) is self:
            root._bleepling_handbook_dialog = None
        self.destroy()

    def _load_handbook(self) -> None:
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self._rendered_images.clear()
        self._heading_positions.clear()
        self._heading_titles.clear()
        self._heading_aliases.clear()
        if not self.handbook_path.exists():
            self.text.insert("1.0", "Das Benutzerhandbuch wurde nicht gefunden.\n", ("body",))
            self.text.configure(state="disabled")
            return
        markdown = self.handbook_path.read_text(encoding="utf-8")
        self._collect_heading_aliases(markdown)
        self._render_markdown(markdown)
        self.text.configure(state="disabled")

    def _collect_heading_aliases(self, markdown: str) -> None:
        for line in markdown.splitlines():
            match = re.match(r"^(#{1,6})\s+(.*)$", line.strip())
            if not match:
                continue
            title = match.group(2).strip()
            anchor = normalize_anchor(title)
            plain = _strip_leading_numbering(title)
            self._heading_titles[anchor] = title
            self._heading_aliases[anchor] = anchor
            self._heading_aliases[normalize_anchor(plain)] = anchor

    def _render_markdown(self, markdown: str) -> None:
        lines = markdown.splitlines()
        table_rows: list[str] = []

        def flush_table() -> None:
            nonlocal table_rows
            if not table_rows:
                return
            self._insert_table(table_rows)
            table_rows = []

        for raw_line in lines:
            stripped = raw_line.strip()
            if stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2:
                table_rows.append(stripped)
                continue

            flush_table()

            if not stripped:
                self.text.insert("end", "\n")
                continue

            heading = re.match(r"^(#{1,6})\s+(.*)$", stripped)
            if heading:
                level = min(len(heading.group(1)), 3)
                title = heading.group(2).strip()
                anchor = normalize_anchor(title)
                idx = self.text.index("end-1c")
                self._heading_positions[anchor] = idx
                self.text.insert("end", _display_plain_text(title) + "\n", (f"h{level}",))
                continue

            image_match = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", stripped)
            if image_match:
                self._insert_image(image_match.group(2).strip(), image_match.group(1).strip())
                continue

            bullet = re.match(r"^[-*]\s+(.*)$", stripped)
            if bullet:
                self.text.insert("end", "• ", ("bullet",))
                self._insert_inline_segments(bullet.group(1), base_tags=("body", "bullet"))
                self.text.insert("end", "\n")
                continue

            ordered = re.match(r"^(\d+)\.\s+(.*)$", stripped)
            if ordered:
                self.text.insert("end", f"{ordered.group(1)}. ", ("bullet",))
                self._insert_inline_segments(ordered.group(2), base_tags=("body", "bullet"))
                self.text.insert("end", "\n")
                continue

            if stripped.startswith(">"):
                quote = stripped.lstrip(">").strip()
                self._insert_inline_segments(quote, base_tags=("body", "quote"))
                self.text.insert("end", "\n")
                continue

            self._insert_inline_segments(stripped, base_tags=("body",))
            self.text.insert("end", "\n")

        flush_table()

    def _insert_image(self, href: str, alt: str) -> None:
        path = (self.handbook_path.parent / href).resolve()
        if Image is not None and ImageTk is not None and path.exists():
            try:
                img = Image.open(path)
                max_width = 760
                width, height = img.size
                if width > max_width:
                    ratio = max_width / float(width)
                    img = img.resize((int(width * ratio), int(height * ratio)))
                tk_img = ImageTk.PhotoImage(img)
                self._rendered_images.append(tk_img)
                self.text.image_create("end", image=tk_img)
                self.text.insert("end", "\n")
                return
            except Exception:
                pass
        self.text.insert("end", f"[Bild: {alt or path.name}]\n", ("body",))

    def _insert_table(self, table_lines: list[str]) -> None:
        rows = [[cell.strip() for cell in line.strip("|").split("|")] for line in table_lines]
        if len(rows) >= 2 and all(re.fullmatch(r"[:\- ]+", cell or "") for cell in rows[1]):
            rows = [rows[0]] + rows[2:]
        widths = []
        for row in rows:
            for idx, cell in enumerate(row):
                while len(widths) <= idx:
                    widths.append(0)
                widths[idx] = max(widths[idx], len(_display_plain_text(cell)))
        for row_index, row in enumerate(rows):
            parts = []
            for idx, cell in enumerate(row):
                parts.append(_display_plain_text(cell).ljust(widths[idx]))
            self.text.insert("end", " | ".join(parts) + "\n", ("body", "mono"))
            if row_index == 0 and len(rows) > 1:
                self.text.insert("end", "-+-".join("-" * width for width in widths) + "\n", ("body", "mono"))
        self.text.insert("end", "\n")

    def _insert_inline_segments(self, text: str, base_tags: tuple[str, ...] = ("body",)) -> None:
        pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
        last = 0
        for match in pattern.finditer(text):
            if match.start() > last:
                plain = _display_plain_text(text[last:match.start()])
                if plain:
                    self.text.insert("end", plain, base_tags)
            label = _display_plain_text(match.group(1))
            href = match.group(2).strip()
            self._insert_link(label, href, base_tags)
            last = match.end()
        if last < len(text):
            plain = _display_plain_text(text[last:])
            if plain:
                self.text.insert("end", plain, base_tags)

    def _insert_link(self, label: str, href: str, base_tags: tuple[str, ...]) -> None:
        tag = f"link_{self._link_counter}"
        self._link_counter += 1
        self.text.tag_configure(tag, foreground="#0b63ce", underline=True)
        self.text.tag_bind(tag, "<Enter>", lambda _e: self.text.configure(cursor="hand2"))
        self.text.tag_bind(tag, "<Leave>", lambda _e: self.text.configure(cursor="arrow"))
        self.text.tag_bind(tag, "<Button-1>", lambda _e, target=href: self._open_link(target))
        self.text.insert("end", label, (*base_tags, tag))

    def _open_link(self, href: str) -> None:
        if href.startswith("#"):
            self.jump_to_anchor(href)
            return
        if re.match(r"^[a-z]+://", href, re.IGNORECASE):
            webbrowser.open(href)
            return
        path = (self.handbook_path.parent / href).resolve()
        if not path.exists():
            messagebox.showwarning("Link öffnen", f"Die verlinkte Datei wurde nicht gefunden:\n\n{path}", parent=self)
            return
        try:
            if hasattr(os, "startfile"):
                os.startfile(str(path))
            else:
                webbrowser.open(path.as_uri())
        except Exception as exc:
            messagebox.showerror("Link öffnen", f"Die Datei konnte nicht geöffnet werden:\n\n{exc}", parent=self)

    def _resolve_anchor(self, target: str | None) -> str | None:
        if not target:
            return None
        normalized = normalize_anchor(target)
        if normalized in self._heading_positions:
            return normalized
        alias = self._heading_aliases.get(normalized)
        if alias and alias in self._heading_positions:
            return alias
        plain = normalize_anchor(_strip_leading_numbering(target))
        alias = self._heading_aliases.get(plain)
        if alias and alias in self._heading_positions:
            return alias
        for key, title in self._heading_titles.items():
            title_plain = normalize_anchor(_strip_leading_numbering(title))
            if normalized in {key, title_plain} or normalized in title_plain or title_plain in normalized:
                return key
        return None

    def jump_to_anchor(self, target: str | None) -> bool:
        anchor = self._resolve_anchor(target)
        if not anchor:
            return False
        position = self._heading_positions.get(anchor)
        if not position:
            return False
        self.text.see(position)
        self.text.mark_set("insert", position)
        self.text.tag_remove("sel", "1.0", "end")
        line_end = f"{position} lineend"
        self.text.tag_add("sel", position, line_end)
        self.after(700, lambda: self.text.tag_remove("sel", "1.0", "end"))
        return True

    def _reset_search(self) -> None:
        self._last_search_term = ""
        self._current_search_index = -1
        self._clear_search_highlights()
        self.search_status_var.set("")

    def _clear_search_highlights(self) -> None:
        self.text.tag_remove("search_match", "1.0", "end")
        self.text.tag_remove("search_active", "1.0", "end")
        self._search_matches.clear()

    def _run_search(self, direction: int) -> None:
        term = self.search_var.get().strip()
        if not term:
            self._reset_search()
            return
        if term != self._last_search_term:
            self._clear_search_highlights()
            start = "1.0"
            while True:
                match_start = self.text.search(term, start, stopindex="end", nocase=True)
                if not match_start:
                    break
                match_end = f"{match_start}+{len(term)}c"
                self._search_matches.append((match_start, match_end))
                start = match_end
            self._last_search_term = term
            self._current_search_index = -1
        if not self._search_matches:
            self.search_status_var.set("0 Treffer")
            return
        if self._current_search_index < 0:
            self._current_search_index = 0 if direction >= 0 else len(self._search_matches) - 1
        else:
            self._current_search_index = (self._current_search_index + direction) % len(self._search_matches)
        self.text.tag_remove("search_match", "1.0", "end")
        self.text.tag_remove("search_active", "1.0", "end")
        for idx, (start, end) in enumerate(self._search_matches):
            tag = "search_active" if idx == self._current_search_index else "search_match"
            self.text.tag_add(tag, start, end)
        active_start, _active_end = self._search_matches[self._current_search_index]
        self.text.see(active_start)
        self.search_status_var.set(f"{self._current_search_index + 1} / {len(self._search_matches)}")

    def find_next(self) -> None:
        self._run_search(1)

    def find_previous(self) -> None:
        self._run_search(-1)

    def export_html(self) -> None:
        if not self.handbook_path.exists():
            messagebox.showwarning("HTML-Export", "Das Benutzerhandbuch wurde nicht gefunden.", parent=self)
            return
        target = filedialog.asksaveasfilename(
            parent=self,
            title="Benutzerhandbuch als HTML exportieren",
            initialdir=str(self.handbook_path.parent),
            initialfile="Bleepling_Benutzerhandbuch.html",
            defaultextension=".html",
            filetypes=[("HTML-Dateien", "*.html"), ("Alle Dateien", "*.*")],
        )
        if not target:
            return
        target_path = Path(target)
        try:
            markdown = self.handbook_path.read_text(encoding="utf-8")
            target_path.write_text(render_markdown_html(markdown, self.handbook_path), encoding="utf-8-sig")
        except Exception as exc:
            messagebox.showerror("HTML-Export", f"Das Benutzerhandbuch konnte nicht exportiert werden:\n\n{exc}", parent=self)
            return
        messagebox.showinfo(
            "HTML-Export",
            f"Das Benutzerhandbuch wurde als HTML exportiert:\n\n{target_path}",
            parent=self,
        )


def open_handbook(owner, anchor: str | None = None) -> HandbookDialog:
    root = owner.winfo_toplevel()
    existing = getattr(root, "_bleepling_handbook_dialog", None)
    if existing is not None:
        try:
            if existing.winfo_exists():
                existing.deiconify()
                existing.lift()
                existing.focus_set()
                if anchor:
                    existing.jump_to_anchor(anchor)
                return existing
        except Exception:
            pass
    dialog = HandbookDialog(owner, handbook_path(), anchor=anchor)
    root._bleepling_handbook_dialog = dialog
    return dialog

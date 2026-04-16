from __future__ import annotations

import tkinter as tk
from tkinter import ttk


def show_help_dialog(owner, title: str, body: str) -> None:
    win = tk.Toplevel(owner.winfo_toplevel())
    win.title(title)
    win.transient(owner.winfo_toplevel())
    win.resizable(False, False)
    frame = ttk.Frame(win, padding=14)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text=title, font=("Segoe UI", 10, "bold")).pack(anchor="w")
    msg = tk.Message(frame, text=body, width=620, justify="left")
    msg.pack(fill="both", expand=True, pady=(10, 12))
    ttk.Button(frame, text="Schließen", command=win.destroy, style="Accent.TButton").pack(anchor="e")
    win.update_idletasks()
    root = owner.winfo_toplevel()
    rx, ry, rw, rh = root.winfo_rootx(), root.winfo_rooty(), root.winfo_width(), root.winfo_height()
    ww, wh = win.winfo_width(), win.winfo_height()
    win.geometry(f"+{rx + max(0, (rw-ww)//2)}+{ry + max(0, (rh-wh)//2)}")

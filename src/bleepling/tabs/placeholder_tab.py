from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class PlaceholderTab(ttk.Frame):
    def __init__(self, master: tk.Misc, title: str, description: str) -> None:
        super().__init__(master, padding=20)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        box = ttk.LabelFrame(self, text=title, padding=16)
        box.grid(row=0, column=0, sticky="nsew")
        box.columnconfigure(0, weight=1)

        ttk.Label(
            box,
            text=description,
            justify="left",
            wraplength=760,
        ).grid(row=0, column=0, sticky="nw")

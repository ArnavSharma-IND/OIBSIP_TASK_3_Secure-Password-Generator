"""Security details view presenting entropy calculations and cryptographic metrics."""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any
from themes.theme_manager import ThemeManager
from password_strength import StrengthReport


class SecurityDetailsFrame(ttk.Frame):
    """Minimalist display of cryptographic entropy and complexity breakdown."""

    def __init__(self, parent: tk.Widget, theme_manager: ThemeManager, **kwargs):
        super().__init__(parent, style="Surface.TFrame", **kwargs)
        self.theme_manager = theme_manager

        self._build_ui()
        self.theme_manager.register_listener(self.on_theme_changed)

    def _build_ui(self) -> None:
        p = self.theme_manager.palette

        # Container with padding
        self.container = tk.Frame(self, bg=p["surface"], padx=20, pady=16)
        self.container.pack(fill="x", expand=True)

        # Header Title
        self.title_lbl = tk.Label(
            self.container,
            text="CRYPTOGRAPHIC METRICS & ENTROPY",
            font=("Segoe UI", 9, "bold"),
            bg=p["surface"],
            fg=p["secondary_text"],
            anchor="w",
        )
        self.title_lbl.pack(fill="x", pady=(0, 10))

        # Divider line
        self.div1 = tk.Frame(self.container, bg=p["borders"], height=1)
        self.div1.pack(fill="x", pady=(0, 12))

        # Metrics Grid (Clean open layout without cards)
        self.grid_frame = tk.Frame(self.container, bg=p["surface"])
        self.grid_frame.pack(fill="x", pady=(0, 10))
        self.grid_frame.columnconfigure(0, weight=1)
        self.grid_frame.columnconfigure(1, weight=1)
        self.grid_frame.columnconfigure(2, weight=1)
        self.grid_frame.columnconfigure(3, weight=1)

        # Metric 1: Entropy Bits
        self.entropy_val_lbl = tk.Label(
            self.grid_frame,
            text="-- bits",
            font=("Segoe UI", 14, "bold"),
            bg=p["surface"],
            fg=p["primary_accent"],
            anchor="w",
        )
        self.entropy_val_lbl.grid(row=0, column=0, sticky="w")
        self.entropy_title_lbl = tk.Label(
            self.grid_frame,
            text="THEORETICAL ENTROPY",
            font=("Segoe UI", 7, "bold"),
            bg=p["surface"],
            fg=p["secondary_text"],
            anchor="w",
        )
        self.entropy_title_lbl.grid(row=1, column=0, sticky="w", pady=(2, 0))

        # Metric 2: Pool Size
        self.pool_val_lbl = tk.Label(
            self.grid_frame,
            text="-- chars",
            font=("Segoe UI", 14, "bold"),
            bg=p["surface"],
            fg=p["primary_text"],
            anchor="w",
        )
        self.pool_val_lbl.grid(row=0, column=1, sticky="w")
        self.pool_title_lbl = tk.Label(
            self.grid_frame,
            text="POOL SIZE (R)",
            font=("Segoe UI", 7, "bold"),
            bg=p["surface"],
            fg=p["secondary_text"],
            anchor="w",
        )
        self.pool_title_lbl.grid(row=1, column=1, sticky="w", pady=(2, 0))

        # Metric 3: Length
        self.len_val_lbl = tk.Label(
            self.grid_frame,
            text="--",
            font=("Segoe UI", 14, "bold"),
            bg=p["surface"],
            fg=p["primary_text"],
            anchor="w",
        )
        self.len_val_lbl.grid(row=0, column=2, sticky="w")
        self.len_title_lbl = tk.Label(
            self.grid_frame,
            text="LENGTH (L)",
            font=("Segoe UI", 7, "bold"),
            bg=p["surface"],
            fg=p["secondary_text"],
            anchor="w",
        )
        self.len_title_lbl.grid(row=1, column=2, sticky="w", pady=(2, 0))

        # Metric 4: Rating
        self.rating_val_lbl = tk.Label(
            self.grid_frame,
            text="--",
            font=("Segoe UI", 14, "bold"),
            bg=p["surface"],
            fg=p["strength_strong"],
            anchor="w",
        )
        self.rating_val_lbl.grid(row=0, column=3, sticky="w")
        self.rating_title_lbl = tk.Label(
            self.grid_frame,
            text="RATING",
            font=("Segoe UI", 7, "bold"),
            bg=p["surface"],
            fg=p["secondary_text"],
            anchor="w",
        )
        self.rating_title_lbl.grid(row=1, column=3, sticky="w", pady=(2, 0))

        # Explanatory detail text
        self.desc_lbl = tk.Label(
            self.container,
            text="Theoretical entropy calculated as E = L × log₂(R).",
            font=("Segoe UI", 9),
            bg=p["surface"],
            fg=p["secondary_text"],
            wraplength=640,
            justify="left",
            anchor="w",
        )
        self.desc_lbl.pack(fill="x", pady=(10, 4))

        # Crack time note
        self.crack_lbl = tk.Label(
            self.container,
            text="Estimated brute-force resistance: --",
            font=("Segoe UI", 8, "italic"),
            bg=p["surface"],
            fg=p["muted_text"],
            anchor="w",
        )
        self.crack_lbl.pack(fill="x", pady=(2, 0))

    def update_metrics(self, report: StrengthReport) -> None:
        """Update metrics labels with the latest strength report."""
        p = self.theme_manager.palette

        self.entropy_val_lbl.config(text=f"{report.entropy_bits:.1f} bits")
        self.pool_val_lbl.config(text=f"{report.pool_size} chars")
        self.len_val_lbl.config(text=str(report.length))

        # Color rating label
        if report.label == "Strong":
            color = p["strength_strong"]
        elif report.label == "Medium":
            color = p["strength_medium"]
        else:
            color = p["strength_weak"]

        self.rating_val_lbl.config(text=report.label, fg=color)
        self.desc_lbl.config(
            text=f"{report.description} Categories: {report.category_summary}."
        )
        self.crack_lbl.config(
            text=f"Estimated brute-force resistance: {report.crack_time_estimate} (at 10¹¹ guesses/sec)."
        )

    def on_theme_changed(self, theme_name: str, palette: Dict[str, str]) -> None:
        """Apply theme updates to tkinter widgets."""
        p = palette
        self.container.config(bg=p["surface"])
        self.title_lbl.config(bg=p["surface"], fg=p["secondary_text"])
        self.div1.config(bg=p["borders"])
        self.grid_frame.config(bg=p["surface"])

        self.entropy_val_lbl.config(bg=p["surface"], fg=p["primary_accent"])
        self.entropy_title_lbl.config(bg=p["surface"], fg=p["secondary_text"])
        self.pool_val_lbl.config(bg=p["surface"], fg=p["primary_text"])
        self.pool_title_lbl.config(bg=p["surface"], fg=p["secondary_text"])
        self.len_val_lbl.config(bg=p["surface"], fg=p["primary_text"])
        self.len_title_lbl.config(bg=p["surface"], fg=p["secondary_text"])
        self.rating_title_lbl.config(bg=p["surface"], fg=p["secondary_text"])
        self.rating_val_lbl.config(bg=p["surface"])

        self.desc_lbl.config(bg=p["surface"], fg=p["secondary_text"])
        self.crack_lbl.config(bg=p["surface"], fg=p["muted_text"])

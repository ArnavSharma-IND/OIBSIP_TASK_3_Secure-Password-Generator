"""Theme manager orchestrating colors, TTK styles, and typography."""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Callable, List
from themes.light import LIGHT_PALETTE
from themes.dark import DARK_PALETTE


class ThemeManager:
    """Manages active color palette, TTK styles, and broadcast notifications on theme switch."""

    def __init__(self, initial_theme: str = "dark"):
        self.current_theme: str = initial_theme if initial_theme in ("dark", "light") else "dark"
        self._listeners: List[Callable[[str, Dict[str, str]], None]] = []
        self._style: ttk.Style | None = None

    @property
    def palette(self) -> Dict[str, str]:
        """Get the dictionary of colors for the currently active theme."""
        return DARK_PALETTE if self.current_theme == "dark" else LIGHT_PALETTE

    def get_color(self, key: str) -> str:
        """Lookup a color in the active palette."""
        return self.palette.get(key, "#000000")

    def register_listener(self, callback: Callable[[str, Dict[str, str]], None]) -> None:
        """Register a callback function to be called whenever theme changes."""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def unregister_listener(self, callback: Callable[[str, Dict[str, str]], None]) -> None:
        """Unregister a theme change callback."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def toggle_theme(self) -> str:
        """Toggle between 'dark' and 'light' mode."""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme()
        return self.current_theme

    def set_theme(self, theme_name: str) -> None:
        """Explicitly set theme ('dark' or 'light')."""
        if theme_name in ("dark", "light") and theme_name != self.current_theme:
            self.current_theme = theme_name
            self.apply_theme()

    def apply_theme(self, root: tk.Tk | None = None) -> None:
        """Configure ttk styles with current palette and notify all listeners."""
        p = self.palette

        if root is not None:
            root.configure(bg=p["main_bg"])
            try:
                self._style = ttk.Style(root)
            except Exception:
                pass

        if self._style is None:
            self._style = ttk.Style()

        # Use 'clam' or 'alt' base theme for consistent ttk color overriding
        try:
            self._style.theme_use("clam")
        except Exception:
            pass

        # Configure base TTK frames
        self._style.configure("TFrame", background=p["main_bg"])
        self._style.configure("Surface.TFrame", background=p["surface"])
        self._style.configure("Secondary.TFrame", background=p["secondary_surface"])
        self._style.configure("Border.TFrame", background=p["borders"])

        # Configure base TTK labels
        self._style.configure(
            "TLabel",
            background=p["main_bg"],
            foreground=p["primary_text"],
            font=("Segoe UI", 10),
        )
        self._style.configure(
            "Surface.TLabel",
            background=p["surface"],
            foreground=p["primary_text"],
            font=("Segoe UI", 10),
        )
        self._style.configure(
            "Title.TLabel",
            background=p["main_bg"],
            foreground=p["primary_text"],
            font=("Segoe UI", 16, "bold"),
        )
        self._style.configure(
            "Subtitle.TLabel",
            background=p["main_bg"],
            foreground=p["secondary_text"],
            font=("Segoe UI", 9),
        )
        self._style.configure(
            "SectionHeader.TLabel",
            background=p["surface"],
            foreground=p["secondary_text"],
            font=("Segoe UI", 8, "bold"),
        )
        self._style.configure(
            "Secondary.TLabel",
            background=p["surface"],
            foreground=p["secondary_text"],
            font=("Segoe UI", 9),
        )
        self._style.configure(
            "Muted.TLabel",
            background=p["surface"],
            foreground=p["muted_text"],
            font=("Segoe UI", 8),
        )

        # Buttons
        self._style.configure(
            "Primary.TButton",
            background=p["primary_accent"],
            foreground=p["accent_text"],
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
            focusthickness=0,
            padding=(14, 8),
        )
        self._style.map(
            "Primary.TButton",
            background=[("active", p["muted_accent"]), ("disabled", p["borders"])],
            foreground=[("disabled", p["muted_text"])],
        )

        self._style.configure(
            "Secondary.TButton",
            background=p["secondary_surface"],
            foreground=p["primary_text"],
            font=("Segoe UI", 9),
            borderwidth=1,
            bordercolor=p["borders"],
            focusthickness=0,
            padding=(10, 6),
        )
        self._style.map(
            "Secondary.TButton",
            background=[("active", p["borders"])],
            foreground=[("active", p["primary_text"])],
        )

        self._style.configure(
            "Ghost.TButton",
            background=p["surface"],
            foreground=p["secondary_text"],
            font=("Segoe UI", 9),
            borderwidth=0,
            padding=(8, 4),
        )
        self._style.map(
            "Ghost.TButton",
            background=[("active", p["secondary_surface"])],
            foreground=[("active", p["primary_text"])],
        )

        # Checkbuttons
        self._style.configure(
            "TCheckbutton",
            background=p["surface"],
            foreground=p["primary_text"],
            font=("Segoe UI", 9),
            focuscolor=p["primary_accent"],
        )
        self._style.map(
            "TCheckbutton",
            background=[("active", p["surface"])],
            foreground=[("active", p["primary_accent"])],
            indicatorcolor=[("selected", p["primary_accent"]), ("!selected", p["secondary_surface"])],
        )

        # Sliders (Scale)
        self._style.configure(
            "Horizontal.TScale",
            background=p["surface"],
            troughcolor=p["secondary_surface"],
            sliderrelief="flat",
        )

        # Progressbar
        self._style.configure(
            "Strength.Horizontal.TProgressbar",
            troughcolor=p["secondary_surface"],
            background=p["primary_accent"],
            thickness=6,
            borderwidth=0,
        )

        # Notebook tabs (clean navigation bar)
        self._style.configure(
            "TNotebook",
            background=p["main_bg"],
            borderwidth=0,
            tabmargins=[0, 0, 0, 0],
        )
        self._style.configure(
            "TNotebook.Tab",
            background=p["main_bg"],
            foreground=p["secondary_text"],
            padding=[16, 8],
            font=("Segoe UI", 9, "bold"),
            borderwidth=0,
        )
        self._style.map(
            "TNotebook.Tab",
            background=[("selected", p["surface"]), ("active", p["secondary_surface"])],
            foreground=[("selected", p["primary_accent"]), ("active", p["primary_text"])],
        )

        # Notify UI components
        for listener in self._listeners:
            try:
                listener(self.current_theme, p)
            except Exception:
                pass

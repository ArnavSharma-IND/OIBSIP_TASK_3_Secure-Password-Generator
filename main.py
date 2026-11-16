"""Main entry point for the Secure Password Generator desktop application.

A minimalist, high-security desktop application developed with Python, Tkinter,
and the standard `secrets` module.
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional

from config import (
    APP_NAME,
    APP_VERSION,
    AUTHOR,
)
from themes.theme_manager import ThemeManager
from services.settings_service import load_settings, save_settings, AppSettings
from services.clipboard_service import copy_to_clipboard
from modules.generator_ui import PasswordGeneratorUI
from modules.security_details import SecurityDetailsFrame
from modules.history_ui import SessionHistoryFrame
from modules.passphrase_ui import PassphraseGeneratorFrame
from modules.settings_ui import SettingsFrame
from password_strength import StrengthReport


class SecurePasswordGeneratorApp:
    """Root Application controller managing window lifecycle, themes, and views."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("780x680")
        self.root.minsize(720, 600)

        # Load persisted non-sensitive preferences
        self.settings: AppSettings = load_settings()

        # Initialize centralized theme manager
        self.theme_manager = ThemeManager(initial_theme=self.settings.theme)

        # Register close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Build UI layout
        self._build_shell()
        self.theme_manager.apply_theme(self.root)
        self.theme_manager.register_listener(self.on_theme_changed)

        # Trigger initial generation so all views sync
        self.generator_view.generate()

        # Global keyboard shortcuts
        self._bind_shortcuts()

        # Center window on screen
        self._center_window()

    def _center_window(self) -> None:
        """Center the application window on screen."""
        self.root.update_idletasks()
        width = 780
        height = 680
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _build_shell(self) -> None:
        """Build main application structure with header, tabbed views, and status bar."""
        p = self.theme_manager.palette

        # Root container
        self.main_container = tk.Frame(self.root, bg=p["main_bg"])
        self.main_container.pack(fill="both", expand=True)

        # -------------------------------------------------------------
        # 1. TOP HEADER / APP BAR
        # -------------------------------------------------------------
        self.header_bar = tk.Frame(self.main_container, bg=p["main_bg"], padx=24, pady=16)
        self.header_bar.pack(fill="x")

        # Brand / Title
        self.brand_frame = tk.Frame(self.header_bar, bg=p["main_bg"])
        self.brand_frame.pack(side="left")

        self.title_lbl = tk.Label(
            self.brand_frame,
            text=APP_NAME.upper(),
            font=("Segoe UI", 13, "bold"),
            bg=p["main_bg"],
            fg=p["primary_text"],
        )
        self.title_lbl.pack(side="left")

        self.badge_lbl = tk.Label(
            self.brand_frame,
            text=f"v{APP_VERSION} • LOCAL CRYPTO",
            font=("Segoe UI", 7, "bold"),
            bg=p["secondary_surface"],
            fg=p["primary_accent"],
            padx=6,
            pady=2,
        )
        self.badge_lbl.pack(side="left", padx=(10, 0))

        # Quick Theme Toggle Pill Button
        self.theme_btn = tk.Button(
            self.header_bar,
            text="☀ Light" if self.theme_manager.current_theme == "dark" else "🌙 Dark",
            font=("Segoe UI", 8, "bold"),
            bg=p["secondary_surface"],
            fg=p["primary_text"],
            activebackground=p["borders"],
            activeforeground=p["primary_text"],
            relief="flat",
            padx=12,
            pady=4,
            command=self.toggle_theme,
        )
        self.theme_btn.pack(side="right")

        # Thin divider line
        self.nav_divider = tk.Frame(self.main_container, bg=p["borders"], height=1)
        self.nav_divider.pack(fill="x", padx=24)

        # -------------------------------------------------------------
        # 2. NOTEBOOK / TABBED NAVIGATION
        # -------------------------------------------------------------
        self.notebook_frame = tk.Frame(self.main_container, bg=p["main_bg"], padx=24, pady=12)
        self.notebook_frame.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(self.notebook_frame)
        self.notebook.pack(fill="both", expand=True)

        # Module 1: Generator (Main)
        self.generator_view = PasswordGeneratorUI(
            self.notebook,
            theme_manager=self.theme_manager,
            settings=self.settings,
            on_password_generated=self.on_password_generated,
            on_status_message=self.show_status,
        )
        self.notebook.add(self.generator_view, text="  Generator  ")

        # Module 2: Security Details
        self.security_view = SecurityDetailsFrame(
            self.notebook,
            theme_manager=self.theme_manager,
        )
        self.notebook.add(self.security_view, text="  Security Details  ")

        # Module 3: History (In-memory)
        self.history_view = SessionHistoryFrame(
            self.notebook,
            theme_manager=self.theme_manager,
            on_select_password=self.on_select_historical_password,
            on_status_message=self.show_status,
        )
        self.notebook.add(self.history_view, text="  History (RAM)  ")

        # Module 4: Passphrase Generator (Creative Bonus)
        self.passphrase_view = PassphraseGeneratorFrame(
            self.notebook,
            theme_manager=self.theme_manager,
            on_passphrase_generated=self.on_passphrase_generated,
            on_status_message=self.show_status,
        )
        self.notebook.add(self.passphrase_view, text="  Passphrase  ")

        # Module 5: Settings & About
        self.settings_view = SettingsFrame(
            self.notebook,
            theme_manager=self.theme_manager,
            on_settings_saved=self.on_settings_saved,
            on_status_message=self.show_status,
        )
        self.notebook.add(self.settings_view, text="  Preferences  ")

        # -------------------------------------------------------------
        # 3. STATUS BAR / TOAST NOTIFICATION
        # -------------------------------------------------------------
        self.status_bar = tk.Frame(self.main_container, bg=p["secondary_surface"], padx=24, pady=6)
        self.status_bar.pack(fill="x", side="bottom")

        self.status_lbl = tk.Label(
            self.status_bar,
            text="Ready • Cryptographically secure CSPRNG (secrets module active)",
            font=("Segoe UI", 8),
            bg=p["secondary_surface"],
            fg=p["secondary_text"],
            anchor="w",
        )
        self.status_lbl.pack(side="left")

        self.author_lbl = tk.Label(
            self.status_bar,
            text=f"Developed by {AUTHOR}",
            font=("Segoe UI", 8),
            bg=p["secondary_surface"],
            fg=p["muted_text"],
            anchor="e",
        )
        self.author_lbl.pack(side="right")

    def _bind_shortcuts(self) -> None:
        """Bind ergonomic keyboard shortcuts."""
        self.root.bind("<Return>", lambda event: self._handle_return_key())
        self.root.bind("<Control-c>", lambda event: self.generator_view.copy_current_password())
        self.root.bind("<Control-C>", lambda event: self.generator_view.copy_current_password())
        self.root.bind("<Control-t>", lambda event: self.toggle_theme())
        self.root.bind("<Control-T>", lambda event: self.toggle_theme())
        self.root.bind("<Control-h>", lambda event: self.generator_view.toggle_mask())
        self.root.bind("<F5>", lambda event: self.generator_view.generate())

    def _handle_return_key(self) -> None:
        """Handle Return key: generate on active view."""
        current_tab = self.notebook.index(self.notebook.select())
        if current_tab == 0:
            self.generator_view.generate()
        elif current_tab == 3:
            self.passphrase_view.generate()

    def toggle_theme(self) -> None:
        """Toggle active theme and update quick button text."""
        new_theme = self.theme_manager.toggle_theme()
        self.settings.theme = new_theme
        save_settings(self.settings)

    def on_password_generated(self, password: str, report: StrengthReport) -> None:
        """Callback triggered whenever a new password is generated."""
        # 1. Update security details view if available
        if hasattr(self, "security_view"):
            self.security_view.update_metrics(report)

        # 2. Add to in-memory session history if available
        if hasattr(self, "history_view"):
            self.history_view.add_entry(password, report.label)

        # 3. Update status bar if available
        if hasattr(self, "status_lbl"):
            self.show_status(
                f"Generated {len(password)}-char password ({report.entropy_bits:.1f} bits entropy • {report.label})",
                is_success=True,
            )

    def on_passphrase_generated(self, passphrase: str) -> None:
        """Callback triggered whenever a new passphrase is generated."""
        self.show_status(
            f"Generated high-entropy passphrase ({len(passphrase.split())} words)",
            is_success=True,
        )

    def on_select_historical_password(self, password: str) -> None:
        """Deliver historical password back to generator view and switch tab."""
        self.generator_view.load_password(password)
        self.notebook.select(0)  # Switch to Generator tab
        self.show_status("Loaded historical password into active view.", True)

    def on_settings_saved(self, updated_settings: AppSettings) -> None:
        """Handle preferences save from settings view."""
        self.settings = updated_settings
        self.generator_view.apply_settings(updated_settings)

    def show_status(self, message: str, is_success: bool = True) -> None:
        """Display feedback status in the bottom status bar."""
        if not hasattr(self, "status_lbl"):
            return
        p = self.theme_manager.palette
        fg_color = p["primary_text"] if is_success else p["strength_weak"]
        self.status_lbl.config(text=message, fg=fg_color)

    def on_theme_changed(self, theme_name: str, palette: Dict[str, str]) -> None:
        """Update window shell colors."""
        p = palette
        self.root.configure(bg=p["main_bg"])
        self.main_container.config(bg=p["main_bg"])
        self.header_bar.config(bg=p["main_bg"])
        self.brand_frame.config(bg=p["main_bg"])
        self.title_lbl.config(bg=p["main_bg"], fg=p["primary_text"])
        self.badge_lbl.config(bg=p["secondary_surface"], fg=p["primary_accent"])
        self.theme_btn.config(
            text="☀ Light" if theme_name == "dark" else "🌙 Dark",
            bg=p["secondary_surface"],
            fg=p["primary_text"],
            activebackground=p["borders"],
        )
        self.nav_divider.config(bg=p["borders"])
        self.notebook_frame.config(bg=p["main_bg"])
        self.status_bar.config(bg=p["secondary_surface"])
        self.status_lbl.config(bg=p["secondary_surface"], fg=p["secondary_text"])
        self.author_lbl.config(bg=p["secondary_surface"], fg=p["muted_text"])

    def on_close(self) -> None:
        """Clean application shutdown."""
        # Purge in-memory history
        try:
            self.history_view.clear_history()
        except Exception:
            pass
        self.root.destroy()


def main() -> None:
    """Entry point for GUI launch."""
    root = tk.Tk()
    app = SecurePasswordGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

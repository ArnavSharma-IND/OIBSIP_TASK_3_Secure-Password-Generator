"""In-memory session history UI component."""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Tuple, Callable, Optional
from config import MAX_HISTORY_ENTRIES
from themes.theme_manager import ThemeManager
from utils.helpers import mask_password, get_current_timestamp
from services.clipboard_service import copy_to_clipboard


class SessionHistoryFrame(ttk.Frame):
    """In-memory session history manager displaying up to 5 recently generated passwords."""

    def __init__(
        self,
        parent: tk.Widget,
        theme_manager: ThemeManager,
        on_select_password: Optional[Callable[[str], None]] = None,
        on_status_message: Optional[Callable[[str, bool], None]] = None,
        **kwargs,
    ):
        super().__init__(parent, style="Surface.TFrame", **kwargs)
        self.theme_manager = theme_manager
        self.on_select_password = on_select_password
        self.on_status_message = on_status_message

        # Strictly in-memory storage of entries: tuple(password, timestamp, entropy_label)
        self._history: List[Tuple[str, str, str]] = []
        self._mask_all: bool = True

        self._build_ui()
        self.theme_manager.register_listener(self.on_theme_changed)

    def _build_ui(self) -> None:
        p = self.theme_manager.palette

        self.container = tk.Frame(self, bg=p["surface"], padx=20, pady=16)
        self.container.pack(fill="both", expand=True)

        # Header with actions
        self.header_frame = tk.Frame(self.container, bg=p["surface"])
        self.header_frame.pack(fill="x", pady=(0, 8))

        self.title_lbl = tk.Label(
            self.header_frame,
            text="SESSION GENERATION HISTORY (MAX 5)",
            font=("Segoe UI", 9, "bold"),
            bg=p["surface"],
            fg=p["secondary_text"],
        )
        self.title_lbl.pack(side="left")

        # Action Buttons on right: Toggle Mask & Clear History
        self.clear_btn = tk.Button(
            self.header_frame,
            text="Clear History",
            font=("Segoe UI", 8),
            bg=p["secondary_surface"],
            fg=p["primary_text"],
            activebackground=p["borders"],
            activeforeground=p["primary_text"],
            relief="flat",
            padx=8,
            pady=2,
            command=self.clear_history,
        )
        self.clear_btn.pack(side="right", padx=(6, 0))

        self.toggle_mask_btn = tk.Button(
            self.header_frame,
            text="Show Passwords",
            font=("Segoe UI", 8),
            bg=p["secondary_surface"],
            fg=p["secondary_text"],
            activebackground=p["borders"],
            activeforeground=p["primary_text"],
            relief="flat",
            padx=8,
            pady=2,
            command=self.toggle_mask,
        )
        self.toggle_mask_btn.pack(side="right")

        # Divider line
        self.divider = tk.Frame(self.container, bg=p["borders"], height=1)
        self.divider.pack(fill="x", pady=(4, 12))

        # Dynamic entries list container
        self.entries_frame = tk.Frame(self.container, bg=p["surface"])
        self.entries_frame.pack(fill="both", expand=True)

        # Empty state label
        self.empty_lbl = tk.Label(
            self.entries_frame,
            text="No passwords generated in this session yet.\nGenerated passwords will temporarily appear here.",
            font=("Segoe UI", 9),
            bg=p["surface"],
            fg=p["muted_text"],
            justify="center",
            pady=24,
        )
        self.empty_lbl.pack(fill="x")

        # Privacy badge / footer
        self.privacy_lbl = tk.Label(
            self.container,
            text="Security notice: History exists strictly in volatile RAM and is never written to disk, logs, or databases.",
            font=("Segoe UI", 8, "italic"),
            bg=p["surface"],
            fg=p["muted_text"],
            anchor="w",
        )
        self.privacy_lbl.pack(fill="x", pady=(12, 0))

    def add_entry(self, password: str, entropy_label: str = "Strong") -> None:
        """Add a newly generated password to the session history.

        Args:
            password: The generated password.
            entropy_label: "Weak", "Medium", or "Strong".
        """
        timestamp = get_current_timestamp()
        # Insert newest first
        self._history.insert(0, (password, timestamp, entropy_label))

        # Enforce maximum of 5 entries
        if len(self._history) > MAX_HISTORY_ENTRIES:
            self._history = self._history[:MAX_HISTORY_ENTRIES]

        self.refresh_display()

    def clear_history(self) -> None:
        """Purge all entries from in-memory history."""
        self._history.clear()
        self.refresh_display()
        if self.on_status_message:
            self.on_status_message("Session history cleared securely.", True)

    def toggle_mask(self) -> None:
        """Toggle masking of history passwords."""
        self._mask_all = not self._mask_all
        self.toggle_mask_btn.config(
            text="Hide Passwords" if not self._mask_all else "Show Passwords"
        )
        self.refresh_display()

    def refresh_display(self) -> None:
        """Redraw all history rows."""
        p = self.theme_manager.palette

        # Clear existing rows in entries_frame
        for widget in self.entries_frame.winfo_children():
            widget.destroy()

        if not self._history:
            self.empty_lbl = tk.Label(
                self.entries_frame,
                text="No passwords generated in this session yet.\nGenerated passwords will temporarily appear here.",
                font=("Segoe UI", 9),
                bg=p["surface"],
                fg=p["muted_text"],
                justify="center",
                pady=24,
            )
            self.empty_lbl.pack(fill="x")
            return

        for idx, (pw, ts, rating) in enumerate(self._history):
            row = tk.Frame(self.entries_frame, bg=p["surface"], pady=4)
            row.pack(fill="x")

            # Timestamp pill
            time_lbl = tk.Label(
                row,
                text=ts,
                font=("Segoe UI", 8),
                bg=p["secondary_surface"],
                fg=p["secondary_text"],
                padx=6,
                pady=2,
            )
            time_lbl.pack(side="left", padx=(0, 10))

            # Password text (masked or unmasked)
            display_text = mask_password(pw) if self._mask_all else pw
            pw_lbl = tk.Label(
                row,
                text=display_text,
                font=("Consolas", 10, "bold"),
                bg=p["surface"],
                fg=p["primary_text"],
                anchor="w",
            )
            pw_lbl.pack(side="left", fill="x", expand=True)

            # Rating badge
            if rating == "Strong":
                rc = p["strength_strong"]
            elif rating == "Medium":
                rc = p["strength_medium"]
            else:
                rc = p["strength_weak"]

            rating_badge = tk.Label(
                row,
                text=rating.upper(),
                font=("Segoe UI", 7, "bold"),
                bg=p["secondary_surface"],
                fg=rc,
                padx=5,
                pady=2,
            )
            rating_badge.pack(side="left", padx=(6, 12))

            # Select button (loads into main view)
            sel_btn = tk.Button(
                row,
                text="Use",
                font=("Segoe UI", 8),
                bg=p["secondary_surface"],
                fg=p["primary_text"],
                activebackground=p["borders"],
                relief="flat",
                padx=8,
                pady=2,
                command=lambda p_val=pw: self._select_entry(p_val),
            )
            sel_btn.pack(side="left", padx=(0, 6))

            # Copy button
            copy_btn = tk.Button(
                row,
                text="Copy",
                font=("Segoe UI", 8),
                bg=p["secondary_surface"],
                fg=p["primary_accent"],
                activebackground=p["borders"],
                relief="flat",
                padx=8,
                pady=2,
                command=lambda p_val=pw: self._copy_entry(p_val),
            )
            copy_btn.pack(side="left")

    def _select_entry(self, password: str) -> None:
        """Select a history entry and deliver to main view."""
        if self.on_select_password:
            self.on_select_password(password)

    def _copy_entry(self, password: str) -> None:
        """Copy a history entry to clipboard."""
        ok, msg = copy_to_clipboard(password)
        if self.on_status_message:
            self.on_status_message(msg, ok)

    def on_theme_changed(self, theme_name: str, palette: Dict[str, str]) -> None:
        """Apply theme update."""
        p = palette
        self.container.config(bg=p["surface"])
        self.header_frame.config(bg=p["surface"])
        self.title_lbl.config(bg=p["surface"], fg=p["secondary_text"])
        self.clear_btn.config(
            bg=p["secondary_surface"],
            fg=p["primary_text"],
            activebackground=p["borders"],
        )
        self.toggle_mask_btn.config(
            bg=p["secondary_surface"],
            fg=p["secondary_text"],
            activebackground=p["borders"],
        )
        self.divider.config(bg=p["borders"])
        self.entries_frame.config(bg=p["surface"])
        self.privacy_lbl.config(bg=p["surface"], fg=p["muted_text"])
        self.refresh_display()

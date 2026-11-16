"""Settings and non-sensitive preferences UI component."""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable, Optional
from config import (
    APP_NAME,
    APP_VERSION,
    AUTHOR,
    APP_DESCRIPTION,
    MIN_PASSWORD_LENGTH,
    MAX_PASSWORD_LENGTH,
    DEFAULT_PASSWORD_LENGTH,
)
from themes.theme_manager import ThemeManager
from services.settings_service import AppSettings, load_settings, save_settings


class SettingsFrame(ttk.Frame):
    """User preferences configuration interface for non-sensitive options."""

    def __init__(
        self,
        parent: tk.Widget,
        theme_manager: ThemeManager,
        on_settings_saved: Optional[Callable[[AppSettings], None]] = None,
        on_status_message: Optional[Callable[[str, bool], None]] = None,
        **kwargs,
    ):
        super().__init__(parent, style="Surface.TFrame", **kwargs)
        self.theme_manager = theme_manager
        self.on_settings_saved = on_settings_saved
        self.on_status_message = on_status_message

        # Load saved settings
        self.current_settings = load_settings()

        # Tkinter state variables
        self.var_theme = tk.StringVar(value=self.current_settings.theme)
        self.var_default_len = tk.IntVar(value=self.current_settings.default_length)
        self.var_upper = tk.BooleanVar(value=self.current_settings.include_uppercase)
        self.var_lower = tk.BooleanVar(value=self.current_settings.include_lowercase)
        self.var_nums = tk.BooleanVar(value=self.current_settings.include_numbers)
        self.var_syms = tk.BooleanVar(value=self.current_settings.include_symbols)
        self.var_ambig = tk.BooleanVar(value=self.current_settings.exclude_ambiguous)
        self.var_auto_copy = tk.BooleanVar(value=self.current_settings.auto_copy)
        self.var_mask_pw = tk.BooleanVar(value=self.current_settings.mask_password)

        self._build_ui()
        self.theme_manager.register_listener(self.on_theme_changed)

    def _build_ui(self) -> None:
        p = self.theme_manager.palette

        self.container = tk.Frame(self, bg=p["surface"], padx=20, pady=16)
        self.container.pack(fill="both", expand=True)

        # Title
        self.title_lbl = tk.Label(
            self.container,
            text="APPLICATION PREFERENCES & SECURITY SETTINGS",
            font=("Segoe UI", 9, "bold"),
            bg=p["surface"],
            fg=p["secondary_text"],
            anchor="w",
        )
        self.title_lbl.pack(fill="x", pady=(0, 10))

        # Divider
        self.div1 = tk.Frame(self.container, bg=p["borders"], height=1)
        self.div1.pack(fill="x", pady=(0, 14))

        # Theme Section
        self.theme_title = tk.Label(
            self.container,
            text="VISUAL THEME",
            font=("Segoe UI", 8, "bold"),
            bg=p["surface"],
            fg=p["secondary_text"],
            anchor="w",
        )
        self.theme_title.pack(fill="x", pady=(0, 6))

        self.theme_radio_box = tk.Frame(self.container, bg=p["surface"])
        self.theme_radio_box.pack(fill="x", pady=(0, 12))

        self.rb_dark = ttk.Radiobutton(
            self.theme_radio_box,
            text="Dark Mode (Black + Soft Violet)",
            value="dark",
            variable=self.var_theme,
            command=self._apply_theme_choice,
        )
        self.rb_dark.pack(side="left", padx=(0, 20))

        self.rb_light = ttk.Radiobutton(
            self.theme_radio_box,
            text="Light Mode (Warm Beige + Burnt Orange)",
            value="light",
            variable=self.var_theme,
            command=self._apply_theme_choice,
        )
        self.rb_light.pack(side="left")

        # Default Length Slider
        self.len_header = tk.Frame(self.container, bg=p["surface"])
        self.len_header.pack(fill="x", pady=(8, 4))

        self.len_title = tk.Label(
            self.len_header,
            text="DEFAULT PASSWORD LENGTH",
            font=("Segoe UI", 8, "bold"),
            bg=p["surface"],
            fg=p["secondary_text"],
        )
        self.len_title.pack(side="left")

        self.len_val_lbl = tk.Label(
            self.len_header,
            text=f"{self.var_default_len.get()} chars",
            font=("Segoe UI", 9, "bold"),
            bg=p["surface"],
            fg=p["primary_accent"],
        )
        self.len_val_lbl.pack(side="right")

        self.len_slider = ttk.Scale(
            self.container,
            from_=MIN_PASSWORD_LENGTH,
            to=64,
            variable=self.var_default_len,
            command=self._on_len_changed,
            style="Horizontal.TScale",
        )
        self.len_slider.pack(fill="x", pady=(0, 12))

        # Workflow Preferences
        self.workflow_title = tk.Label(
            self.container,
            text="WORKFLOW PREFERENCES",
            font=("Segoe UI", 8, "bold"),
            bg=p["surface"],
            fg=p["secondary_text"],
            anchor="w",
        )
        self.workflow_title.pack(fill="x", pady=(4, 6))

        self.chk_auto_copy = ttk.Checkbutton(
            self.container,
            text="Automatically copy newly generated passwords to clipboard",
            variable=self.var_auto_copy,
        )
        self.chk_auto_copy.pack(anchor="w", pady=2)

        self.chk_mask_default = ttk.Checkbutton(
            self.container,
            text="Mask passwords with bullets (•••) by default",
            variable=self.var_mask_pw,
        )
        self.chk_mask_default.pack(anchor="w", pady=2)

        self.chk_ambig_default = ttk.Checkbutton(
            self.container,
            text="Exclude ambiguous characters (0, O, o, l, 1, I) by default",
            variable=self.var_ambig,
        )
        self.chk_ambig_default.pack(anchor="w", pady=2)

        # Action Buttons
        self.btn_row = tk.Frame(self.container, bg=p["surface"])
        self.btn_row.pack(fill="x", pady=(16, 12))

        self.save_btn = ttk.Button(
            self.btn_row,
            text="Save Preferences",
            style="Primary.TButton",
            command=self.save,
        )
        self.save_btn.pack(side="left", padx=(0, 10))

        self.reset_btn = ttk.Button(
            self.btn_row,
            text="Reset to Factory Defaults",
            style="Secondary.TButton",
            command=self.reset_defaults,
        )
        self.reset_btn.pack(side="left")

        # Security declaration box
        self.sec_box = tk.Frame(
            self.container,
            bg=p["secondary_surface"],
            highlightbackground=p["borders"],
            highlightthickness=1,
            padx=12,
            pady=10,
        )
        self.sec_box.pack(fill="x", pady=(10, 0))

        self.sec_box_title = tk.Label(
            self.sec_box,
            text="ZERO-KNOWLEDGE LOCAL PRIVACY ASSURANCE",
            font=("Segoe UI", 8, "bold"),
            bg=p["secondary_surface"],
            fg=p["primary_text"],
            anchor="w",
        )
        self.sec_box_title.pack(fill="x")

        self.sec_box_text = tk.Label(
            self.sec_box,
            text=(
                f"{APP_NAME} v{APP_VERSION} by {AUTHOR}. Generated passwords and session histories "
                "are strictly stored in volatile application memory. The configuration file persists only non-sensitive "
                "preferences (theme, length, checkbox defaults). Zero passwords or sensitive cryptographic material are ever saved to disk."
            ),
            font=("Segoe UI", 8),
            bg=p["secondary_surface"],
            fg=p["secondary_text"],
            wraplength=620,
            justify="left",
            anchor="w",
        )
        self.sec_box_text.pack(fill="x", pady=(4, 0))

    def _apply_theme_choice(self) -> None:
        """Apply theme change dynamically."""
        choice = self.var_theme.get()
        self.theme_manager.set_theme(choice)

    def _on_len_changed(self, val: str) -> None:
        """Update length readout label."""
        count = int(round(float(val)))
        self.var_default_len.set(count)
        self.len_val_lbl.config(text=f"{count} chars")

    def save(self) -> None:
        """Save settings to disk."""
        settings = AppSettings(
            theme=self.var_theme.get(),
            default_length=self.var_default_len.get(),
            include_uppercase=self.var_upper.get(),
            include_lowercase=self.var_lower.get(),
            include_numbers=self.var_nums.get(),
            include_symbols=self.var_syms.get(),
            exclude_ambiguous=self.var_ambig.get(),
            auto_copy=self.var_auto_copy.get(),
            mask_password=self.var_mask_pw.get(),
        )
        ok = save_settings(settings)
        self.current_settings = settings
        if self.on_settings_saved:
            self.on_settings_saved(settings)
        if self.on_status_message:
            msg = "Preferences saved successfully." if ok else "Failed to persist preferences."
            self.on_status_message(msg, ok)

    def reset_defaults(self) -> None:
        """Reset controls to default values."""
        defaults = AppSettings()
        self.var_theme.set(defaults.theme)
        self.var_default_len.set(defaults.default_length)
        self.var_upper.set(defaults.include_uppercase)
        self.var_lower.set(defaults.include_lowercase)
        self.var_nums.set(defaults.include_numbers)
        self.var_syms.set(defaults.include_symbols)
        self.var_ambig.set(defaults.exclude_ambiguous)
        self.var_auto_copy.set(defaults.auto_copy)
        self.var_mask_pw.set(defaults.mask_password)
        self._apply_theme_choice()
        self.len_val_lbl.config(text=f"{defaults.default_length} chars")
        self.save()

    def on_theme_changed(self, theme_name: str, palette: Dict[str, str]) -> None:
        """Update colors on theme toggle."""
        p = palette
        self.var_theme.set(theme_name)
        self.container.config(bg=p["surface"])
        self.title_lbl.config(bg=p["surface"], fg=p["secondary_text"])
        self.div1.config(bg=p["borders"])
        self.theme_title.config(bg=p["surface"], fg=p["secondary_text"])
        self.theme_radio_box.config(bg=p["surface"])
        self.len_header.config(bg=p["surface"])
        self.len_title.config(bg=p["surface"], fg=p["secondary_text"])
        self.len_val_lbl.config(bg=p["surface"], fg=p["primary_accent"])
        self.workflow_title.config(bg=p["surface"], fg=p["secondary_text"])
        self.btn_row.config(bg=p["surface"])
        self.sec_box.config(
            bg=p["secondary_surface"],
            highlightbackground=p["borders"],
        )
        self.sec_box_title.config(bg=p["secondary_surface"], fg=p["primary_text"])
        self.sec_box_text.config(bg=p["secondary_surface"], fg=p["secondary_text"])

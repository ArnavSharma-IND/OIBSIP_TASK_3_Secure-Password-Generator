"""Flagship generator UI view combining controls, password hero display, and strength indicator."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Callable, Optional, Tuple
from config import (
    MIN_PASSWORD_LENGTH,
    MAX_PASSWORD_LENGTH,
    DEFAULT_PASSWORD_LENGTH,
    PRESETS,
)
from themes.theme_manager import ThemeManager
from services.generation_service import generate_secure_password
from services.clipboard_service import copy_to_clipboard
from services.settings_service import AppSettings
from password_strength import evaluate_password_strength, StrengthReport
from utils.validators import ValidationError, validate_password_length
from utils.helpers import mask_password


class PasswordGeneratorUI(ttk.Frame):
    """Main password generator view featuring hero display, controls, and strength metrics."""

    def __init__(
        self,
        parent: tk.Widget,
        theme_manager: ThemeManager,
        settings: AppSettings,
        on_password_generated: Optional[Callable[[str, StrengthReport], None]] = None,
        on_status_message: Optional[Callable[[str, bool], None]] = None,
        **kwargs,
    ):
        super().__init__(parent, style="Surface.TFrame", **kwargs)
        self.theme_manager = theme_manager
        self.settings = settings
        self.on_password_generated = on_password_generated
        self.on_status_message = on_status_message

        # Internal state
        self._current_password: str = ""
        self._is_masked: bool = self.settings.mask_password
        self._last_report: Optional[StrengthReport] = None

        # Tkinter Control Variables
        self.var_length = tk.IntVar(value=self.settings.default_length)
        self.var_length_str = tk.StringVar(value=str(self.settings.default_length))
        self.var_upper = tk.BooleanVar(value=self.settings.include_uppercase)
        self.var_lower = tk.BooleanVar(value=self.settings.include_lowercase)
        self.var_nums = tk.BooleanVar(value=self.settings.include_numbers)
        self.var_syms = tk.BooleanVar(value=self.settings.include_symbols)
        self.var_ambig = tk.BooleanVar(value=self.settings.exclude_ambiguous)
        self.var_preset = tk.StringVar(value="Strong" if self.settings.default_length == 16 else "Custom")

        self._build_ui()
        self.theme_manager.register_listener(self.on_theme_changed)

        # Generate initial password on startup
        self.generate()

    def _build_ui(self) -> None:
        p = self.theme_manager.palette

        # Floating main canvas container
        self.container = tk.Frame(self, bg=p["surface"], padx=24, pady=20)
        self.container.pack(fill="both", expand=True)

        # -------------------------------------------------------------
        # 1. HERO PASSWORD DISPLAY
        # -------------------------------------------------------------
        self.hero_frame = tk.Frame(
            self.container,
            bg=p["code_bg"],
            highlightbackground=p["borders"],
            highlightthickness=1,
            padx=18,
            pady=16,
        )
        self.hero_frame.pack(fill="x", pady=(0, 10))

        # Password text display
        self.password_display = tk.Label(
            self.hero_frame,
            text="",
            font=("Consolas", 15, "bold"),
            bg=p["code_bg"],
            fg=p["code_fg"],
            anchor="w",
            cursor="xterm",
            wraplength=520,
            justify="left",
        )
        self.password_display.pack(side="left", fill="x", expand=True)

        # Action Buttons Inside Hero Box
        self.hero_actions_frame = tk.Frame(self.hero_frame, bg=p["code_bg"])
        self.hero_actions_frame.pack(side="right")

        # Show / Hide Toggle Button
        self.btn_toggle_mask = tk.Button(
            self.hero_actions_frame,
            text="Show" if self._is_masked else "Hide",
            font=("Segoe UI", 9),
            bg=p["secondary_surface"],
            fg=p["secondary_text"],
            activebackground=p["borders"],
            activeforeground=p["primary_text"],
            relief="flat",
            padx=10,
            pady=4,
            command=self.toggle_mask,
        )
        self.btn_toggle_mask.pack(side="left", padx=(0, 6))

        # Copy to Clipboard Button
        self.btn_copy = tk.Button(
            self.hero_actions_frame,
            text="Copy",
            font=("Segoe UI", 9, "bold"),
            bg=p["primary_accent"],
            fg=p["accent_text"],
            activebackground=p["muted_accent"],
            activeforeground=p["accent_text"],
            relief="flat",
            padx=14,
            pady=4,
            command=self.copy_current_password,
        )
        self.btn_copy.pack(side="left")

        # -------------------------------------------------------------
        # 2. STRENGTH PROGRESS BAR & DIAGNOSTIC LABEL
        # -------------------------------------------------------------
        self.strength_container = tk.Frame(self.container, bg=p["surface"])
        self.strength_container.pack(fill="x", pady=(0, 16))

        # Visual progress bar with custom Canvas for precise color mapping
        self.strength_canvas = tk.Canvas(
            self.strength_container,
            height=6,
            bg=p["secondary_surface"],
            highlightthickness=0,
            bd=0,
        )
        self.strength_canvas.pack(fill="x", pady=(0, 6))

        self.strength_meta_frame = tk.Frame(self.strength_container, bg=p["surface"])
        self.strength_meta_frame.pack(fill="x")

        self.lbl_strength_badge = tk.Label(
            self.strength_meta_frame,
            text="STRONG",
            font=("Segoe UI", 8, "bold"),
            bg=p["secondary_surface"],
            fg=p["strength_strong"],
            padx=6,
            pady=2,
        )
        self.lbl_strength_badge.pack(side="left")

        self.lbl_strength_text = tk.Label(
            self.strength_meta_frame,
            text="Evaluating entropy...",
            font=("Segoe UI", 8),
            bg=p["surface"],
            fg=p["secondary_text"],
            padx=8,
        )
        self.lbl_strength_text.pack(side="left", fill="x", expand=True)

        # -------------------------------------------------------------
        # 3. CONTROLS SECTION: LENGTH & PRESETS
        # -------------------------------------------------------------
        self.length_section = tk.Frame(self.container, bg=p["surface"])
        self.length_section.pack(fill="x", pady=(0, 14))

        # Header with label, numerical input, and presets
        self.length_header = tk.Frame(self.length_section, bg=p["surface"])
        self.length_header.pack(fill="x", pady=(0, 6))

        self.lbl_length_title = tk.Label(
            self.length_header,
            text="PASSWORD LENGTH",
            font=("Segoe UI", 8, "bold"),
            bg=p["surface"],
            fg=p["secondary_text"],
        )
        self.lbl_length_title.pack(side="left")

        # Numerical entry for exact length editing
        self.entry_length = tk.Entry(
            self.length_header,
            textvariable=self.var_length_str,
            font=("Segoe UI", 9, "bold"),
            width=5,
            justify="center",
            bg=p["code_bg"],
            fg=p["primary_accent"],
            highlightbackground=p["borders"],
            highlightthickness=1,
            relief="flat",
        )
        self.entry_length.pack(side="right", padx=(8, 0))
        self.entry_length.bind("<FocusOut>", self._on_entry_length_focusout)
        self.entry_length.bind("<Return>", self._on_entry_length_return)

        # Preset Pills (Standard, Strong, Maximum)
        self.presets_frame = tk.Frame(self.length_header, bg=p["surface"])
        self.presets_frame.pack(side="right", padx=(0, 10))

        self.preset_buttons: Dict[str, tk.Button] = {}
        for name, length_val in PRESETS.items():
            btn = tk.Button(
                self.presets_frame,
                text=f"{name} ({length_val})",
                font=("Segoe UI", 7, "bold"),
                bg=p["secondary_surface"],
                fg=p["secondary_text"],
                activebackground=p["borders"],
                relief="flat",
                padx=6,
                pady=2,
                command=lambda l=length_val, n=name: self._apply_preset(l, n),
            )
            btn.pack(side="left", padx=2)
            self.preset_buttons[name] = btn

        # Slider
        self.length_slider = ttk.Scale(
            self.length_section,
            from_=MIN_PASSWORD_LENGTH,
            to=64,
            variable=self.var_length,
            command=self._on_slider_changed,
            style="Horizontal.TScale",
        )
        self.length_slider.pack(fill="x")

        # -------------------------------------------------------------
        # 4. CHARACTER CATEGORIES & AMBIGUOUS EXCLUSION
        # -------------------------------------------------------------
        self.categories_section = tk.Frame(self.container, bg=p["surface"])
        self.categories_section.pack(fill="x", pady=(0, 16))

        self.lbl_categories_title = tk.Label(
            self.categories_section,
            text="CHARACTER POOLS & COMPLEXITY (MINIMUM 2 REQUIRED)",
            font=("Segoe UI", 8, "bold"),
            bg=p["surface"],
            fg=p["secondary_text"],
            anchor="w",
        )
        self.lbl_categories_title.pack(fill="x", pady=(0, 8))

        # Checkboxes Grid (2x2 layout with ample spacing)
        self.chk_grid = tk.Frame(self.categories_section, bg=p["surface"])
        self.chk_grid.pack(fill="x", pady=(0, 8))
        self.chk_grid.columnconfigure(0, weight=1)
        self.chk_grid.columnconfigure(1, weight=1)

        self.chk_upper = ttk.Checkbutton(
            self.chk_grid,
            text="Uppercase Letters (A–Z)",
            variable=self.var_upper,
            command=self._on_option_changed,
        )
        self.chk_upper.grid(row=0, column=0, sticky="w", pady=4)

        self.chk_lower = ttk.Checkbutton(
            self.chk_grid,
            text="Lowercase Letters (a–z)",
            variable=self.var_lower,
            command=self._on_option_changed,
        )
        self.chk_lower.grid(row=0, column=1, sticky="w", pady=4)

        self.chk_nums = ttk.Checkbutton(
            self.chk_grid,
            text="Numbers (0–9)",
            variable=self.var_nums,
            command=self._on_option_changed,
        )
        self.chk_nums.grid(row=1, column=0, sticky="w", pady=4)

        self.chk_syms = ttk.Checkbutton(
            self.chk_grid,
            text="Symbols (!@#$%^&*...)",
            variable=self.var_syms,
            command=self._on_option_changed,
        )
        self.chk_syms.grid(row=1, column=1, sticky="w", pady=4)

        # Ambiguous character exclusion checkbox
        self.chk_ambig = ttk.Checkbutton(
            self.categories_section,
            text="Exclude ambiguous characters (0, O, o, l, 1, I)",
            variable=self.var_ambig,
            command=self._on_option_changed,
        )
        self.chk_ambig.pack(anchor="w", pady=(4, 0))

        # -------------------------------------------------------------
        # 5. GENERATE & REGENERATE ACTIONS
        # -------------------------------------------------------------
        self.actions_frame = tk.Frame(self.container, bg=p["surface"])
        self.actions_frame.pack(fill="x", pady=(4, 0))

        self.btn_generate = ttk.Button(
            self.actions_frame,
            text="Generate Password (↵)",
            style="Primary.TButton",
            command=self.generate,
        )
        self.btn_generate.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.btn_regenerate = ttk.Button(
            self.actions_frame,
            text="Regenerate",
            style="Secondary.TButton",
            command=self.generate,
        )
        self.btn_regenerate.pack(side="left")

    def _apply_preset(self, length: int, name: str) -> None:
        """Apply a selected password length preset."""
        self.var_length.set(length)
        self.var_length_str.set(str(length))
        self.var_preset.set(name)
        self._update_preset_buttons()
        self.generate()

    def _update_preset_buttons(self) -> None:
        """Highlight currently active preset button."""
        p = self.theme_manager.palette
        current_len = self.var_length.get()
        for name, length_val in PRESETS.items():
            btn = self.preset_buttons.get(name)
            if not btn:
                continue
            if current_len == length_val:
                btn.config(bg=p["primary_accent"], fg=p["accent_text"])
            else:
                btn.config(bg=p["secondary_surface"], fg=p["secondary_text"])

    def _on_slider_changed(self, val: str) -> None:
        """Handle length slider dragging."""
        length = int(round(float(val)))
        self.var_length.set(length)
        self.var_length_str.set(str(length))
        self._update_preset_buttons()
        self.generate()

    def _on_entry_length_focusout(self, event=None) -> None:
        """Validate and apply manually entered length."""
        self._apply_manual_length()

    def _on_entry_length_return(self, event=None) -> None:
        """Handle Enter key in length entry."""
        self._apply_manual_length()

    def _apply_manual_length(self) -> None:
        raw_val = self.var_length_str.get()
        try:
            valid_len = validate_password_length(
                raw_val,
                min_length=MIN_PASSWORD_LENGTH,
                max_length=MAX_PASSWORD_LENGTH,
            )
            self.var_length.set(valid_len)
            self.var_length_str.set(str(valid_len))
            self._update_preset_buttons()
            self.generate()
        except ValidationError as err:
            messagebox.showerror("Invalid Password Length", str(err), parent=self)
            self.var_length_str.set(str(self.var_length.get()))

    def _on_option_changed(self) -> None:
        """Handle checkbox updates."""
        self.generate()

    def generate(self) -> None:
        """Generate a cryptographically secure password based on active inputs."""
        length = self.var_length.get()
        upper = self.var_upper.get()
        lower = self.var_lower.get()
        nums = self.var_nums.get()
        syms = self.var_syms.get()
        ambig = self.var_ambig.get()

        try:
            password = generate_secure_password(
                length=length,
                uppercase=upper,
                lowercase=lower,
                numbers=nums,
                symbols=syms,
                exclude_ambiguous=ambig,
            )
        except ValidationError as err:
            messagebox.showwarning("Validation Error", str(err), parent=self)
            return
        except Exception as exc:
            messagebox.showerror("Generation Error", f"Unexpected error: {exc}", parent=self)
            return

        self._current_password = password
        self._update_password_display()

        # Evaluate strength
        report = evaluate_password_strength(
            length=length,
            uppercase=upper,
            lowercase=lower,
            numbers=nums,
            symbols=syms,
            exclude_ambiguous=ambig,
            password_text=password,
        )
        self._last_report = report
        self._update_strength_display(report)

        # Notify parent / listeners
        if self.on_password_generated:
            self.on_password_generated(password, report)

        # Auto-copy if configured
        if self.settings.auto_copy:
            ok, msg = copy_to_clipboard(password)
            if self.on_status_message:
                self.on_status_message(f"Auto-{msg}", ok)

    def load_password(self, password: str) -> None:
        """Load an external or historical password into the hero view."""
        self._current_password = password
        self.var_length.set(len(password))
        self.var_length_str.set(str(len(password)))
        self._update_password_display()

        report = evaluate_password_strength(
            length=len(password),
            password_text=password,
        )
        self._last_report = report
        self._update_strength_display(report)
        self._update_preset_buttons()

        if self.on_password_generated:
            self.on_password_generated(password, report)

    def _update_password_display(self) -> None:
        """Render password respecting current mask state."""
        if not self._current_password:
            self.password_display.config(text="")
            return

        if self._is_masked:
            self.password_display.config(text=mask_password(self._current_password))
        else:
            self.password_display.config(text=self._current_password)

    def _update_strength_display(self, report: StrengthReport) -> None:
        """Render the strength bar and badge based on report metrics."""
        p = self.theme_manager.palette

        if report.label == "Strong":
            color = p["strength_strong"]
        elif report.label == "Medium":
            color = p["strength_medium"]
        else:
            color = p["strength_weak"]

        self.lbl_strength_badge.config(text=report.label.upper(), fg=color)
        self.lbl_strength_text.config(
            text=f"{report.entropy_bits:.1f} bits entropy • {report.pool_size} chars pool • Crack time: {report.crack_time_estimate}"
        )

        # Draw smooth progress line on Canvas
        self.strength_canvas.delete("all")
        width = self.strength_canvas.winfo_width()
        if width <= 1:
            width = 500  # Fallback prior to window mapping
        fill_width = max(10, int((report.percent / 100.0) * width))
        self.strength_canvas.create_rectangle(
            0, 0, fill_width, 6, fill=color, outline=""
        )

    def toggle_mask(self) -> None:
        """Toggle bullet masking on the hero password display."""
        self._is_masked = not self._is_masked
        self.btn_toggle_mask.config(text="Show" if self._is_masked else "Hide")
        self._update_password_display()

    def copy_current_password(self) -> None:
        """Copy current password to clipboard."""
        if not self._current_password:
            if self.on_status_message:
                self.on_status_message("No password generated to copy.", False)
            return

        ok, msg = copy_to_clipboard(self._current_password)
        if self.on_status_message:
            self.on_status_message(msg, ok)

    def apply_settings(self, settings: AppSettings) -> None:
        """Apply newly updated user settings."""
        self.settings = settings
        self.var_length.set(settings.default_length)
        self.var_length_str.set(str(settings.default_length))
        self.var_upper.set(settings.include_uppercase)
        self.var_lower.set(settings.include_lowercase)
        self.var_nums.set(settings.include_numbers)
        self.var_syms.set(settings.include_symbols)
        self.var_ambig.set(settings.exclude_ambiguous)
        self._is_masked = settings.mask_password
        self.btn_toggle_mask.config(text="Show" if self._is_masked else "Hide")
        self.generate()

    def on_theme_changed(self, theme_name: str, palette: Dict[str, str]) -> None:
        """Apply colors on theme change."""
        p = palette
        self.container.config(bg=p["surface"])
        self.hero_frame.config(
            bg=p["code_bg"],
            highlightbackground=p["borders"],
        )
        self.password_display.config(bg=p["code_bg"], fg=p["code_fg"])
        self.hero_actions_frame.config(bg=p["code_bg"])
        self.btn_toggle_mask.config(
            bg=p["secondary_surface"],
            fg=p["secondary_text"],
            activebackground=p["borders"],
            activeforeground=p["primary_text"],
        )
        self.btn_copy.config(
            bg=p["primary_accent"],
            fg=p["accent_text"],
            activebackground=p["muted_accent"],
            activeforeground=p["accent_text"],
        )
        self.strength_container.config(bg=p["surface"])
        self.strength_canvas.config(bg=p["secondary_surface"])
        self.strength_meta_frame.config(bg=p["surface"])
        self.lbl_strength_badge.config(bg=p["secondary_surface"])
        self.lbl_strength_text.config(bg=p["surface"], fg=p["secondary_text"])
        self.length_section.config(bg=p["surface"])
        self.length_header.config(bg=p["surface"])
        self.lbl_length_title.config(bg=p["surface"], fg=p["secondary_text"])
        self.entry_length.config(
            bg=p["code_bg"],
            fg=p["primary_accent"],
            highlightbackground=p["borders"],
        )
        self.presets_frame.config(bg=p["surface"])
        self.categories_section.config(bg=p["surface"])
        self.lbl_categories_title.config(bg=p["surface"], fg=p["secondary_text"])
        self.chk_grid.config(bg=p["surface"])
        self.actions_frame.config(bg=p["surface"])

        self._update_preset_buttons()
        if self._last_report:
            self._update_strength_display(self._last_report)

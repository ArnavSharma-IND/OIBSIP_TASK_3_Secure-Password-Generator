"""Passphrase generation view using secure random word selection."""

import math
import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable, Optional
from themes.theme_manager import ThemeManager
from utils.wordlist import EFF_WORDLIST
from utils.helpers import mask_password
from services.generation_service import generate_secure_passphrase
from services.clipboard_service import copy_to_clipboard


class PassphraseGeneratorFrame(ttk.Frame):
    """UI view for generating memorable, high-entropy passphrases."""

    def __init__(
        self,
        parent: tk.Widget,
        theme_manager: ThemeManager,
        on_passphrase_generated: Optional[Callable[[str], None]] = None,
        on_status_message: Optional[Callable[[str, bool], None]] = None,
        **kwargs,
    ):
        super().__init__(parent, style="Surface.TFrame", **kwargs)
        self.theme_manager = theme_manager
        self.on_passphrase_generated = on_passphrase_generated
        self.on_status_message = on_status_message

        self._current_passphrase: str = ""
        self._is_masked: bool = False

        # State variables
        self.var_word_count = tk.IntVar(value=4)
        self.var_separator = tk.StringVar(value="-")
        self.var_capitalize = tk.BooleanVar(value=True)
        self.var_number = tk.BooleanVar(value=True)

        self._build_ui()
        self.theme_manager.register_listener(self.on_theme_changed)
        self.generate()

    def _build_ui(self) -> None:
        p = self.theme_manager.palette

        self.container = tk.Frame(self, bg=p["surface"], padx=20, pady=16)
        self.container.pack(fill="both", expand=True)

        # Header Title
        self.title_lbl = tk.Label(
            self.container,
            text="MEMORABLE SECURE PASSPHRASE GENERATOR",
            font=("Segoe UI", 9, "bold"),
            bg=p["surface"],
            fg=p["secondary_text"],
            anchor="w",
        )
        self.title_lbl.pack(fill="x", pady=(0, 10))

        # Divider line
        self.divider = tk.Frame(self.container, bg=p["borders"], height=1)
        self.divider.pack(fill="x", pady=(0, 14))

        # Hero Passphrase Display Container
        self.display_box = tk.Frame(
            self.container,
            bg=p["code_bg"],
            highlightbackground=p["borders"],
            highlightthickness=1,
            padx=14,
            pady=12,
        )
        self.display_box.pack(fill="x", pady=(0, 14))

        self.passphrase_lbl = tk.Label(
            self.display_box,
            text="",
            font=("Consolas", 13, "bold"),
            bg=p["code_bg"],
            fg=p["code_fg"],
            anchor="w",
            wraplength=600,
            justify="left",
        )
        self.passphrase_lbl.pack(side="left", fill="x", expand=True)

        # Toggle mask button
        self.mask_btn = tk.Button(
            self.display_box,
            text="Hide",
            font=("Segoe UI", 8),
            bg=p["secondary_surface"],
            fg=p["secondary_text"],
            activebackground=p["borders"],
            relief="flat",
            padx=8,
            pady=4,
            command=self.toggle_mask,
        )
        self.mask_btn.pack(side="right", padx=(8, 0))

        # Copy button
        self.copy_btn = tk.Button(
            self.display_box,
            text="Copy",
            font=("Segoe UI", 8, "bold"),
            bg=p["primary_accent"],
            fg=p["accent_text"],
            activebackground=p["muted_accent"],
            activeforeground=p["accent_text"],
            relief="flat",
            padx=10,
            pady=4,
            command=self.copy_passphrase,
        )
        self.copy_btn.pack(side="right")

        # Controls Grid
        self.controls_frame = tk.Frame(self.container, bg=p["surface"])
        self.controls_frame.pack(fill="x", pady=(0, 12))
        self.controls_frame.columnconfigure(0, weight=1)
        self.controls_frame.columnconfigure(1, weight=1)

        # Word count slider
        self.words_frame = tk.Frame(self.controls_frame, bg=p["surface"])
        self.words_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.words_header = tk.Frame(self.words_frame, bg=p["surface"])
        self.words_header.pack(fill="x", pady=(0, 4))

        self.words_title = tk.Label(
            self.words_header,
            text="WORD COUNT",
            font=("Segoe UI", 8, "bold"),
            bg=p["surface"],
            fg=p["secondary_text"],
        )
        self.words_title.pack(side="left")

        self.words_val_lbl = tk.Label(
            self.words_header,
            text="4 words",
            font=("Segoe UI", 9, "bold"),
            bg=p["surface"],
            fg=p["primary_accent"],
        )
        self.words_val_lbl.pack(side="right")

        self.slider = ttk.Scale(
            self.words_frame,
            from_=3,
            to=8,
            variable=self.var_word_count,
            command=self._on_slider_changed,
            style="Horizontal.TScale",
        )
        self.slider.pack(fill="x")

        # Separator Selection
        self.sep_frame = tk.Frame(self.controls_frame, bg=p["surface"])
        self.sep_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self.sep_title = tk.Label(
            self.sep_frame,
            text="SEPARATOR",
            font=("Segoe UI", 8, "bold"),
            bg=p["surface"],
            fg=p["secondary_text"],
            anchor="w",
        )
        self.sep_title.pack(fill="x", pady=(0, 4))

        self.sep_buttons_box = tk.Frame(self.sep_frame, bg=p["surface"])
        self.sep_buttons_box.pack(fill="x")

        for s_char, label in [("-", "Hyphen (-)"), (".", "Period (.)"), ("_", "Underscore (_)"), (" ", "Space")]:
            rb = ttk.Radiobutton(
                self.sep_buttons_box,
                text=label,
                value=s_char,
                variable=self.var_separator,
                command=self.generate,
            )
            rb.pack(side="left", padx=(0, 8))

        # Checkboxes: Capitalize & Number
        self.chk_frame = tk.Frame(self.container, bg=p["surface"])
        self.chk_frame.pack(fill="x", pady=(6, 12))

        self.chk_cap = ttk.Checkbutton(
            self.chk_frame,
            text="Capitalize each word",
            variable=self.var_capitalize,
            command=self.generate,
        )
        self.chk_cap.pack(side="left", padx=(0, 20))

        self.chk_num = ttk.Checkbutton(
            self.chk_frame,
            text="Append secure number",
            variable=self.var_number,
            command=self.generate,
        )
        self.chk_num.pack(side="left")

        # Entropy & Wordlist Note
        self.entropy_lbl = tk.Label(
            self.container,
            text="",
            font=("Segoe UI", 8),
            bg=p["surface"],
            fg=p["secondary_text"],
            anchor="w",
        )
        self.entropy_lbl.pack(fill="x", pady=(0, 12))

        # Action: Generate Button
        self.gen_btn = ttk.Button(
            self.container,
            text="Generate Passphrase",
            style="Primary.TButton",
            command=self.generate,
        )
        self.gen_btn.pack(fill="x")

    def _on_slider_changed(self, val: str) -> None:
        """Handle word count slider changes."""
        count = int(round(float(val)))
        self.var_word_count.set(count)
        self.words_val_lbl.config(text=f"{count} words")
        self.generate()

    def generate(self) -> None:
        """Generate a new passphrase."""
        words = self.var_word_count.get()
        sep = self.var_separator.get()
        cap = self.var_capitalize.get()
        num = self.var_number.get()

        self._current_passphrase = generate_secure_passphrase(
            word_count=words,
            separator=sep,
            capitalize=cap,
            include_number=num,
        )

        self._update_display()

        # Calculate wordlist entropy
        wordlist_size = len(EFF_WORDLIST)
        base_bits = words * math.log2(wordlist_size)
        if num:
            base_bits += math.log2(90)  # 2-digit number entropy
        self.entropy_lbl.config(
            text=f"Estimated Diceware Entropy: ~{base_bits:.1f} bits | Pool: {wordlist_size} curated English words."
        )

        if self.on_passphrase_generated:
            self.on_passphrase_generated(self._current_passphrase)

    def _update_display(self) -> None:
        """Update display label respecting masking."""
        if self._is_masked:
            self.passphrase_lbl.config(text=mask_password(self._current_passphrase))
        else:
            self.passphrase_lbl.config(text=self._current_passphrase)

    def toggle_mask(self) -> None:
        """Toggle masked state."""
        self._is_masked = not self._is_masked
        self.mask_btn.config(text="Show" if self._is_masked else "Hide")
        self._update_display()

    def copy_passphrase(self) -> None:
        """Copy current passphrase to clipboard."""
        ok, msg = copy_to_clipboard(self._current_passphrase)
        if self.on_status_message:
            self.on_status_message(msg, ok)

    def on_theme_changed(self, theme_name: str, palette: Dict[str, str]) -> None:
        """Update widget colors on theme change."""
        p = palette
        self.container.config(bg=p["surface"])
        self.title_lbl.config(bg=p["surface"], fg=p["secondary_text"])
        self.divider.config(bg=p["borders"])
        self.display_box.config(
            bg=p["code_bg"],
            highlightbackground=p["borders"],
        )
        self.passphrase_lbl.config(bg=p["code_bg"], fg=p["code_fg"])
        self.mask_btn.config(
            bg=p["secondary_surface"],
            fg=p["secondary_text"],
            activebackground=p["borders"],
        )
        self.copy_btn.config(
            bg=p["primary_accent"],
            fg=p["accent_text"],
            activebackground=p["muted_accent"],
        )
        self.controls_frame.config(bg=p["surface"])
        self.words_frame.config(bg=p["surface"])
        self.words_header.config(bg=p["surface"])
        self.words_title.config(bg=p["surface"], fg=p["secondary_text"])
        self.words_val_lbl.config(bg=p["surface"], fg=p["primary_accent"])
        self.sep_frame.config(bg=p["surface"])
        self.sep_title.config(bg=p["surface"], fg=p["secondary_text"])
        self.sep_buttons_box.config(bg=p["surface"])
        self.chk_frame.config(bg=p["surface"])
        self.entropy_lbl.config(bg=p["surface"], fg=p["secondary_text"])

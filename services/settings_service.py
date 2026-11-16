"""Settings persistence service for non-sensitive user preferences.

STRICT SECURITY RULE:
Never save generated passwords, session history, or sensitive cryptographic keys.
Only non-sensitive UI and generator preferences (theme, default length, category flags)
are stored.
"""

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict
from config import (
    DEFAULT_PASSWORD_LENGTH,
    MIN_PASSWORD_LENGTH,
    MAX_PASSWORD_LENGTH,
    SETTINGS_FILENAME,
)


@dataclass
class AppSettings:
    """Non-sensitive application configuration model."""
    theme: str = "dark"                   # "dark" or "light"
    default_length: int = DEFAULT_PASSWORD_LENGTH
    include_uppercase: bool = True
    include_lowercase: bool = True
    include_numbers: bool = True
    include_symbols: bool = True
    exclude_ambiguous: bool = False
    auto_copy: bool = False               # Auto copy on generation
    mask_password: bool = False           # Mask password in display by default


def get_settings_file_path() -> Path:
    """Determine the file path for persistent non-sensitive settings.

    Returns:
        Path: Path to JSON configuration file.
    """
    # Use user's home directory or local directory fallback
    home = Path.home()
    config_dir = home / ".secure_password_generator"
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / SETTINGS_FILENAME
    except (OSError, PermissionError):
        # Fallback to local directory
        return Path(SETTINGS_FILENAME)


def load_settings() -> AppSettings:
    """Load non-sensitive preferences from disk or return default settings.

    Returns:
        AppSettings: The loaded or default application settings.
    """
    settings_path = get_settings_file_path()
    defaults = AppSettings()

    if not settings_path.exists():
        return defaults

    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Sanitize and validate loaded data
        theme = data.get("theme", defaults.theme)
        if theme not in ("dark", "light"):
            theme = defaults.theme

        length = data.get("default_length", defaults.default_length)
        if not isinstance(length, int) or length < MIN_PASSWORD_LENGTH or length > MAX_PASSWORD_LENGTH:
            length = defaults.default_length

        return AppSettings(
            theme=theme,
            default_length=length,
            include_uppercase=bool(data.get("include_uppercase", defaults.include_uppercase)),
            include_lowercase=bool(data.get("include_lowercase", defaults.include_lowercase)),
            include_numbers=bool(data.get("include_numbers", defaults.include_numbers)),
            include_symbols=bool(data.get("include_symbols", defaults.include_symbols)),
            exclude_ambiguous=bool(data.get("exclude_ambiguous", defaults.exclude_ambiguous)),
            auto_copy=bool(data.get("auto_copy", defaults.auto_copy)),
            mask_password=bool(data.get("mask_password", defaults.mask_password)),
        )
    except Exception:
        # On any corruption or read failure, safely fallback to defaults
        return defaults


def save_settings(settings: AppSettings) -> bool:
    """Persist non-sensitive preferences to disk.

    Args:
        settings: AppSettings instance to persist.

    Returns:
        bool: True if saved successfully, False otherwise.
    """
    settings_path = get_settings_file_path()
    try:
        data = asdict(settings)
        # Ensure directory exists
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False

"""Configuration constants and defaults for Secure Password Generator."""

import string
from typing import Final, Dict

# Application Metadata
APP_NAME: Final[str] = "Secure Password Generator"
APP_VERSION: Final[str] = "1.0.0"
AUTHOR: Final[str] = "Arnav Sharma"
APP_DESCRIPTION: Final[str] = (
    "A production-grade, cryptographically secure password generation desktop "
    "application built with Python, Tkinter, and the secrets module."
)

# Password Length Constraints
MIN_PASSWORD_LENGTH: Final[int] = 8
MAX_PASSWORD_LENGTH: Final[int] = 128
DEFAULT_PASSWORD_LENGTH: Final[int] = 16

# Minimum mandatory categories for generation
MIN_SELECTED_CATEGORIES: Final[int] = 2

# Maximum in-memory session history items
MAX_HISTORY_ENTRIES: Final[int] = 5

# Character Pools
UPPERCASE_CHARS: Final[str] = string.ascii_uppercase
LOWERCASE_CHARS: Final[str] = string.ascii_lowercase
DIGIT_CHARS: Final[str] = string.digits
# Safe punctuation / special characters
SYMBOL_CHARS: Final[str] = "!@#$%^&*()_+-=[]{}|;:,.<>?"

# Ambiguous characters set (frequently confused visually in standard typefaces)
AMBIGUOUS_CHARS: Final[str] = "0Ool1I"

# Character Pool Mapping
CATEGORY_POOLS: Final[Dict[str, str]] = {
    "uppercase": UPPERCASE_CHARS,
    "lowercase": LOWERCASE_CHARS,
    "numbers": DIGIT_CHARS,
    "symbols": SYMBOL_CHARS,
}

CATEGORY_DISPLAY_NAMES: Final[Dict[str, str]] = {
    "uppercase": "Uppercase (A-Z)",
    "lowercase": "Lowercase (a-z)",
    "numbers": "Numbers (0-9)",
    "symbols": "Symbols (!@#$)",
}

# Password Presets
PRESETS: Final[Dict[str, int]] = {
    "Standard": 12,
    "Strong": 16,
    "Maximum": 24,
}

# Entropy & Strength Evaluation Thresholds (Bits)
# Theoretical entropy: Length * log2(Pool Size)
ENTROPY_THRESHOLD_WEAK: Final[float] = 40.0
ENTROPY_THRESHOLD_MEDIUM: Final[float] = 60.0

# Non-sensitive Settings File Name (saved in user home or local app data)
SETTINGS_FILENAME: Final[str] = "secure_password_generator_settings.json"

"""Clipboard integration service using pyperclip with defensive error handling."""

from typing import Tuple

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    pyperclip = None
    PYPERCLIP_AVAILABLE = False


def copy_to_clipboard(text: str) -> Tuple[bool, str]:
    """Copy given text to system clipboard with safety and error handling.

    Args:
        text: Plaintext string to copy.

    Returns:
        Tuple[bool, str]: (Success boolean, Status message).
    """
    if not text:
        return False, "Nothing to copy: password is empty."

    if not PYPERCLIP_AVAILABLE or pyperclip is None:
        return (
            False,
            "Clipboard unavailable: 'pyperclip' package is not installed or accessible.",
        )

    try:
        pyperclip.copy(text)
        return (
            True,
            "Copied to clipboard successfully! (Note: May remain in OS clipboard history until replaced)",
        )
    except Exception as exc:
        return (
            False,
            f"Clipboard error: Failed to access system clipboard ({type(exc).__name__}).",
        )

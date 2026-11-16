"""Root export for clipboard service."""

from services.clipboard_service import copy_to_clipboard, PYPERCLIP_AVAILABLE

__all__ = ["copy_to_clipboard", "PYPERCLIP_AVAILABLE"]

"""Unit tests for clipboard operations with mocked providers."""

from unittest.mock import patch
import pytest
from services.clipboard_service import copy_to_clipboard


class TestClipboardService:
    """Test clipboard service error handling and integration."""

    def test_copy_empty_text_rejected(self):
        success, message = copy_to_clipboard("")
        assert success is False
        assert "empty" in message.lower()

    @patch("pyperclip.copy")
    def test_copy_success_handling(self, mock_copy):
        mock_copy.return_value = None
        success, message = copy_to_clipboard("test_string_123")
        assert success is True
        assert "success" in message.lower()
        mock_copy.assert_called_once_with("test_string_123")

    @patch("pyperclip.copy", side_effect=Exception("System clipboard locked"))
    def test_copy_exception_handling(self, mock_copy):
        success, message = copy_to_clipboard("test_string_123")
        assert success is False
        assert "clipboard error" in message.lower()

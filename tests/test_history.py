"""Unit tests for in-memory session history lifecycle."""

import os
import pytest
from config import MAX_HISTORY_ENTRIES
from modules.history_ui import SessionHistoryFrame
from themes.theme_manager import ThemeManager
import tkinter as tk


class TestSessionHistory:
    """Test in-memory history constraints and lifecycle."""

    @pytest.fixture(scope="class")
    @classmethod
    def tk_root(cls):
        root = tk.Tk()
        root.withdraw()
        yield root
        try:
            root.destroy()
        except Exception:
            pass

    @pytest.fixture
    def history_frame(self, tk_root):
        tm = ThemeManager("dark")
        frame = SessionHistoryFrame(tk_root, tm)
        yield frame

    def test_maximum_five_entries_and_ordering(self, history_frame):
        # Add 7 items
        for i in range(1, 8):
            history_frame.add_entry(f"pw_{i}", "Strong")

        # History must contain exactly 5 entries
        assert len(history_frame._history) == MAX_HISTORY_ENTRIES

        # Newest first: pw_7, pw_6, pw_5, pw_4, pw_3
        passwords = [entry[0] for entry in history_frame._history]
        assert passwords == ["pw_7", "pw_6", "pw_5", "pw_4", "pw_3"]

        # Older entries pw_1 and pw_2 must have been discarded
        assert "pw_1" not in passwords
        assert "pw_2" not in passwords

    def test_clear_history(self, history_frame):
        history_frame.add_entry("test_pw", "Strong")
        assert len(history_frame._history) == 1

        history_frame.clear_history()
        assert len(history_frame._history) == 0

    def test_history_not_persisted_to_disk(self):
        # Ensure no history file exists in the directory
        for f in os.listdir("."):
            assert "history" not in f.lower(), f"Unexpected history file on disk: {f}"

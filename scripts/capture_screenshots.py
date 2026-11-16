"""Capture actual application screenshots of Secure Password Generator."""

import os
import sys
import time
import tkinter as tk
from pathlib import Path
from PIL import ImageGrab

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from main import SecurePasswordGeneratorApp


def capture_app_window(root: tk.Tk, output_path: str):
    root.update_idletasks()
    root.update()
    time.sleep(0.3)
    
    x = root.winfo_rootx()
    y = root.winfo_rooty()
    w = root.winfo_width()
    h = root.winfo_height()
    
    # Grab window bbox
    bbox = (x, y, x + w, y + h)
    img = ImageGrab.grab(bbox=bbox)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    print(f"Saved screenshot: {output_path} ({w}x{h})")


def run_capture():
    screenshots_dir = REPO_ROOT / "assets" / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    root = tk.Tk()
    app = SecurePasswordGeneratorApp(root)
    
    # 1. Dark Mode - Generator
    app.theme_manager.set_theme("dark")
    root.update_idletasks()
    root.update()
    capture_app_window(root, str(screenshots_dir / "dark_mode_generator.png"))
    
    # 2. Dark Mode - Security Details
    app.notebook.select(1)
    root.update_idletasks()
    root.update()
    capture_app_window(root, str(screenshots_dir / "dark_mode_security.png"))
    
    # 3. Dark Mode - Passphrase
    app.notebook.select(3)
    root.update_idletasks()
    root.update()
    capture_app_window(root, str(screenshots_dir / "dark_mode_passphrase.png"))
    
    # 4. Light Mode - Generator (Warm Beige + Burnt Orange)
    app.theme_manager.set_theme("light")
    app.notebook.select(0)
    root.update_idletasks()
    root.update()
    capture_app_window(root, str(screenshots_dir / "light_mode_generator.png"))
    
    # 5. Light Mode - History
    app.notebook.select(2)
    root.update_idletasks()
    root.update()
    capture_app_window(root, str(screenshots_dir / "light_mode_history.png"))
    
    root.destroy()
    print("All screenshots captured successfully!")


if __name__ == "__main__":
    run_capture()

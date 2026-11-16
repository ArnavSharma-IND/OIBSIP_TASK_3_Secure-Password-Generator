"""Dark Mode Color Palette – Near Black + Soft Violet."""

from typing import Dict

DARK_PALETTE: Dict[str, str] = {
    # Core Surfaces
    "main_bg": "#111014",           # Near black main background
    "surface": "#1B1820",           # Elevated dark surface
    "secondary_surface": "#211D27", # Secondary surface / subtle panels
    "borders": "#37303F",           # Subtle deep violet-gray borders
    
    # Text Hierarchy
    "primary_text": "#F2EFF7",      # Off-white primary text
    "secondary_text": "#A69BAF",    # Soft muted lavender-gray
    "muted_text": "#6D6475",        # Faint helper text
    
    # Accents & Interactivity
    "primary_accent": "#A987F5",    # Soft violet primary accent
    "muted_accent": "#8A66D6",      # Deeper violet on hover/active
    "accent_bg": "#292138",         # Faint violet tint for badges / selection
    "accent_text": "#111014",       # Dark text on top of soft violet
    
    # Password Strength Indicators
    "strength_weak": "#EF5350",     # Soft red for weak
    "strength_medium": "#FFB74D",   # Soft amber for medium
    "strength_strong": "#66BB6A",   # Soft emerald for strong
    
    # Monospace Entry & Highlights
    "code_bg": "#15131A",
    "code_fg": "#F2EFF7",
    "badge_bg": "#211D27",
    "badge_fg": "#C5BCD0",
}

"""Light Mode Color Palette – Warm Beige + Burnt Orange."""

from typing import Dict

LIGHT_PALETTE: Dict[str, str] = {
    # Core Surfaces
    "main_bg": "#F3EDE3",           # Warm beige main background
    "surface": "#FAF7F1",           # Elevated surface / inputs / cards
    "secondary_surface": "#E9DFD0", # Secondary surface / subtle panels
    "borders": "#DED5C9",           # Subtle structural dividers and borders
    
    # Text Hierarchy
    "primary_text": "#29251F",      # Dark charcoal primary text
    "secondary_text": "#81776A",    # Muted secondary / metadata text
    "muted_text": "#A39786",        # Faint helper text
    
    # Accents & Interactivity
    "primary_accent": "#C8793C",    # Burnt orange primary accent
    "muted_accent": "#B96C32",      # Deep burnt orange on hover/active
    "accent_bg": "#FCEFE3",         # Faint orange tint for badges / selection
    "accent_text": "#FFFFFF",       # Text on top of primary accent
    
    # Password Strength Indicators
    "strength_weak": "#D32F2F",     # Deep red for weak
    "strength_medium": "#D9822B",   # Amber / dark orange for medium
    "strength_strong": "#2E7D32",   # Forest green for strong
    
    # Monospace Entry & Highlights
    "code_bg": "#FFFFFF",
    "code_fg": "#29251F",
    "badge_bg": "#E9DFD0",
    "badge_fg": "#5E5448",
}

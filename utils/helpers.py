"""Helper functions for display formatting and date/time handling."""

from datetime import datetime


def mask_password(password: str, mask_char: str = "•") -> str:
    """Mask a password string for secure visual presentation.

    Args:
        password: Raw password.
        mask_char: The bullet/mask character (default '•').

    Returns:
        str: Masked string of the same length as the password.
    """
    return mask_char * len(password)


def format_entropy(bits: float) -> str:
    """Format entropy bits into a clean string representation.

    Args:
        bits: Theoretical entropy value in bits.

    Returns:
        str: Formatted string e.g. "65.4 bits".
    """
    return f"{bits:.1f} bits"


def get_current_timestamp() -> str:
    """Get the current time formatted for session history logs.

    Returns:
        str: Time formatted as 'HH:MM:SS'.
    """
    return datetime.now().strftime("%H:%M:%S")

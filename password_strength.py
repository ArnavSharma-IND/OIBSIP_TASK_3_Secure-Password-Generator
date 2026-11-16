"""Password strength and theoretical entropy calculation module.

Evaluates password complexity and estimated Shannon entropy using character pool
diversity, length, and logarithmic calculations.
"""

import math
import string
from dataclasses import dataclass
from typing import Dict, Optional, Set
from config import (
    CATEGORY_POOLS,
    AMBIGUOUS_CHARS,
    ENTROPY_THRESHOLD_WEAK,
    ENTROPY_THRESHOLD_MEDIUM,
)


@dataclass
class StrengthReport:
    """Structured report detailing password strength and entropy metrics."""
    label: str                  # "Weak", "Medium", "Strong"
    entropy_bits: float         # Theoretical entropy in bits
    pool_size: int              # Estimated character pool size
    length: int                 # Password length
    percent: float              # Percentage representation (0.0 to 100.0)
    category_summary: str       # E.g., "Uppercase, Lowercase, Numbers"
    description: str            # Detailed human-readable explanation
    crack_time_estimate: str    # Educational offline crack time estimate


def calculate_pool_size(
    uppercase: bool,
    lowercase: bool,
    numbers: bool,
    symbols: bool,
    exclude_ambiguous: bool = False,
) -> int:
    """Calculate the total distinct available character pool size.

    Args:
        uppercase: Whether uppercase characters are included.
        lowercase: Whether lowercase characters are included.
        numbers: Whether digits are included.
        symbols: Whether symbols are included.
        exclude_ambiguous: Whether ambiguous characters (0, O, o, l, 1, I) are excluded.

    Returns:
        int: Number of available unique characters in the combined pool.
    """
    total_chars = set()
    ambiguous_set = set(AMBIGUOUS_CHARS) if exclude_ambiguous else set()

    if uppercase:
        total_chars.update(set(CATEGORY_POOLS["uppercase"]) - ambiguous_set)
    if lowercase:
        total_chars.update(set(CATEGORY_POOLS["lowercase"]) - ambiguous_set)
    if numbers:
        total_chars.update(set(CATEGORY_POOLS["numbers"]) - ambiguous_set)
    if symbols:
        total_chars.update(set(CATEGORY_POOLS["symbols"]) - ambiguous_set)

    return len(total_chars)


def calculate_theoretical_entropy(length: int, pool_size: int) -> float:
    """Calculate theoretical information entropy in bits: E = L * log2(R).

    Args:
        length: Password length.
        pool_size: Size of the character pool.

    Returns:
        float: Theoretical entropy in bits (rounded to 1 decimal place).
    """
    if length <= 0 or pool_size <= 1:
        return 0.0
    return round(length * math.log2(pool_size), 1)


def estimate_crack_time(entropy_bits: float) -> str:
    """Provide a realistic educational estimate of offline brute-force time.

    Assumes a high-end offline GPU cracking cluster testing 100 billion
    (10^11) guesses per second.

    Args:
        entropy_bits: Theoretical entropy in bits.

    Returns:
        str: Human-readable duration.
    """
    if entropy_bits <= 0:
        return "Instant"

    combinations = 2 ** entropy_bits
    guesses_per_sec = 100_000_000_000  # 100 billion guesses/sec
    seconds = combinations / (2 * guesses_per_sec)  # Average time to crack

    if seconds < 1:
        return "Less than a second"
    elif seconds < 60:
        return f"~{int(seconds)} seconds"
    elif seconds < 3600:
        return f"~{int(seconds / 60)} minutes"
    elif seconds < 86400:
        return f"~{int(seconds / 3600)} hours"
    elif seconds < 86400 * 365:
        return f"~{int(seconds / 86400)} days"
    elif seconds < 86400 * 365 * 1000:
        return f"~{int(seconds / (86400 * 365)):,} years"
    elif seconds < 86400 * 365 * 1_000_000:
        return f"~{int(seconds / (86400 * 365 * 1000)):,} thousand years"
    else:
        return "Centuries (virtually uncrackable by brute-force)"


def evaluate_password_strength(
    length: int,
    uppercase: bool = True,
    lowercase: bool = True,
    numbers: bool = True,
    symbols: bool = True,
    exclude_ambiguous: bool = False,
    password_text: Optional[str] = None,
) -> StrengthReport:
    """Evaluate password strength and generate a comprehensive diagnostic report.

    Args:
        length: Password length.
        uppercase: Whether uppercase pool is enabled.
        lowercase: Whether lowercase pool is enabled.
        numbers: Whether numbers pool is enabled.
        symbols: Whether symbols pool is enabled.
        exclude_ambiguous: Whether ambiguous characters are excluded.
        password_text: Optional actual password string for fine-grained empirical evaluation.

    Returns:
        StrengthReport: Complete metrics and feedback.
    """
    # If explicit password text is provided, determine empirical categories present
    if password_text is not None and len(password_text) > 0:
        length = len(password_text)
        has_upper = any(c in string.ascii_uppercase for c in password_text)
        has_lower = any(c in string.ascii_lowercase for c in password_text)
        has_digit = any(c in string.digits for c in password_text)
        has_symbol = any(c in CATEGORY_POOLS["symbols"] for c in password_text)
        pool_size = calculate_pool_size(
            has_upper, has_lower, has_digit, has_symbol, exclude_ambiguous=False
        )
        active_names = []
        if has_upper:
            active_names.append("Uppercase")
        if has_lower:
            active_names.append("Lowercase")
        if has_digit:
            active_names.append("Numbers")
        if has_symbol:
            active_names.append("Symbols")
    else:
        pool_size = calculate_pool_size(
            uppercase, lowercase, numbers, symbols, exclude_ambiguous
        )
        active_names = []
        if uppercase:
            active_names.append("Uppercase")
        if lowercase:
            active_names.append("Lowercase")
        if numbers:
            active_names.append("Numbers")
        if symbols:
            active_names.append("Symbols")

    entropy = calculate_theoretical_entropy(length, pool_size)

    # Classify strength according to standardized thresholds
    if entropy < ENTROPY_THRESHOLD_WEAK:
        label = "Weak"
        # 0 to 40 bits maps to 0 to 33%
        percent = min(33.0, max(5.0, (entropy / ENTROPY_THRESHOLD_WEAK) * 33.0))
        description = (
            f"Insufficient entropy ({entropy} bits). Vulnerable to modern automated "
            f"dictionary and brute-force attacks. Recommended length: 16+ characters with multiple character sets."
        )
    elif entropy < ENTROPY_THRESHOLD_MEDIUM:
        label = "Medium"
        # 40 to 60 bits maps to 34% to 66%
        progress = (entropy - ENTROPY_THRESHOLD_WEAK) / (ENTROPY_THRESHOLD_MEDIUM - ENTROPY_THRESHOLD_WEAK)
        percent = 34.0 + (progress * 32.0)
        description = (
            f"Moderate entropy ({entropy} bits). Suitable for non-critical accounts. "
            f"Consider increasing length or adding symbols to achieve 60+ bits."
        )
    else:
        label = "Strong"
        # 60 to 100+ bits maps to 67% to 100%
        progress = min(1.0, (entropy - ENTROPY_THRESHOLD_MEDIUM) / 40.0)
        percent = 67.0 + (progress * 33.0)
        description = (
            f"High entropy ({entropy} bits). Outstanding cryptographic resistance against "
            f"distributed offline brute-force attacks."
        )

    crack_time = estimate_crack_time(entropy)
    category_summary = ", ".join(active_names) if active_names else "None"

    return StrengthReport(
        label=label,
        entropy_bits=entropy,
        pool_size=pool_size,
        length=length,
        percent=round(percent, 1),
        category_summary=category_summary,
        description=description,
        crack_time_estimate=crack_time,
    )

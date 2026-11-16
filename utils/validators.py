"""Input validation utilities for Secure Password Generator."""

from typing import Any, Dict, List, Set, Union
from config import (
    MIN_PASSWORD_LENGTH,
    MAX_PASSWORD_LENGTH,
    MIN_SELECTED_CATEGORIES,
    CATEGORY_POOLS,
)


class ValidationError(ValueError):
    """Custom exception raised when user inputs fail validation rules."""
    pass


def validate_password_length(
    length_input: Any,
    min_length: int = MIN_PASSWORD_LENGTH,
    max_length: int = MAX_PASSWORD_LENGTH,
) -> int:
    """Validate requested password length.

    Args:
        length_input: Input value to validate (can be int, str, etc.).
        min_length: Minimum allowed length (default 8).
        max_length: Maximum allowed length (default 128).

    Returns:
        int: Validated integer password length.

    Raises:
        ValidationError: If length is empty, non-integer, negative, zero, or out of bounds.
    """
    if length_input is None:
        raise ValidationError("Password length cannot be empty.")

    if isinstance(length_input, str):
        cleaned = length_input.strip()
        if not cleaned:
            raise ValidationError("Password length cannot be empty.")
        if not (cleaned.isdigit() or (cleaned.startswith("-") and cleaned[1:].isdigit())):
            raise ValidationError(
                f"Password length must be a valid whole number (received '{length_input}')."
            )
        try:
            val = int(cleaned)
        except ValueError as exc:
            raise ValidationError(
                f"Password length must be a valid whole number (received '{length_input}')."
            ) from exc
    elif isinstance(length_input, bool):
        # In Python, bool is a subclass of int, so True == 1. Reject bool explicitly.
        raise ValidationError("Password length must be an integer, not a boolean.")
    elif isinstance(length_input, (int, float)):
        if isinstance(length_input, float) and not length_input.is_integer():
            raise ValidationError(
                f"Password length must be a whole integer without decimals (received {length_input})."
            )
        val = int(length_input)
    else:
        raise ValidationError(
            f"Password length must be an integer (received {type(length_input).__name__})."
        )

    if val <= 0:
        raise ValidationError(
            f"Password length must be a positive number greater than 0 (received {val})."
        )

    if val < min_length:
        raise ValidationError(
            f"Password length must be at least {min_length} characters for security (received {val})."
        )

    if val > max_length:
        raise ValidationError(
            f"Password length cannot exceed {max_length} characters (received {val})."
        )

    return val


def validate_category_selection(
    selected_categories: Union[Dict[str, bool], List[str], Set[str]],
    min_required: int = MIN_SELECTED_CATEGORIES,
) -> List[str]:
    """Validate that at least the minimum required number of categories are selected.

    Args:
        selected_categories: Mapping of category names to booleans, or a collection of active names.
        min_required: Minimum categories required (default 2).

    Returns:
        List[str]: List of active category keys.

    Raises:
        ValidationError: If fewer than `min_required` categories are selected or if unknown categories are provided.
    """
    if isinstance(selected_categories, dict):
        active = [cat for cat, enabled in selected_categories.items() if enabled]
    elif isinstance(selected_categories, (list, set, tuple)):
        active = list(selected_categories)
    else:
        raise ValidationError("Invalid category format provided.")

    valid_keys = set(CATEGORY_POOLS.keys())
    for cat in active:
        if cat not in valid_keys:
            raise ValidationError(f"Unknown character category: '{cat}'.")

    if len(active) < min_required:
        raise ValidationError(
            f"At least {min_required} character categories must be selected (currently {len(active)} selected). "
            "Please select Uppercase, Lowercase, Numbers, or Symbols."
        )

    return active


def validate_character_pools(
    pools: Dict[str, str],
    password_length: int,
) -> None:
    """Validate character pools for non-emptiness and length sufficiency.

    Args:
        pools: Mapping of active category names to their available characters.
        password_length: The requested password length.

    Raises:
        ValidationError: If any selected pool is empty or length is insufficient.
    """
    for name, chars in pools.items():
        if not chars:
            raise ValidationError(
                f"Character category '{name}' contains no available characters after exclusions. "
                "Please adjust ambiguous character settings or reselect categories."
            )

    required_chars_count = len(pools)
    if password_length < required_chars_count:
        raise ValidationError(
            f"Requested password length ({password_length}) is shorter than the number of mandatory "
            f"selected categories ({required_chars_count}). Increase length to at least {required_chars_count}."
        )

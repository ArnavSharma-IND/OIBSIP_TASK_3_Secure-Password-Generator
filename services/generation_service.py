"""Cryptographically secure password and passphrase generation service.

Utilizes Python's standard `secrets` module exclusively for cryptographically
strong pseudo-random number generation suitable for managing data such as
passwords, account authentication, and security tokens.
"""

import secrets
from typing import Dict, List, Optional, Set, Union
from config import (
    CATEGORY_POOLS,
    AMBIGUOUS_CHARS,
    MIN_PASSWORD_LENGTH,
    MAX_PASSWORD_LENGTH,
    MIN_SELECTED_CATEGORIES,
)
from utils.validators import (
    ValidationError,
    validate_password_length,
    validate_category_selection,
    validate_character_pools,
)
from utils.wordlist import EFF_WORDLIST


def build_filtered_pool(chars: str, exclude_ambiguous: bool) -> str:
    """Filter out ambiguous characters from a given character string if requested.

    Args:
        chars: Raw pool string.
        exclude_ambiguous: Whether to exclude confusing characters (0, O, o, l, 1, I).

    Returns:
        str: Filtered character string.
    """
    if not exclude_ambiguous:
        return chars
    ambiguous_set = set(AMBIGUOUS_CHARS)
    return "".join(c for c in chars if c not in ambiguous_set)


def secure_shuffle(items: List[str]) -> None:
    """In-place Fisher-Yates shuffle powered exclusively by `secrets.randbelow`.

    Guarantees unbiased, cryptographically secure shuffling without relying
    on the standard `random` module.

    Args:
        items: List of characters/items to shuffle in place.
    """
    n = len(items)
    for i in range(n - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        items[i], items[j] = items[j], items[i]


def generate_secure_password(
    length: Union[int, str] = 16,
    uppercase: bool = True,
    lowercase: bool = True,
    numbers: bool = True,
    symbols: bool = True,
    exclude_ambiguous: bool = False,
) -> str:
    """Generate a cryptographically secure password conforming to strict criteria.

    Guarantees:
    - At least one character from each selected category is included.
    - Exactly the requested password length.
    - No characters from unselected categories are present.
    - Uses `secrets` exclusively for selection and shuffling.
    - Rejects fewer than two selected categories or invalid lengths.

    Args:
        length: Desired length (min 8).
        uppercase: Include A-Z.
        lowercase: Include a-z.
        numbers: Include 0-9.
        symbols: Include punctuation/symbols.
        exclude_ambiguous: Exclude confusing characters (0, O, o, l, 1, I).

    Returns:
        str: The generated password.

    Raises:
        ValidationError: If length, category count, or pool constraints are violated.
    """
    # 1. Validate password length
    validated_length = validate_password_length(
        length,
        min_length=MIN_PASSWORD_LENGTH,
        max_length=MAX_PASSWORD_LENGTH,
    )

    # 2. Validate category selections (minimum 2 required)
    selected_dict = {
        "uppercase": uppercase,
        "lowercase": lowercase,
        "numbers": numbers,
        "symbols": symbols,
    }
    active_categories = validate_category_selection(selected_dict, min_required=MIN_SELECTED_CATEGORIES)

    # 3. Build filtered pools for active categories
    active_pools: Dict[str, str] = {}
    for cat in active_categories:
        base_pool = CATEGORY_POOLS[cat]
        filtered = build_filtered_pool(base_pool, exclude_ambiguous)
        active_pools[cat] = filtered

    # 4. Validate that pools are non-empty and length is sufficient
    validate_character_pools(active_pools, validated_length)

    # 5. Guarantee at least one character from every active pool
    password_chars: List[str] = []
    for cat in active_categories:
        chosen_char = secrets.choice(active_pools[cat])
        password_chars.append(chosen_char)

    # 6. Build combined master pool for remaining positions
    combined_pool = "".join(active_pools.values())
    if not combined_pool:
        raise ValidationError("Combined character pool is empty.")

    # 7. Fill remaining positions with cryptographically random choices
    remaining_count = validated_length - len(password_chars)
    for _ in range(remaining_count):
        password_chars.append(secrets.choice(combined_pool))

    # 8. Cryptographically secure shuffle using Fisher-Yates + secrets.randbelow
    secure_shuffle(password_chars)

    final_password = "".join(password_chars)

    # 9. Integrity Verification
    if len(final_password) != validated_length:
        raise RuntimeError("Generated password length does not match requested length.")

    # Verify every active pool is represented
    for cat in active_categories:
        pool_chars = set(active_pools[cat])
        if not any(c in pool_chars for c in final_password):
            # Extremely improbable fallback in case of shuffle anomaly
            # Recursively re-generate to enforce guarantee
            return generate_secure_password(
                length=validated_length,
                uppercase=uppercase,
                lowercase=lowercase,
                numbers=numbers,
                symbols=symbols,
                exclude_ambiguous=exclude_ambiguous,
            )

    # Verify no unselected category characters are present
    all_allowed_chars = set(combined_pool)
    for c in final_password:
        if c not in all_allowed_chars:
            raise RuntimeError(f"Disallowed character detected in generated password: '{c}'")

    return final_password


def generate_secure_passphrase(
    word_count: int = 4,
    separator: str = "-",
    capitalize: bool = True,
    include_number: bool = True,
) -> str:
    """Generate a high-entropy, memorable passphrase using secure random word selection.

    Args:
        word_count: Number of words in the passphrase (min 3, max 10).
        separator: Character used to separate words (e.g. '-', '.', ' ', '_').
        capitalize: Whether each word is title-cased.
        include_number: Append a random two-digit number for extra entropy.

    Returns:
        str: Generated secure passphrase.

    Raises:
        ValidationError: If word count is less than 3.
    """
    if word_count < 3 or word_count > 10:
        raise ValidationError("Passphrase word count must be between 3 and 10 words.")

    chosen_words: List[str] = [secrets.choice(EFF_WORDLIST) for _ in range(word_count)]

    if capitalize:
        chosen_words = [w.capitalize() for w in chosen_words]

    passphrase = separator.join(chosen_words)

    if include_number:
        # Generate 2-digit number (10 to 99)
        num = 10 + secrets.randbelow(90)
        passphrase = f"{passphrase}{separator}{num}"

    return passphrase

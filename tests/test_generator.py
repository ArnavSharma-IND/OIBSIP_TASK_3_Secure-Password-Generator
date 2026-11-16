"""Comprehensive unit tests for cryptographically secure password generation."""

import string
import pytest
from password_generator import (
    generate_secure_password,
    build_filtered_pool,
    secure_shuffle,
)
from utils.validators import ValidationError
from config import AMBIGUOUS_CHARS, SYMBOL_CHARS


class TestPasswordGenerator:
    """Test suite for password generation engine."""

    def test_minimum_length_generation(self):
        pw = generate_secure_password(length=8)
        assert len(pw) == 8

    @pytest.mark.parametrize("length", [8, 12, 16, 20, 24, 32, 64, 100])
    def test_exact_requested_length(self, length):
        pw = generate_secure_password(length=length)
        assert len(pw) == length

    def test_all_categories_represented_guarantee(self):
        """Run 100 iterations to verify that EVERY selected category is always present."""
        for _ in range(100):
            pw = generate_secure_password(
                length=8,  # minimal length to test tight guarantee
                uppercase=True,
                lowercase=True,
                numbers=True,
                symbols=True,
            )
            has_upper = any(c in string.ascii_uppercase for c in pw)
            has_lower = any(c in string.ascii_lowercase for c in pw)
            has_digit = any(c in string.digits for c in pw)
            has_symbol = any(c in SYMBOL_CHARS for c in pw)

            assert has_upper, f"Uppercase missing in: {pw}"
            assert has_lower, f"Lowercase missing in: {pw}"
            assert has_digit, f"Number missing in: {pw}"
            assert has_symbol, f"Symbol missing in: {pw}"

    def test_unselected_categories_strictly_excluded(self):
        """When symbols and numbers are omitted, only letters should appear."""
        for _ in range(50):
            pw = generate_secure_password(
                length=16,
                uppercase=True,
                lowercase=True,
                numbers=False,
                symbols=False,
            )
            assert not any(c in string.digits for c in pw), "Digit found in letters-only password"
            assert not any(c in SYMBOL_CHARS for c in pw), "Symbol found in letters-only password"
            assert all(c in string.ascii_letters for c in pw)

    def test_ambiguous_character_exclusion(self):
        """Verify that ambiguous characters (0, O, o, l, 1, I) never appear when excluded."""
        ambiguous_set = set(AMBIGUOUS_CHARS)
        for _ in range(100):
            pw = generate_secure_password(
                length=32,
                uppercase=True,
                lowercase=True,
                numbers=True,
                symbols=True,
                exclude_ambiguous=True,
            )
            for ambig in ambiguous_set:
                assert ambig not in pw, f"Ambiguous character '{ambig}' found in password '{pw}'"

    def test_fewer_than_two_categories_raises_error(self):
        with pytest.raises(ValidationError, match="At least 2 character categories must be selected"):
            generate_secure_password(
                length=16,
                uppercase=True,
                lowercase=False,
                numbers=False,
                symbols=False,
            )

    def test_invalid_length_raises_error(self):
        with pytest.raises(ValidationError, match="at least 8 characters"):
            generate_secure_password(length=5)

        with pytest.raises(ValidationError, match="cannot be empty"):
            generate_secure_password(length="")

    def test_length_less_than_mandatory_categories_raises_error(self):
        # 4 categories selected with custom min_length passed to pool validation
        # By default length < 8 is caught, but if length < categories:
        with pytest.raises(ValidationError):
            generate_secure_password(length=3)

    def test_filtered_pool_builder(self):
        raw = "012345OolIabc"
        filtered = build_filtered_pool(raw, exclude_ambiguous=True)
        for ambig in AMBIGUOUS_CHARS:
            assert ambig not in filtered
        assert "2" in filtered
        assert "a" in filtered

    def test_secure_shuffle_integrity(self):
        original = list("ABCDEF123456!@#$")
        copied = list(original)
        secure_shuffle(copied)
        assert len(copied) == len(original)
        assert sorted(copied) == sorted(original)

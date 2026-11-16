"""Unit tests for input validation logic."""

import pytest
from utils.validators import (
    ValidationError,
    validate_password_length,
    validate_category_selection,
    validate_character_pools,
)
from config import MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH


class TestLengthValidation:
    """Test password length validation rules."""

    def test_valid_integer_lengths(self):
        assert validate_password_length(8) == 8
        assert validate_password_length(16) == 16
        assert validate_password_length(64) == 64
        assert validate_password_length(128) == 128

    def test_valid_string_lengths(self):
        assert validate_password_length("8") == 8
        assert validate_password_length(" 24 ") == 24
        assert validate_password_length("64") == 64

    def test_below_minimum_length_rejected(self):
        with pytest.raises(ValidationError, match="at least 8 characters"):
            validate_password_length(7)

        with pytest.raises(ValidationError, match="at least 8 characters"):
            validate_password_length("4")

    def test_above_maximum_length_rejected(self):
        with pytest.raises(ValidationError, match="cannot exceed 128"):
            validate_password_length(129)

    def test_zero_and_negative_rejected(self):
        with pytest.raises(ValidationError, match="positive number greater than 0"):
            validate_password_length(0)

        with pytest.raises(ValidationError, match="positive number greater than 0"):
            validate_password_length(-5)

        with pytest.raises(ValidationError, match="positive number greater than 0"):
            validate_password_length("-10")

    def test_empty_input_rejected(self):
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_password_length(None)

        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_password_length("")

        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_password_length("   ")

    def test_non_integer_strings_rejected(self):
        with pytest.raises(ValidationError, match="must be a valid whole number"):
            validate_password_length("abc")

        with pytest.raises(ValidationError, match="must be a valid whole number"):
            validate_password_length("16.5")

    def test_boolean_type_rejected(self):
        with pytest.raises(ValidationError, match="not a boolean"):
            validate_password_length(True)

        with pytest.raises(ValidationError, match="not a boolean"):
            validate_password_length(False)

    def test_float_type_handling(self):
        # Whole floats are accepted as int
        assert validate_password_length(16.0) == 16

        # Decimal floats are rejected
        with pytest.raises(ValidationError, match="must be a whole integer"):
            validate_password_length(16.5)


class TestCategoryValidation:
    """Test character category selection rules."""

    def test_valid_selection_dict(self):
        active = validate_category_selection({
            "uppercase": True,
            "lowercase": True,
            "numbers": False,
            "symbols": False,
        })
        assert set(active) == {"uppercase", "lowercase"}

    def test_all_categories_selected(self):
        active = validate_category_selection({
            "uppercase": True,
            "lowercase": True,
            "numbers": True,
            "symbols": True,
        })
        assert len(active) == 4

    def test_fewer_than_two_categories_rejected(self):
        with pytest.raises(ValidationError, match="At least 2 character categories must be selected"):
            validate_category_selection({
                "uppercase": True,
                "lowercase": False,
                "numbers": False,
                "symbols": False,
            })

        with pytest.raises(ValidationError, match="At least 2 character categories must be selected"):
            validate_category_selection({
                "uppercase": False,
                "lowercase": False,
                "numbers": False,
                "symbols": False,
            })

    def test_unknown_category_rejected(self):
        with pytest.raises(ValidationError, match="Unknown character category"):
            validate_category_selection(["uppercase", "unknown_category"])


class TestPoolValidation:
    """Test pool sufficiency checks."""

    def test_empty_pool_rejected(self):
        with pytest.raises(ValidationError, match="contains no available characters"):
            validate_character_pools({"uppercase": "ABC", "lowercase": ""}, password_length=12)

    def test_insufficient_length_for_mandatory_categories(self):
        # 4 categories required, but length is 3
        with pytest.raises(ValidationError, match="shorter than the number of mandatory"):
            validate_character_pools(
                {"uppercase": "ABC", "lowercase": "abc", "numbers": "123", "symbols": "!@#"},
                password_length=3,
            )

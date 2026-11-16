"""Unit tests for secure passphrase generation."""

import pytest
from services.generation_service import generate_secure_passphrase
from utils.validators import ValidationError
from utils.wordlist import EFF_WORDLIST


class TestPassphraseGenerator:
    """Test suite for passphrase generation service."""

    def test_default_passphrase_generation(self):
        phrase = generate_secure_passphrase(
            word_count=4,
            separator="-",
            capitalize=True,
            include_number=True,
        )
        parts = phrase.split("-")
        # 4 words + 1 number = 5 tokens
        assert len(parts) == 5
        # Words must be capitalized
        for w in parts[:4]:
            assert w[0].isupper()
            assert w.lower() in EFF_WORDLIST
        # Number must be 2-digit integer
        assert parts[4].isdigit()
        assert 10 <= int(parts[4]) <= 99

    def test_custom_separators(self):
        phrase_dot = generate_secure_passphrase(word_count=3, separator=".", include_number=False)
        assert len(phrase_dot.split(".")) == 3

        phrase_space = generate_secure_passphrase(word_count=3, separator=" ", include_number=False)
        assert len(phrase_space.split(" ")) == 3

    def test_uncapitalized_passphrase(self):
        phrase = generate_secure_passphrase(word_count=3, capitalize=False, include_number=False)
        for w in phrase.split("-"):
            assert w.islower()

    def test_invalid_word_count_rejected(self):
        with pytest.raises(ValidationError, match="between 3 and 10 words"):
            generate_secure_passphrase(word_count=2)

        with pytest.raises(ValidationError, match="between 3 and 10 words"):
            generate_secure_passphrase(word_count=11)

"""Unit tests for password strength evaluation and theoretical entropy calculation."""

import pytest
from password_strength import (
    calculate_pool_size,
    calculate_theoretical_entropy,
    evaluate_password_strength,
    estimate_crack_time,
)
from config import (
    ENTROPY_THRESHOLD_WEAK,
    ENTROPY_THRESHOLD_MEDIUM,
)


class TestEntropyCalculations:
    """Test mathematical entropy calculations."""

    def test_theoretical_entropy_formula(self):
        # 16 characters from 94 pool: 16 * log2(94) = 16 * ~6.554588 = ~104.9 bits
        entropy = calculate_theoretical_entropy(16, 94)
        assert 104.0 <= entropy <= 106.0

    def test_zero_length_or_single_char_pool(self):
        assert calculate_theoretical_entropy(0, 94) == 0.0
        assert calculate_theoretical_entropy(16, 1) == 0.0
        assert calculate_theoretical_entropy(-5, 50) == 0.0

    def test_pool_size_calculation_standard(self):
        # Upper (26) + Lower (26) + Digits (10) + Symbols (26) = 88
        pool = calculate_pool_size(
            uppercase=True,
            lowercase=True,
            numbers=True,
            symbols=True,
            exclude_ambiguous=False,
        )
        assert pool > 80

    def test_pool_size_with_ambiguous_exclusion(self):
        pool_standard = calculate_pool_size(True, True, True, True, exclude_ambiguous=False)
        pool_excluded = calculate_pool_size(True, True, True, True, exclude_ambiguous=True)
        # Should exclude 6 characters: '0', 'O', 'o', 'l', '1', 'I'
        assert pool_standard - pool_excluded == 6


class TestStrengthClassification:
    """Test classification thresholds (Weak, Medium, Strong)."""

    def test_weak_classification(self):
        # Length 8, letters only: 8 * log2(26) ≈ 37.6 bits (< 40)
        report = evaluate_password_strength(
            length=8,
            uppercase=False,
            lowercase=True,
            numbers=False,
            symbols=False,
        )
        assert report.label == "Weak"
        assert report.entropy_bits < ENTROPY_THRESHOLD_WEAK

    def test_medium_classification(self):
        # Length 10, letters + numbers: 10 * log2(62) ≈ 59.5 bits (40 <= E < 60)
        report = evaluate_password_strength(
            length=10,
            uppercase=True,
            lowercase=True,
            numbers=True,
            symbols=False,
        )
        assert report.label == "Medium"
        assert ENTROPY_THRESHOLD_WEAK <= report.entropy_bits < ENTROPY_THRESHOLD_MEDIUM

    def test_strong_classification(self):
        # Length 16, all pools: 16 * log2(88) ≈ 103 bits (>= 60)
        report = evaluate_password_strength(
            length=16,
            uppercase=True,
            lowercase=True,
            numbers=True,
            symbols=True,
        )
        assert report.label == "Strong"
        assert report.entropy_bits >= ENTROPY_THRESHOLD_MEDIUM

    def test_empirical_password_text_evaluation(self):
        # Weak password string
        weak_report = evaluate_password_strength(length=6, password_text="abc123")
        assert weak_report.label == "Weak"

        # Strong password string
        strong_report = evaluate_password_strength(
            length=16,
            password_text="Kx9#mQ2$pL7!vW4@",
        )
        assert strong_report.label == "Strong"


class TestCrackTimeEstimates:
    """Test educational crack time outputs."""

    def test_instant_for_low_entropy(self):
        time_str = estimate_crack_time(10.0)
        assert "second" in time_str.lower()

    def test_high_entropy_estimate(self):
        time_str = estimate_crack_time(100.0)
        assert "centuries" in time_str.lower() or "year" in time_str.lower()

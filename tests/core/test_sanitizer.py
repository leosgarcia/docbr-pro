"""Tests for the sanitizer module."""

from docbr_pro.core.sanitizer import sanitize_cnpj, sanitize_cpf


def test_sanitize_cpf_numeric_padding() -> None:
    """Test if a CPF missing leading zeros is padded correctly."""
    # Excel might turn "00123456789" into 123456789
    assert sanitize_cpf(123456789) == "00123456789"
    assert sanitize_cpf("123456789") == "00123456789"


def test_sanitize_cpf_punctuation() -> None:
    """Test if punctuation is properly removed from CPF."""
    assert sanitize_cpf("123.456.789-01") == "12345678901"
    assert sanitize_cpf(" 123.456.789-01  ") == "12345678901"


def test_sanitize_cpf_fuzzy_fixing() -> None:
    """Test if common typos like 'O' are replaced by '0'."""
    assert sanitize_cpf("123.456.789-Oo") == "12345678900"


def test_sanitize_cnpj_numeric_padding() -> None:
    """Test if a CNPJ missing leading zeros is padded correctly."""
    assert sanitize_cnpj(123) == "00000000000123"
    assert sanitize_cnpj("123") == "00000000000123"


def test_sanitize_cnpj_punctuation() -> None:
    """Test if punctuation is properly removed from CNPJ."""
    assert sanitize_cnpj("06.990.590/0001-23") == "06990590000123"


def test_sanitize_cnpj_alphanumeric() -> None:
    """Test if alphanumeric CNPJs are handled correctly (uppercased and preserved)."""
    # Lowercase should become uppercase
    assert sanitize_cnpj("12abcdeF345678") == "12ABCDEF345678"

    # Missing leading zeros on alphanumeric
    assert sanitize_cnpj("A23") == "00000000000A23"

"""Tests for the CPF module."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from docbr_pro.core.cpf import CPF, _calculate_dv
from docbr_pro.core.exceptions import InvalidDigitError, InvalidFormatError


def generate_valid_cpf_digits() -> list[int]:
    """Helper to generate a valid CPF for testing purposes."""
    # A known valid CPF: 529.982.247-25
    return [5, 2, 9, 9, 8, 2, 2, 4, 7, 2, 5]


def test_cpf_valid_document() -> None:
    """Test a known valid CPF."""
    cpf_obj = CPF("52998224725")
    assert cpf_obj.clean == "52998224725"
    assert cpf_obj.formatted == "529.982.247-25"
    assert cpf_obj.fiscal_region == "ES e RJ"


def test_cpf_invalid_length() -> None:
    """Test CPF with invalid length."""
    with pytest.raises(InvalidFormatError, match="Quantidade de dígitos incorreta"):
        CPF("123")

    with pytest.raises(InvalidFormatError, match="Quantidade de dígitos incorreta"):
        CPF("123456789012")


def test_cpf_repeated_digits() -> None:
    """Test CPF with all repeated digits."""
    with pytest.raises(InvalidFormatError, match="Documento contém apenas dígitos repetidos"):
        CPF("111.111.111-11")


def test_cpf_invalid_first_digit() -> None:
    """Test CPF with invalid first verification digit."""
    # valid is 529982247-25
    with pytest.raises(InvalidDigitError, match="Dígito verificador inválido."):
        CPF("52998224735")


def test_cpf_invalid_second_digit() -> None:
    """Test CPF with invalid second verification digit."""
    # valid is 529982247-25
    with pytest.raises(InvalidDigitError, match="Dígito verificador inválido."):
        CPF("52998224726")


@given(st.lists(st.integers(min_value=0, max_value=9), min_size=9, max_size=9))
def test_hypothesis_cpf_generation_roundtrip(base_digits: list[int]) -> None:
    """
    Test that calculating the DVs for any 9 random digits results in a CPF
    that is accepted by our own validation logic.
    """
    # Skip if all digits are the same
    if len(set(base_digits)) == 1:
        return

    dv1 = _calculate_dv(base_digits)
    dv2 = _calculate_dv(base_digits + [dv1])

    full_digits = base_digits + [dv1, dv2]
    cpf_str = "".join(str(d) for d in full_digits)

    # Should not raise any exception
    cpf_obj = CPF(cpf_str)
    assert cpf_obj.clean == cpf_str

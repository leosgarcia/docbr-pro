"""Tests for the CNPJ module."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from docbr_pro.core.cnpj import CNPJ, _calculate_dv
from docbr_pro.core.exceptions import InvalidDigitError, InvalidFormatError


def test_cnpj_valid_numeric() -> None:
    """Test a known valid numeric CNPJ."""
    # Google Brasil CNPJ
    cnpj_obj = CNPJ("06.990.590/0001-23")
    assert cnpj_obj.clean == "06990590000123"
    assert cnpj_obj.formatted == "06.990.590/0001-23"


def test_cnpj_valid_alphanumeric_manual() -> None:
    """Test a manually crafted alphanumeric CNPJ."""
    # Let's generate a valid one dynamically to test basic validation without Hypothesis
    base = "12ABCDEF3456"
    dv1 = _calculate_dv(base, CNPJ._WEIGHTS_DV1)
    dv2 = _calculate_dv(base + str(dv1), CNPJ._WEIGHTS_DV2)
    doc = f"{base}{dv1}{dv2}"

    cnpj_obj = CNPJ(doc)
    assert cnpj_obj.clean == doc


def test_cnpj_invalid_length() -> None:
    """Test CNPJ with invalid length."""
    with pytest.raises(InvalidFormatError, match="Quantidade de caracteres incorreta"):
        CNPJ("123")

    with pytest.raises(InvalidFormatError, match="Quantidade de caracteres incorreta"):
        CNPJ("123456789012345")


def test_cnpj_repeated_chars() -> None:
    """Test CNPJ with all repeated characters."""
    with pytest.raises(InvalidFormatError, match="Documento contém apenas caracteres repetidos"):
        CNPJ("11.111.111/1111-11")


def test_cnpj_dv_must_be_digits() -> None:
    """Test that the last 2 digits must be numbers."""
    with pytest.raises(InvalidFormatError, match="Os dígitos verificadores do CNPJ"):
        CNPJ("069905900001AB")


def test_cnpj_invalid_first_digit() -> None:
    """Test CNPJ with invalid first verification digit."""
    # Valid is 06990590000123
    with pytest.raises(InvalidDigitError, match="Primeiro dígito verificador inválido."):
        CNPJ("06990590000133")


def test_cnpj_invalid_second_digit() -> None:
    """Test CNPJ with invalid second verification digit."""
    # Valid is 06990590000123
    with pytest.raises(InvalidDigitError, match="Segundo dígito verificador inválido."):
        CNPJ("06990590000124")


@given(
    st.lists(
        st.sampled_from("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
        min_size=12,
        max_size=12,
    )
)
def test_hypothesis_cnpj_generation_roundtrip(base_chars_list: list[str]) -> None:
    """
    Test that calculating the DVs for any 12 random valid characters results in a CNPJ
    that is accepted by our own validation logic.
    """
    # Skip if all characters are the same
    if len(set(base_chars_list)) == 1:
        return

    base = "".join(base_chars_list)
    dv1 = _calculate_dv(base, CNPJ._WEIGHTS_DV1)
    dv2 = _calculate_dv(base + str(dv1), CNPJ._WEIGHTS_DV2)

    cnpj_str = f"{base}{dv1}{dv2}"

    # Should not raise any exception
    cnpj_obj = CNPJ(cnpj_str)
    assert cnpj_obj.clean == cnpj_str

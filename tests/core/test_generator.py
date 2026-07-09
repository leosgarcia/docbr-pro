"""Tests for the generation module."""

import pytest

from docbr_pro.core.cnpj import CNPJ
from docbr_pro.core.cpf import CPF
from docbr_pro.core.generator import generate_cnpj, generate_cpf


def test_generate_cpf() -> None:
    """Test generating a simple numeric CPF."""
    cpf_str = generate_cpf()
    assert len(cpf_str) == 11
    # Validation will raise InvalidDigitError/InvalidFormatError if invalid
    cpf_obj = CPF(cpf_str)
    assert cpf_obj.clean == cpf_str


def test_generate_cpf_formatted() -> None:
    """Test generating a formatted CPF."""
    cpf_str = generate_cpf(formatted=True)
    assert len(cpf_str) == 14
    cpf_obj = CPF(cpf_str)
    assert cpf_obj.formatted == cpf_str


def test_generate_cpf_with_region() -> None:
    """Test generating a CPF for a specific fiscal region (SP)."""
    cpf_str = generate_cpf(region="8")
    cpf_obj = CPF(cpf_str)
    assert cpf_obj.fiscal_region == "SP"


def test_generate_cpf_invalid_region() -> None:
    """Test generating a CPF with an invalid region code."""
    with pytest.raises(ValueError, match="Região fiscal inválida"):
        generate_cpf(region="X")


def test_generate_cnpj_numeric() -> None:
    """Test generating a standard numeric CNPJ."""
    cnpj_str = generate_cnpj()
    assert len(cnpj_str) == 14
    cnpj_obj = CNPJ(cnpj_str)
    assert cnpj_obj.clean == cnpj_str
    # Standard generation uses 0001 for the branch
    assert cnpj_str[8:12] == "0001"


def test_generate_cnpj_numeric_formatted() -> None:
    """Test generating a formatted standard CNPJ."""
    cnpj_str = generate_cnpj(formatted=True)
    assert len(cnpj_str) == 18
    cnpj_obj = CNPJ(cnpj_str)
    assert cnpj_obj.formatted == cnpj_str


def test_generate_cnpj_alphanumeric() -> None:
    """Test generating an alphanumeric CNPJ."""
    cnpj_str = generate_cnpj(alphanumeric=True)
    assert len(cnpj_str) == 14
    cnpj_obj = CNPJ(cnpj_str)
    assert cnpj_obj.clean == cnpj_str

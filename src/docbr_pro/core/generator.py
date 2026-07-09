"""Generation module for CPF and CNPJ."""

import random

from .cnpj import CNPJ
from .cnpj import _calculate_dv as _calculate_cnpj_dv
from .cpf import CPF
from .cpf import _calculate_dv as _calculate_cpf_dv


def generate_cpf(region: str | None = None, formatted: bool = False) -> str:
    """
    Generates a valid CPF.

    Args:
        region: Optional fiscal region code (0-9). If not provided, a random one is used.
        formatted: If True, returns the formatted CPF string.

    Returns:
        A valid string representation of a CPF.
    """
    digits = [random.randint(0, 9) for _ in range(8)]

    if region is not None:
        if str(region) not in CPF._REGION_MAP:
            raise ValueError(f"Região fiscal inválida: {region}. Escolha entre 0 e 9.")
        digits.append(int(region))
    else:
        digits.append(random.randint(0, 9))

    dv1 = _calculate_cpf_dv(digits)
    dv2 = _calculate_cpf_dv(digits + [dv1])

    full_digits = digits + [dv1, dv2]
    doc = "".join(str(d) for d in full_digits)

    return CPF(doc).formatted if formatted else doc


def generate_cnpj(alphanumeric: bool = False, formatted: bool = False) -> str:
    """
    Generates a valid CNPJ.

    Args:
        alphanumeric: If True, generates a CNPJ using the alphanumeric standard (2026).
        formatted: If True, returns the formatted CNPJ string.

    Returns:
        A valid string representation of a CNPJ.
    """
    if alphanumeric:
        charset = CNPJ._ALLOWED_LETTERS + CNPJ._ALLOWED_DIGITS
        base = "".join(random.choice(charset) for _ in range(12))
    else:
        # Standard numeric CNPJ generally ends its root with '0001'
        base = "".join(str(random.randint(0, 9)) for _ in range(8)) + "0001"

    dv1 = _calculate_cnpj_dv(base, CNPJ._WEIGHTS_DV1)
    dv2 = _calculate_cnpj_dv(base + str(dv1), CNPJ._WEIGHTS_DV2)

    doc = f"{base}{dv1}{dv2}"

    return CNPJ(doc).formatted if formatted else doc

"""CNPJ validation and manipulation module."""

import re
from typing import ClassVar

from .exceptions import InvalidDigitError, InvalidFormatError


def _char_value(char: str) -> int:
    """
    Returns the numeric value of a character for CNPJ calculation.
    '0'-'9' -> 0-9
    'A'-'Z' -> 17-42
    """
    return ord(char) - 48


def _calculate_dv(base_chars: str, weights: tuple[int, ...]) -> int:
    """Calculate the verification digit for a given CNPJ base."""
    total = sum(_char_value(c) * w for c, w in zip(base_chars, weights, strict=True))
    remainder = total % 11
    return 0 if remainder < 2 else 11 - remainder


class CNPJ:
    """Class representing a Brazilian CNPJ, including alphanumeric support (2026)."""

    # Character sets for defensive programming, easy to adjust if RFB excludes letters.
    _ALLOWED_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    _ALLOWED_DIGITS = "0123456789"

    # Weights for DV calculations
    _WEIGHTS_DV1: ClassVar[tuple[int, ...]] = (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
    _WEIGHTS_DV2: ClassVar[tuple[int, ...]] = (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)

    def __init__(self, document: str) -> None:
        """
        Initialize and validate a CNPJ.

        Args:
            document: The CNPJ string, formatted or not.

        Raises:
            InvalidFormatError: If length is not 14, contains invalid characters, or same chars.
            InvalidDigitError: If the verification digits are wrong.
        """
        self.raw = document
        # Remove anything that is not a letter or digit, and uppercase it
        self.clean_str = re.sub(r"[^a-zA-Z0-9]", "", document).upper()

        if len(self.clean_str) != 14:
            raise InvalidFormatError(
                f"Quantidade de caracteres incorreta (esperado 14, recebido {len(self.clean_str)})."
            )

        if len(set(self.clean_str)) == 1:
            raise InvalidFormatError("Documento contém apenas caracteres repetidos.")

        # The first 12 characters can be digits or allowed letters.
        base = self.clean_str[:12]
        # The last 2 characters must be digits.
        dvs = self.clean_str[12:]

        for char in base:
            if char not in self._ALLOWED_LETTERS and char not in self._ALLOWED_DIGITS:
                raise InvalidFormatError(f"Caractere inválido na raiz do CNPJ: '{char}'.")

        if not dvs.isdigit():
            raise InvalidFormatError("Os dígitos verificadores do CNPJ devem ser números.")

        dv1 = _calculate_dv(base, self._WEIGHTS_DV1)
        if str(dv1) != dvs[0]:
            raise InvalidDigitError("Primeiro dígito verificador inválido.")

        dv2 = _calculate_dv(base + str(dv1), self._WEIGHTS_DV2)
        if str(dv2) != dvs[1]:
            raise InvalidDigitError("Segundo dígito verificador inválido.")

    @property
    def formatted(self) -> str:
        """Returns the formatted CNPJ."""
        return (
            f"{self.clean_str[:2]}."
            f"{self.clean_str[2:5]}."
            f"{self.clean_str[5:8]}/"
            f"{self.clean_str[8:12]}-"
            f"{self.clean_str[12:]}"
        )

    @property
    def clean(self) -> str:
        """Returns the alphanumeric CNPJ string without formatting."""
        return self.clean_str

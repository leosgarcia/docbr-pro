"""CPF validation and manipulation module."""

import re

from .exceptions import InvalidDigitError, InvalidFormatError


def _calculate_dv(digits: list[int]) -> int:
    """Calculate the verification digit for a given list of digits."""
    weight = len(digits) + 1
    total = sum(d * (weight - i) for i, d in enumerate(digits))
    remainder = total % 11
    return 0 if remainder < 2 else 11 - remainder


class CPF:
    """Class representing a Brazilian CPF."""

    _REGION_MAP = {
        "1": "DF, GO, MS, MT e TO",
        "2": "AC, AM, AP, PA, RO e RR",
        "3": "CE, MA e PI",
        "4": "AL, PB, PE e RN",
        "5": "BA e SE",
        "6": "MG",
        "7": "ES e RJ",
        "8": "SP",
        "9": "PR e SC",
        "0": "RS",
    }

    def __init__(self, document: str) -> None:
        """
        Initialize and validate a CPF.

        Args:
            document: The CPF string, formatted or not.

        Raises:
            InvalidFormatError: If length is not 11 or contains non-digits, or all same digits.
            InvalidDigitError: If the verification digits are wrong.
        """
        self.raw = document
        self.digits_str = re.sub(r"\D", "", document)

        if len(self.digits_str) != 11:
            raise InvalidFormatError(
                f"Quantidade de dígitos incorreta (esperado 11, recebido {len(self.digits_str)})."
            )

        if len(set(self.digits_str)) == 1:
            raise InvalidFormatError("Documento contém apenas dígitos repetidos.")

        digits = [int(d) for d in self.digits_str]

        # Calculate first DV
        dv1 = _calculate_dv(digits[:9])
        if dv1 != digits[9]:
            raise InvalidDigitError("Dígito verificador inválido.")

        # Calculate second DV
        dv2 = _calculate_dv(digits[:10])
        if dv2 != digits[10]:
            raise InvalidDigitError("Dígito verificador inválido.")

    @property
    def formatted(self) -> str:
        """Returns the formatted CPF."""
        return (
            f"{self.digits_str[:3]}.{self.digits_str[3:6]}."
            f"{self.digits_str[6:9]}-{self.digits_str[9:]}"
        )

    @property
    def clean(self) -> str:
        """Returns the digits only."""
        return self.digits_str

    @property
    def fiscal_region(self) -> str:
        """Returns the fiscal region name based on the 9th digit."""
        digit = self.digits_str[8]
        return self._REGION_MAP.get(digit, "Desconhecida")

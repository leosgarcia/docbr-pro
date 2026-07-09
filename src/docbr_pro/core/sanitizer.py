"""Sanitization and fuzzy fixing module for CPF and CNPJ."""

import re


def sanitize_cpf(document: str | int) -> str:
    """
    Cleans and attempts to fix a CPF string or integer.

    Features:
    - Converts integer to string (handling lost leading zeros from Excel).
    - Fixes common typos ('O'/'o' to '0').
    - Removes all non-digit characters.
    - Pads with leading zeros if length is less than 11.
    """
    doc_str = str(document).strip()

    # CPF is strictly numeric, so we can fix common OCR/human typos
    doc_str = doc_str.translate(str.maketrans("Oo", "00"))

    # Remove anything that is not a digit
    doc_str = re.sub(r"\D", "", doc_str)

    # Pad missing leading zeros (very common in Excel CSV exports)
    if 0 < len(doc_str) < 11:
        return doc_str.zfill(11)

    return doc_str


def sanitize_cnpj(document: str | int) -> str:
    """
    Cleans and attempts to fix a CNPJ string or integer.

    Features:
    - Converts integer to string (handling lost leading zeros from Excel).
    - Removes all punctuation and whitespace.
    - Uppercases letters.
    - Pads with leading zeros if length is less than 14.
    """
    doc_str = str(document).strip().upper()

    # Remove anything that is not a digit or allowed letter
    doc_str = re.sub(r"[^A-Z0-9]", "", doc_str)

    # Pad missing leading zeros
    if 0 < len(doc_str) < 14:
        return doc_str.zfill(14)

    return doc_str

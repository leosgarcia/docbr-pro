"""Custom exceptions for the docbr-pro domain."""


class DocbrError(Exception):
    """Base exception for all docbr-pro errors."""

    pass


class InvalidFormatError(DocbrError):
    """Raised when the document has an invalid format (e.g., wrong length, non-digit chars)."""

    pass


class InvalidDigitError(DocbrError):
    """Raised when the document verification digit is mathematically invalid."""

    pass

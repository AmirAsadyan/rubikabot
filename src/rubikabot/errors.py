"""Exceptions raised by rubikabot."""

from __future__ import annotations


class RubikaBotError(Exception):
    """Base class for every error raised by this library."""


class APIError(RubikaBotError):
    """The Rubika API answered with an error status or an HTTP error.

    Attributes:
        method: Name of the API method that was called, for example
            ``sendMessage``.
        payload: The decoded response body when there was one, otherwise
            the raw response text.
        status_code: The HTTP status code, when known.
    """

    def __init__(self, method: str, payload=None, status_code: int | None = None):
        self.method = method
        self.payload = payload
        self.status_code = status_code
        super().__init__(
            f"Rubika API call {method} failed"
            + (f" (HTTP {status_code})" if status_code else "")
            + f": {payload!r}"
        )


class TransportError(RubikaBotError):
    """The request never produced a usable response (network, timeout,
    invalid JSON and similar)."""


class ValidationError(RubikaBotError, ValueError):
    """A locally built object is invalid, for example metadata parts that
    point outside the text. Raised before any network call is made."""

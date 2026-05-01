"""Custom exceptions for the NPS Hikes SDK."""


class NPSHikesError(Exception):
    """Base exception for all NPS Hikes SDK errors."""


class APIError(NPSHikesError):
    """Raised when the API returns an unexpected error response."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"API error {status_code}: {message}")


class ParkNotFoundError(NPSHikesError):
    """Raised when a park code does not match any known park."""

    def __init__(self, park_code: str) -> None:
        self.park_code = park_code
        super().__init__(f"Park not found: '{park_code}'")


class ValidationError(NPSHikesError):
    """Raised when the API returns a 422 validation error."""

    def __init__(self, detail: list[dict]) -> None:
        self.detail = detail
        messages = "; ".join(
            f"{err.get('msg', 'unknown')} (at {err.get('loc', '?')})"
            for err in detail
        )
        super().__init__(f"Validation error: {messages}")

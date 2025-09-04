from json import JSONDecodeError
from typing import Any, Protocol

import httpx


class ApiErrorProtocol(Protocol):
    """Protocol for API errors"""

    def __init__(self, content: bytes, status_code: int):
        pass


class ApiError(Exception):
    """Base exception for API errors"""

    def __init__(self, content: bytes, status_code: int):
        self.status_code = status_code
        self.content = content
        super().__init__(f'API error: {self.status_code} - {self.content}')


def raise_for_status(
    response: httpx.Response,
    *,
    exc_class: type[ApiErrorProtocol] = ApiError,
    expected_status_codes: list[int] = [200, 201, 202, 204],
) -> dict[str, Any] | list[dict[str, Any]] | bytes | None:
    """Raise an exception if the response status code is not in the
    expected status codes. Otherwise, return the response as a deserialized object
    or bytes if the response is not JSON. If the response is 204, return None.

    Args:
        response: The response to check
        exc_class: The exception class to raise
        expected_status_codes: The expected status codes

    Raises:
        exc_class: If the response status code is not in the expected status codes
    """

    if response.status_code not in expected_status_codes:
        raise exc_class(response.content, response.status_code)  # pyright: ignore[reportGeneralTypeIssues]

    if response.status_code == 204:
        return None

    try:
        return response.json()
    except JSONDecodeError:
        return response.content

    return response.content

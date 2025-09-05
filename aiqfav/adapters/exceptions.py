class StoreApiAdapterException(Exception):
    """Base exception for store API adapters"""


class StoreApiUnexpectedResponseError(StoreApiAdapterException):
    """Exception for unexpected responses from store API adapters"""

    def __init__(self, content: bytes, status_code: int):
        self.content = content
        self.status_code = status_code
        super().__init__(
            f'Unexpected response from store API: {status_code} - {content}'
        )


class StoreApiNotFoundError(StoreApiAdapterException):
    """Exception for not found errors from store API adapters"""


class JwtAdapterException(Exception):
    """Base exception for JWT adapters"""


class ExpiredToken(JwtAdapterException):
    """Exception for expired tokens"""


class InvalidAudience(JwtAdapterException):
    """Exception for invalid audiences"""

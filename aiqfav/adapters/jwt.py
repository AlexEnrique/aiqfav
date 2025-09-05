from typing import Iterable

import jwt

from .base import JwtAdapter
from .exceptions import ExpiredToken, InvalidAudience


class JwtAdapterImpl(JwtAdapter):
    def __init__(self, secret: str, algorithm: str):
        self.secret = secret
        self.algorithm = algorithm

    def encode(self, payload: dict) -> str:
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def decode(
        self, token: str, audience: Iterable[str] | None = None
    ) -> dict:
        try:
            return jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                audience=audience,
            )
        except jwt.ExpiredSignatureError as e:
            raise ExpiredToken('Token expired') from e
        except jwt.InvalidTokenError as e:
            raise InvalidAudience('Invalid token') from e

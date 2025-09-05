import logging
from datetime import datetime, timedelta, timezone
from typing import Callable

from passlib.context import CryptContext

from aiqfav.adapters.base import JwtAdapter
from aiqfav.db.base import CustomerRepository
from aiqfav.domain.customer import CustomerNotFound
from aiqfav.services.customer.exceptions import InvalidCredentials


class AuthService:
    def __init__(
        self,
        customer_repo: CustomerRepository,
        pwd_context: CryptContext,
        access_token_expiration: timedelta,
        refresh_token_expiration: timedelta,
        jti_generator: Callable[[], str],
        jwt_adapter: JwtAdapter,
        jwt_issuer: str,
    ):
        self.customer_repo = customer_repo
        self.pwd_context = pwd_context
        self.access_token_expiration = access_token_expiration
        self.refresh_token_expiration = refresh_token_expiration
        self.jwt_adapter = jwt_adapter
        self.jwt_issuer = jwt_issuer
        self.jti_generator = jti_generator

    async def pair_tokens(self, email: str, password: str) -> tuple[str, str]:
        """Generate a pair of access and refresh tokens for a customer

        Args:
            email (str): The email of the customer.
            password (str): The password of the customer.

        Returns:
            tuple[str, str]: A tuple of the access and refresh tokens.

        Raises:
            InvalidCredentials: If the email or password is incorrect.
        """
        logging.info('Generating token pair for customer %s', email)

        invalid_credentials_exception = InvalidCredentials(
            'E-mail ou senha incorretos'
        )

        try:
            customer = await self.customer_repo.get_customer(email=email)
        except CustomerNotFound:
            raise invalid_credentials_exception

        if not self.pwd_context.verify(password, customer.hashed_password):
            raise invalid_credentials_exception

        access_token, refresh_token = self._generate_tokens(customer.id)

        return access_token, refresh_token

    def _generate_tokens(self, customer_id: int) -> tuple[str, str]:
        access_token = self._generate_token(customer_id, 'access')
        refresh_token = self._generate_token(customer_id, 'refresh')
        return access_token, refresh_token

    def _generate_token(self, customer_id: int, token_type: str) -> str:
        iat = datetime.now(timezone.utc)
        specific_data = {
            'access': {
                'aud': 'access',
                'exp': iat + self.access_token_expiration,
            },
            'refresh': {
                'aud': 'refresh',
                'exp': iat + self.refresh_token_expiration,
            },
        }

        if token_type not in specific_data:
            raise ValueError(f'Invalid token type: {token_type}')

        token_data = {
            'jti': self.jti_generator(),
            'iss': self.jwt_issuer,
            'iat': iat,
            'sub': customer_id,
            **specific_data[token_type],
        }

        return self.jwt_adapter.encode(token_data)

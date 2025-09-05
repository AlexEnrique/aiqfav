import uuid
from datetime import timedelta

import httpx
import pytest
from faker import Faker
from passlib.context import CryptContext

from aiqfav.adapters.base import JwtAdapter, StoreApiAdapter
from aiqfav.adapters.fakestore_api import FakeStoreApi
from aiqfav.adapters.jwt import JwtAdapterImpl
from aiqfav.adapters.redis_adapter import RedisAsyncProtocol
from aiqfav.db.base import CustomerRepository
from aiqfav.services.admin import AdminService
from aiqfav.services.auth import AuthService
from aiqfav.services.customer import CustomerService

from ._mocks.customer_repo import CustomerRepositoryMock
from ._mocks.httpx import HttpxAsyncClientMock
from ._mocks.redis import RedisMock


@pytest.fixture
def customer_repo() -> CustomerRepository:
    return CustomerRepositoryMock()


@pytest.fixture
def redis_mock() -> RedisAsyncProtocol:
    return RedisMock()


@pytest.fixture
def client_mock():
    return HttpxAsyncClientMock()


@pytest.fixture
def store_api_adapter(
    client_mock: httpx.AsyncClient,
    redis_mock: RedisAsyncProtocol,
) -> StoreApiAdapter:
    return FakeStoreApi(
        'https://fakestoreapi.com',
        client_mock,
        redis_mock,
    )


@pytest.fixture
def pwd_context() -> CryptContext:
    return CryptContext(schemes=['argon2'], deprecated='auto')


@pytest.fixture
def customer_service(
    customer_repo: CustomerRepository,
    store_api_adapter: StoreApiAdapter,
    pwd_context: CryptContext,
    redis_mock: RedisAsyncProtocol,
) -> CustomerService:
    return CustomerService(
        customer_repo=customer_repo,
        store_api_adapter=store_api_adapter,
        pwd_context=pwd_context,
        redis=redis_mock,
    )


@pytest.fixture
def jwt_adapter() -> JwtAdapter:
    return JwtAdapterImpl(
        secret='secret',
        algorithm='HS256',
    )


@pytest.fixture
def auth_service(
    customer_repo: CustomerRepository,
    pwd_context: CryptContext,
    jwt_adapter: JwtAdapter,
) -> AuthService:
    return AuthService(
        customer_repo=customer_repo,
        pwd_context=pwd_context,
        access_token_expiration=timedelta(days=1),
        refresh_token_expiration=timedelta(days=30),
        jwt_adapter=jwt_adapter,
        jwt_issuer='aiqfav',
        jti_generator=lambda: uuid.uuid4().hex,
    )


@pytest.fixture
def admin_service(
    customer_repo: CustomerRepository,
    customer_service: CustomerService,
) -> AdminService:
    return AdminService(
        customer_service=customer_service,
        customer_repo=customer_repo,
    )


@pytest.fixture
def fake() -> Faker:
    return Faker(['pt_BR'])

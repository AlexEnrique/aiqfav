import uuid
from datetime import timedelta

import asyncpg
import httpx
import pytest
from environs import Env
from faker import Faker
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from aiqfav.adapters.base import JwtAdapter, StoreApiAdapter
from aiqfav.adapters.fakestore_api import FakeStoreApi
from aiqfav.adapters.jwt import JwtAdapterImpl
from aiqfav.adapters.redis_adapter import RedisAsyncProtocol
from aiqfav.db.base import CustomerRepository
from aiqfav.db.implementations.customer import CustomerRepositoryImpl
from aiqfav.db.implementations.models import Base
from aiqfav.services.admin import AdminService
from aiqfav.services.auth import AuthService
from aiqfav.services.customer import CustomerService

from ._mocks.customer_repo import CustomerRepositoryMock
from ._mocks.httpx import HttpxAsyncClientMock
from ._mocks.redis import RedisMock

env = Env()
env.read_env()


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


@pytest.fixture(scope='session')
def postgres_db():
    return {
        'user': env('POSTGRES_USER'),
        'password': env('POSTGRES_PASSWORD'),
        'host': env('POSTGRES_HOST'),
        'port': env.int('POSTGRES_PORT'),
        'database': 'test_' + env('POSTGRES_DB'),
    }


@pytest.fixture(scope='session')
def temp_db_url(postgres_db: dict):
    """Cria uma URL de banco temporário para PostgreSQL."""
    user = postgres_db['user']
    password = postgres_db['password']
    host = postgres_db['host']
    port = postgres_db['port']
    database = postgres_db['database']
    return f'postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}'


async def create_test_database(postgres_db: dict):
    """Cria o banco de dados de teste se não existir."""
    try:
        conn: asyncpg.Connection = await asyncpg.connect(
            host=postgres_db['host'],
            port=postgres_db['port'],
            user=postgres_db['user'],
            password=postgres_db['password'],
            database='postgres',
        )

        exists = await conn.fetchval(
            'SELECT 1 FROM pg_database WHERE datname = $1',
            postgres_db['database'],
        )

        if not exists:
            # Postgres não suporta $1 em comandos DDL
            await conn.execute(f'CREATE DATABASE {postgres_db["database"]}')
            print('Banco de dados de teste criado com sucesso!')

        await conn.close()
    except Exception as e:
        print(f'Erro ao criar banco de teste: {e}')
        raise


@pytest.fixture(scope='session', autouse=True)
async def setup_test_db(postgres_db: dict):
    """Configura o banco de dados de teste antes de todos os testes."""
    await create_test_database(postgres_db)


@pytest.fixture
async def async_session(temp_db_url):
    """Cria uma sessão assíncrona com PostgreSQL temporário."""
    engine = create_async_engine(
        temp_db_url,
        echo=False,
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    yield async_session_maker

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def customer_repo_impl(
    async_session: async_sessionmaker[AsyncSession],
):
    """Cria uma instância do CustomerRepositoryImpl para testes."""
    return CustomerRepositoryImpl(async_session)

from typing import Annotated

from environs import Env
from fastapi import Depends
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from aiqfav.adapters.base import StoreApiAdapter
from aiqfav.adapters.fakestore_api import FakeStoreApi
from aiqfav.db.base import CustomerRepository
from aiqfav.db.implementations.customer import CustomerRepositoryImpl
from aiqfav.services.customer import CustomerService

env = Env()
env.read_env()


def get_async_session() -> async_sessionmaker[AsyncSession]:
    """Dependency para obter uma sessão assíncrona"""
    DATABASE_URL = env('DATABASE_URL')
    engine = create_async_engine(DATABASE_URL, echo=True)
    # async_sessionmaker: a factory for new AsyncSession objects.
    # expire_on_commit - don't expire objects after transaction commit
    return async_sessionmaker(engine, expire_on_commit=False)


def get_pwd_context() -> CryptContext:
    """Dependency para obter o contexto de hash de senhas"""
    return CryptContext(schemes=['argon2'], deprecated='auto')


def get_customer_repository(
    async_session: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_async_session)
    ],
) -> CustomerRepository:
    """Dependency para obter o repositório de clientes"""
    return CustomerRepositoryImpl(async_session)


def get_store_api_adapter() -> StoreApiAdapter:
    """Dependency para obter o adaptador de API de loja"""
    return FakeStoreApi(env('FAKE_STORE_API_URL'))


def get_customer_service(
    customer_repository: Annotated[
        CustomerRepository, Depends(get_customer_repository)
    ],
    store_api_adapter: Annotated[
        StoreApiAdapter, Depends(get_store_api_adapter)
    ],
    pwd_context: Annotated[CryptContext, Depends(get_pwd_context)],
) -> CustomerService:
    """Dependency para obter o serviço de clientes"""
    return CustomerService(customer_repository, store_api_adapter, pwd_context)

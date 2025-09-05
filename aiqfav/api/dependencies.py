import uuid
from datetime import timedelta
from typing import Annotated

import redis.asyncio as redis
from environs import Env
from fastapi import Depends
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from aiqfav.adapters.base import JwtAdapter, StoreApiAdapter
from aiqfav.adapters.fakestore_api import FakeStoreApi
from aiqfav.adapters.jwt import JwtAdapterImpl
from aiqfav.db.base import CustomerRepository
from aiqfav.db.implementations.customer import CustomerRepositoryImpl
from aiqfav.services.auth import AuthService
from aiqfav.services.customer import CustomerService

env = Env()
env.read_env()


def get_async_session() -> async_sessionmaker[AsyncSession]:
    """Dependency para obter uma sessão assíncrona"""
    DATABASE_URL = env('DATABASE_URL')
    engine = create_async_engine(DATABASE_URL, echo=False)
    # async_sessionmaker: a factory for new AsyncSession objects.
    # expire_on_commit - don't expire objects after transaction commit
    return async_sessionmaker(engine, expire_on_commit=False)


def get_pwd_context() -> CryptContext:
    """Dependency para obter o contexto de hash de senhas"""
    return CryptContext(schemes=['argon2'], deprecated='auto')


def get_redis() -> redis.Redis:
    """Dependency para obter o Redis"""
    return redis.Redis(
        host=env('REDIS_HOST'),
        port=env.int('REDIS_PORT'),
        db=env.int('REDIS_DB'),
    )


def get_customer_repository(
    async_session: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_async_session)
    ],
) -> CustomerRepository:
    """Dependency para obter o repositório de clientes"""
    return CustomerRepositoryImpl(async_session)


def get_store_api_adapter(
    redis: Annotated[redis.Redis, Depends(get_redis)],
) -> StoreApiAdapter:
    """Dependency para obter o adaptador de API de loja"""
    return FakeStoreApi(env('FAKE_STORE_API_URL'), redis)


def get_customer_service(
    customer_repository: Annotated[
        CustomerRepository, Depends(get_customer_repository)
    ],
    store_api_adapter: Annotated[
        StoreApiAdapter, Depends(get_store_api_adapter)
    ],
    pwd_context: Annotated[CryptContext, Depends(get_pwd_context)],
    redis: Annotated[redis.Redis, Depends(get_redis)],
) -> CustomerService:
    """Dependency para obter o serviço de clientes"""
    return CustomerService(
        customer_repository, store_api_adapter, pwd_context, redis
    )


def get_access_token_expiration() -> timedelta:
    """Dependency para obter o tempo de expiração do token de acesso"""
    return timedelta(minutes=env.int('ACCESS_TOKEN_EXPIRE_MINUTES'))


def get_refresh_token_expiration() -> timedelta:
    """Dependency para obter o tempo de expiração do token de refresh"""
    return timedelta(days=env.int('REFRESH_TOKEN_EXPIRE_DAYS'))


def get_jwt_adapter() -> JwtAdapter:
    """Dependency para obter o adaptador de JWT"""
    return JwtAdapterImpl(env('SECRET_KEY'), env('ALGORITHM'))


def get_auth_service(
    customer_repository: Annotated[
        CustomerRepository, Depends(get_customer_repository)
    ],
    pwd_context: Annotated[CryptContext, Depends(get_pwd_context)],
    access_token_expiration: Annotated[
        timedelta, Depends(get_access_token_expiration)
    ],
    refresh_token_expiration: Annotated[
        timedelta, Depends(get_refresh_token_expiration)
    ],
    jwt_adapter: Annotated[JwtAdapter, Depends(get_jwt_adapter)],
) -> AuthService:
    """Dependency para obter o serviço de autenticação"""
    return AuthService(
        customer_repo=customer_repository,
        pwd_context=pwd_context,
        access_token_expiration=access_token_expiration,
        refresh_token_expiration=refresh_token_expiration,
        jwt_adapter=jwt_adapter,
        jwt_issuer=env('JWT_ISSUER'),
        jti_generator=lambda: uuid.uuid4().hex,
    )

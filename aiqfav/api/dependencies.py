from typing import Annotated

from environs import Env
from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from aiqfav.db.base import CustomerRepository
from aiqfav.db.implementations.repositories import CustomerRepositoryImpl

env = Env()
env.read_env()


def get_async_session() -> async_sessionmaker[AsyncSession]:
    """Dependency para obter uma sessão assíncrona"""
    DATABASE_URL = env('DATABASE_URL')
    engine = create_async_engine(DATABASE_URL, echo=True)
    # async_sessionmaker: a factory for new AsyncSession objects.
    # expire_on_commit - don't expire objects after transaction commit
    return async_sessionmaker(engine, expire_on_commit=False)


def get_customer_repository(
    async_session: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_async_session)
    ],
) -> CustomerRepository:
    """Dependency para obter o repositório de clientes"""
    return CustomerRepositoryImpl(async_session)

#! /usr/bin/env python3

import asyncio
import getpass
import sys

import httpx
import redis.asyncio as redis
from environs import Env
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from aiqfav.adapters.fakestore_api import FakeStoreApi
from aiqfav.adapters.redis_adapter import RedisAdapter
from aiqfav.db.implementations.customer import CustomerRepositoryImpl
from aiqfav.domain.customer import CustomerCreate
from aiqfav.services.admin import AdminService
from aiqfav.services.customer import CustomerService
from aiqfav.services.customer.exceptions import EmailAlreadyExists

env = Env()
env.read_env()


def get_async_session() -> async_sessionmaker[AsyncSession]:
    """Dependency para obter uma sessão assíncrona"""
    DATABASE_URL = env('DATABASE_URL')
    engine = create_async_engine(DATABASE_URL, echo=False)
    return async_sessionmaker(engine, expire_on_commit=False)


async def create_admin_customer():
    """Create a new admin customer."""

    # We could simplify the instantiation of the dependencies by using a
    # DI framework, like Dependency Injector
    # (https://python-dependency-injector.ets-labs.org/)
    customer_repo = CustomerRepositoryImpl(get_async_session())
    pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')
    redis_instance = RedisAdapter(
        redis.Redis(
            host=env('REDIS_HOST'),
            port=env.int('REDIS_PORT'),
            db=env.int('REDIS_DB'),
        )
    )

    customer_service = CustomerService(
        customer_repo=customer_repo,
        pwd_context=pwd_context,
        redis=redis_instance,
        store_api_adapter=FakeStoreApi(
            base_url=env('FAKE_STORE_API_URL'),
            client=httpx.AsyncClient(),
            redis=redis_instance,
        ),
    )

    admin_service = AdminService(
        customer_repo=customer_repo,
        customer_service=customer_service,
    )

    print('=' * 50)
    print('CRIAÇÃO DE CLIENTE ADMINISTRADOR')
    print('=' * 50)

    name = input('Nome: ')
    email = input('Email: ')
    password = getpass.getpass('Senha: ')

    try:
        customer_created = await admin_service.create_admin(
            CustomerCreate(
                name=name,
                email=email,
                password=password,
            )
        )
    except ValidationError:
        print('=' * 50)
        print(
            (
                '[ERRO]: A senha deve conter pelo menos 8 caracteres, '
                'uma letra maiúscula, uma letra minúscula, um número e '
                'um símbolo especial.\a'
            )
        )
        print('=' * 50)
        return sys.exit(1)
    except EmailAlreadyExists:
        print('=' * 50)
        print('[ERRO]: Já existe um cliente com este e-mail\a')
        print('=' * 50)
        return sys.exit(1)

    print('=' * 50)
    print(f'Cliente criado com sucesso: {customer_created!r}')
    print('=' * 50)
    return sys.exit(0)


if __name__ == '__main__':
    asyncio.run(create_admin_customer())

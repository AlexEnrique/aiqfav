from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from aiqfav.db.implementations.repositories import CustomerRepositoryImpl

from environs import Env

env = Env()
env.read_env()


app = FastAPI()


@app.get('/customers')
async def list_customers():
    """Endpoint para listar todos os clientes"""

    # TODO: Refatorar para usar o DI
    DATABASE_URL = env('DATABASE_URL')
    engine = create_async_engine(DATABASE_URL, echo=True)
    # async_sessionmaker: a factory for new AsyncSession objects.
    # expire_on_commit - don't expire objects after transaction commit
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    repo = CustomerRepositoryImpl(async_session)
    return await repo.list_customers()

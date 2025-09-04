from typing import Annotated

from environs import Env
from fastapi import Depends, FastAPI

from aiqfav.db.base import CustomerRepository

from .dependencies import get_customer_repository

env = Env()
env.read_env()


app = FastAPI()


@app.get('/customers')
async def list_customers(
    customer_repo: Annotated[
        CustomerRepository, Depends(get_customer_repository)
    ],
):
    """Endpoint para listar todos os clientes"""
    return await customer_repo.list_customers()

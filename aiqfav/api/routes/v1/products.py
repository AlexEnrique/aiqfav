from typing import Annotated

from fastapi import APIRouter, Depends

from aiqfav.adapters.base import StoreApiAdapter
from aiqfav.api.dependencies import get_store_api_adapter
from aiqfav.domain.product import ProductPublic

__all__ = ['router']

router = APIRouter(tags=['products'])


@router.get(
    '/products',
    response_model=list[ProductPublic],
    summary='Listar produtos',
    description='Endpoint auxiliar para listar todos os produtos',
)
async def list_products(
    store_api: Annotated[StoreApiAdapter, Depends(get_store_api_adapter)],
):
    return await store_api.list_products()

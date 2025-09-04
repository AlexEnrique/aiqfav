import asyncio
from typing import Iterable

import httpx

from aiqfav.domain.product import ProductPublic
from aiqfav.utils.httpx import raise_for_status

from .base import StoreApiAdapter
from .exceptions import StoreApiNotFoundError, StoreApiUnexpectedResponseError

__all__ = ['FakeStoreApi']


class FakeStoreApi(StoreApiAdapter):
    def __init__(self, base_url: str):
        assert isinstance(base_url, str) and base_url, (
            'base_url must be a non-empty string'
        )
        self.base_url = base_url.rstrip('/')

    async def list_products(self) -> list[ProductPublic]:
        """List products from the store API"""

        async with httpx.AsyncClient() as session:
            response = await session.get(f'{self.base_url}/products')

            data = raise_for_status(
                response,
                exc_class=StoreApiUnexpectedResponseError,
            )

            assert isinstance(data, list)
            return [self._validate_product(product) for product in data]

    async def get_product(self, product_id: int) -> ProductPublic:
        """Get a product from the store API"""
        async with httpx.AsyncClient() as session:
            response = await session.get(
                f'{self.base_url}/products/{product_id}'
            )

            if response.status_code == 404:
                raise StoreApiNotFoundError(
                    response.content, response.status_code
                )

            data = raise_for_status(
                response,
                exc_class=StoreApiUnexpectedResponseError,
            )

            assert isinstance(data, dict)
            return self._validate_product(data)

    async def get_products_in_batch(
        self, product_ids: Iterable[int]
    ) -> list[ProductPublic]:
        """Get products in batch from the store API"""
        return await asyncio.gather(
            *[self.get_product(product_id) for product_id in product_ids]
        )

    def _validate_product(self, product: dict) -> ProductPublic:
        """Validate a product"""

        assert isinstance(product, dict)
        assert 'id' in product
        assert 'title' in product
        assert 'image' in product
        assert 'price' in product

        rating = product.get('rating', {}).get('rate')

        return ProductPublic(
            id=product['id'],
            title=product['title'],
            image=product['image'],
            price=product['price'],
            rating=rating,
        )

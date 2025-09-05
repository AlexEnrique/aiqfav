import asyncio
import json
import logging
from typing import Iterable

import httpx
import redis.asyncio as redis
from environs import Env

from aiqfav.domain.product import ProductPublic
from aiqfav.utils.httpx import raise_for_status

from .base import StoreApiAdapter
from .exceptions import StoreApiNotFoundError, StoreApiUnexpectedResponseError

__all__ = ['FakeStoreApi']

env = Env()
env.read_env()


CACHE_EXPIRATION = 60 * 60  # 1 hour


class FakeStoreApi(StoreApiAdapter):
    def __init__(self, base_url: str):
        assert isinstance(base_url, str) and base_url, (
            'base_url must be a non-empty string'
        )
        self.base_url = base_url.rstrip('/')
        self.redis = redis.Redis(
            host=env('REDIS_HOST'),
            port=env.int('REDIS_PORT'),
            db=env.int('REDIS_DB'),
        )

    async def list_products(self) -> list[ProductPublic]:
        """List products from the store API"""
        logging.info('Listing products from the store API')

        async with httpx.AsyncClient() as session:
            cached_data = await self.redis.get('products')
            if cached_data:
                logging.debug('Cache hit for products')
                return [
                    self._validate_product(product)
                    for product in json.loads(cached_data)
                ]
            else:
                logging.debug('Cache miss for products')

            response = await session.get(f'{self.base_url}/products')

            data = raise_for_status(
                response,
                exc_class=StoreApiUnexpectedResponseError,
            )

            assert isinstance(data, list)
            await self.redis.set(
                'products', json.dumps(data), ex=CACHE_EXPIRATION
            )

            pipeline = self.redis.pipeline()
            for product in data:
                pipeline.set(
                    f'product:{product["id"]}',
                    json.dumps(product),
                    ex=CACHE_EXPIRATION,
                )
            await pipeline.execute()

            return [self._validate_product(product) for product in data]

    async def get_product(self, product_id: int) -> ProductPublic:
        """Get a product from the store API"""
        logging.info('Getting product %s from the store API', product_id)

        async with httpx.AsyncClient() as session:
            response = await session.get(
                f'{self.base_url}/products/{product_id}'
            )

            cached_data = await self.redis.get(f'product:{product_id}')
            if cached_data:
                logging.debug('Cache hit for product %s', product_id)
                return self._validate_product(json.loads(cached_data))
            else:
                logging.debug('Cache miss for product %s', product_id)

            if response.status_code == 404:
                raise StoreApiNotFoundError(
                    response.content, response.status_code
                )

            data = raise_for_status(
                response,
                exc_class=StoreApiUnexpectedResponseError,
            )

            assert isinstance(data, dict)
            await self.redis.set(
                f'product:{product_id}', json.dumps(data), ex=CACHE_EXPIRATION
            )

            return self._validate_product(data)

    async def get_products_in_batch(
        self, product_ids: Iterable[int]
    ) -> list[ProductPublic]:
        """Get products in batch from the store API"""
        logging.info(
            'Getting products in batch %s from the store API', product_ids
        )

        # Usando asyncio.gather para executar as chamadas de forma concorrente
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

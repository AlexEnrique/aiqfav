import logging

import redis.asyncio as redis
from passlib.context import CryptContext

from aiqfav.adapters.base import StoreApiAdapter
from aiqfav.db.base import CustomerRepository
from aiqfav.domain.customer import (
    CustomerCreate,
    CustomerListAdapter,
    CustomerNotFound,
    CustomerPublic,
    CustomerWithPassword,
)
from aiqfav.domain.product import ProductListAdapter, ProductPublic

from .exceptions import EmailAlreadyExists


class CustomerService:
    def __init__(
        self,
        customer_repo: CustomerRepository,
        store_api_adapter: StoreApiAdapter,
        pwd_context: CryptContext,
        redis: redis.Redis,
        cache_expiration: int = 60 * 60,
    ):
        self.customer_repo = customer_repo
        self.store_api_adapter = store_api_adapter
        self.pwd_context = pwd_context
        self.redis = redis
        self.cache_expiration = cache_expiration

    async def get_customer_by_id(self, id: int) -> CustomerPublic:
        logging.info('Getting customer by id %s', id)

        if cached_customer_data := await self._get_cached_customer(id):
            logging.debug('Cache hit for customer %s', id)
            return cached_customer_data
        else:
            logging.debug('Cache miss for customer %s', id)

        customer_in_db = await self.customer_repo.get_customer(id=id)

        customer = CustomerPublic.model_validate(customer_in_db)

        await self._cache_customer(customer)

        return customer

    async def list_customers(self) -> list[CustomerPublic]:
        logging.info('Listing customers')

        if cached_customers_data := await self._get_cached_customers():
            logging.debug('Cache hit for customers')
            return cached_customers_data
        else:
            logging.debug('Cache miss for customers')

        customers_in_db = await self.customer_repo.list_customers()

        customers = [
            CustomerPublic.model_validate(customer)
            for customer in customers_in_db
        ]

        await self._cache_customers(customers)

        return customers

    async def create_customer(
        self, customer: CustomerCreate
    ) -> CustomerPublic:
        logging.info('Creating customer %s', customer.email)

        try:
            customer_in_db = await self.customer_repo.get_customer(
                email=customer.email
            )
        except CustomerNotFound:
            pass
        else:
            raise EmailAlreadyExists('Já existe um cliente com este e-mail')

        hashed_password = self.pwd_context.hash(customer.password)
        customer_with_password = CustomerWithPassword(
            name=customer.name,
            email=customer.email,
            hashed_password=hashed_password,
        )
        customer_in_db = await self.customer_repo.create_customer(
            customer_with_password
        )

        new_customer = CustomerPublic.model_validate(customer_in_db)

        await self._cache_customer(new_customer)
        await self._delete_cached_customers()

        return new_customer

    async def delete_customer(self, id: int) -> None:
        logging.info('Deleting customer %s', id)

        await self.customer_repo.delete_customer(id=id)
        await self._delete_cached_customer(id)
        await self._delete_cached_customers()

    async def list_favorites_for_customer(
        self, customer_id: int
    ) -> list[ProductPublic]:
        logging.info('Listing favorites for customer %s', customer_id)

        cached_favorites_data = await self._get_cached_favorites(customer_id)
        if cached_favorites_data:
            logging.debug(
                'Cache hit for favorites for customer %s', customer_id
            )
            return cached_favorites_data
        else:
            logging.debug(
                'Cache miss for favorites for customer %s', customer_id
            )

        # Valida se o cliente existe
        # Raises CustomerNotFound, se o cliente não existe
        await self.customer_repo.get_customer(id=customer_id)

        favorites_in_db = await self.customer_repo.list_favorites_for_customer(
            customer_id
        )
        product_ids = [favorite.product_id for favorite in favorites_in_db]
        favorite_products = await self.store_api_adapter.get_products_in_batch(
            product_ids
        )

        await self._cache_favorites(customer_id, favorite_products)

        return favorite_products

    async def add_favorite(
        self, customer_id: int, product_id: int
    ) -> ProductPublic:
        """Add a product to customer's favorites.

        Args:
            customer_id (int): the customer id.
            product_id (int): the product id.
        """
        logging.info(
            'Adding favorite product %s for customer %s',
            product_id,
            customer_id,
        )

        # Valida se o cliente existe
        # Raises CustomerNotFound, se o cliente não existe
        await self.customer_repo.get_customer(id=customer_id)

        product = await self.store_api_adapter.get_product(product_id)

        await self.customer_repo.add_favorite(customer_id, product_id)
        await self._delete_cached_favorites(customer_id)

        return product

    async def remove_favorite(self, customer_id: int, product_id: int) -> None:
        """Remove a product from customer's favorites.

        Args:
            customer_id (int): the customer id.
            product_id (int): the product id.
        """
        logging.info(
            'Removing favorite product %s for customer %s',
            product_id,
            customer_id,
        )

        await self.customer_repo.get_customer(id=customer_id)
        await self.customer_repo.remove_favorite(customer_id, product_id)
        await self._delete_cached_favorites(customer_id)

    ### Caching
    async def _get_cached_customer(self, id: int) -> CustomerPublic | None:
        cached_customer_data = await self.redis.get(f'customer:{id}')
        if cached_customer_data:
            return CustomerPublic.model_validate_json(cached_customer_data)
        else:
            return None

    async def _get_cached_customers(self) -> list[CustomerPublic] | None:
        cached_customers_data = await self.redis.get('customers')
        if cached_customers_data:
            return CustomerListAdapter.validate_json(cached_customers_data)
        else:
            return None

    async def _get_cached_favorites(
        self, customer_id: int
    ) -> list[ProductPublic] | None:
        cached_favorites_data = await self.redis.get(
            f'favorites:{customer_id}'
        )
        if cached_favorites_data:
            return ProductListAdapter.validate_json(cached_favorites_data)
        else:
            return None

    async def _cache_customer(self, customer: CustomerPublic) -> None:
        customer_data = customer.model_dump_json()
        await self.redis.set(
            f'customer:{customer.id}', customer_data, ex=self.cache_expiration
        )

    async def _cache_customers(self, customers: list[CustomerPublic]) -> None:
        customers_data = CustomerListAdapter.dump_json(customers)
        await self.redis.set(
            'customers', customers_data, ex=self.cache_expiration
        )

    async def _cache_favorites(
        self, customer_id: int, favorites: list[ProductPublic]
    ) -> None:
        favorites_data = ProductListAdapter.dump_json(favorites)
        await self.redis.set(
            f'favorites:{customer_id}',
            favorites_data,
            ex=self.cache_expiration,
        )

    async def _delete_cached_customer(self, id: int) -> None:
        await self.redis.delete(f'customer:{id}')

    async def _delete_cached_customers(self) -> None:
        await self.redis.delete('customers')

    async def _delete_cached_favorites(self, customer_id: int) -> None:
        await self.redis.delete(f'favorites:{customer_id}')

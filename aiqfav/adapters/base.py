import abc

from aiqfav.domain.product import ProductPublic


class StoreApiAdapter(abc.ABC):
    """Base class for store API adapters"""

    @abc.abstractmethod
    async def list_products(self) -> list[ProductPublic]:
        """Get all products from the store API"""

    @abc.abstractmethod
    async def get_product(self, product_id: int) -> ProductPublic:
        """Get a product from the store API"""

    @abc.abstractmethod
    async def get_products_in_batch(
        self, product_ids: list[int]
    ) -> list[ProductPublic]:
        """Get products in batch from the store API"""

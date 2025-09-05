import abc

from aiqfav.domain.product import ProductPublic


class StoreApiAdapter(abc.ABC):
    """Base class for store API adapters"""

    @abc.abstractmethod
    async def list_products(self) -> list[ProductPublic]:
        """Get all products from the store API

        Returns:
            list[ProductPublic]: the list of products.

        Raises:
            StoreApiUnexpectedResponseError: in case of unexpected response.
        """

    @abc.abstractmethod
    async def get_product(self, product_id: int) -> ProductPublic:
        """Get a product from the store API

        Args:
            product_id (int): the product id.

        Returns:
            ProductPublic: the product object.

        Raises:
            StoreApiNotFoundError: if the product is not found.
            StoreApiUnexpectedResponseError: in case of unexpected response.
        """

    @abc.abstractmethod
    async def get_products_in_batch(
        self, product_ids: list[int]
    ) -> list[ProductPublic]:
        """Get products in batch from the store API

        Args:
            product_ids (list[int]): the list of product ids.

        Returns:
            list[ProductPublic]: the list of products.

        Raises:
            StoreApiNotFoundError: if one of the products is not found.
            StoreApiUnexpectedResponseError: in case of unexpected response.
        """


class JwtAdapter(abc.ABC):
    """Base class for JWT adapters"""

    @abc.abstractmethod
    def __init__(self, secret: str, algorithm: str): ...

    @abc.abstractmethod
    def encode(self, payload: dict) -> str:
        """Encode a payload into a JWT"""

    @abc.abstractmethod
    def decode(self, token: str) -> dict:
        """Decode a JWT into a payload"""

import abc
from typing import overload

from aiqfav.domain.customer import CustomerInDb, CustomerWithPassword
from aiqfav.domain.favorite import FavoriteInDb


class CustomerRepository(abc.ABC):
    """Base class for the Customer repository"""

    @overload
    async def get_customer(self, *, email: str) -> CustomerInDb:
        """Query a customer by email (alternate key).

        Args:
            email (str): the customer email.

        Returns:
            Customer: the customer object.

        Raises:
            CustomerNotFound: if the customer cannot be found.
        """

    @overload
    async def get_customer(self, *, id: int) -> CustomerInDb:
        """Query a customer by id (primary key).

        Args:
            id (int): the customer id.

        Returns:
            Customer: the customer object.

        Raises:
            CustomerNotFound: if the customer cannot be found.
        """

    @abc.abstractmethod
    async def get_customer(
        self, *, email: str | None = None, id: int | None = None
    ) -> CustomerInDb: ...

    @abc.abstractmethod
    async def list_customers(self) -> list[CustomerInDb]:
        """List all customers."""

    @abc.abstractmethod
    async def create_customer(
        self, customer: CustomerWithPassword
    ) -> CustomerInDb:
        """Create a customer."""

    @abc.abstractmethod
    async def delete_customer(self, id: int) -> None:
        """Delete a customer.

        Args:
            id (int): the customer id.

        Raises:
            CustomerNotFound: if the customer cannot be found.
        """

    @abc.abstractmethod
    async def list_favorites_for_customer(
        self, customer_id: int
    ) -> list[FavoriteInDb]:
        """List all favorites for a customer.

        Args:
            customer_id (int): the customer id.

        Raises:
            CustomerNotFound: if the a customer with the given id cannot be found.
        """

    @abc.abstractmethod
    async def add_favorite(self, customer_id: int, product_id: int) -> None:
        """Add a product to customer's favorites.

        Args:
            customer_id (int): the customer id.
            product_id (int): the product id.
        """

    @abc.abstractmethod
    async def remove_favorite(self, customer_id: int, product_id: int) -> None:
        """Remove a product from customer's favorites.

        Args:
            customer_id (int): the customer id.
            product_id (int): the product id.

        Raises:
            FavoriteNotFound: if the favorited product was not found for the customer.
        """

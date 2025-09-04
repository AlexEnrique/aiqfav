import abc
from typing import overload

from aiqfav.domain.customer import CustomerInDb, CustomerWithPassword


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
    async def list_customers(self) -> list[CustomerInDb]: ...

    @abc.abstractmethod
    async def create_customer(
        self, customer: CustomerWithPassword
    ) -> CustomerInDb: ...

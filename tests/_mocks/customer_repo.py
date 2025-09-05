from aiqfav.db.base import CustomerRepository
from aiqfav.domain.customer import (
    CustomerInDb,
    CustomerNotFound,
    CustomerWithPassword,
)
from aiqfav.domain.favorite import FavoriteInDb


class CustomerRepositoryMock(CustomerRepository):
    def __init__(self):
        self._customers: list[CustomerInDb] = []
        self._favorites: list[FavoriteInDb] = []

    async def get_customer(
        self, *, email: str | None = None, id: int | None = None
    ) -> CustomerInDb:
        if email:
            customer = next(
                (
                    customer
                    for customer in self._customers
                    if customer.email == email
                ),
                None,
            )
        elif id:
            customer = next(
                (
                    customer
                    for customer in self._customers
                    if customer.id == id
                ),
                None,
            )
        else:
            raise ValueError('Either email or id must be provided')

        if not customer:
            raise CustomerNotFound(f'Customer with id {id} not found')

        return customer

    async def list_customers(self) -> list[CustomerInDb]:
        return self._customers

    async def create_customer(
        self, customer: CustomerWithPassword
    ) -> CustomerInDb:
        customer_in_db = CustomerInDb(
            id=self._get_next_id(),
            name=customer.name,
            email=customer.email,
            hashed_password=customer.hashed_password,
        )
        self._customers.append(customer_in_db)
        return customer_in_db

    async def delete_customer(self, id: int) -> None:
        self._customers = [
            customer for customer in self._customers if customer.id != id
        ]

    async def list_favorites_for_customer(
        self, customer_id: int
    ) -> list[FavoriteInDb]:
        return [
            favorite
            for favorite in self._favorites
            if favorite.customer_id == customer_id
        ]

    async def add_favorite(self, customer_id: int, product_id: int) -> None:
        self._favorites.append(
            FavoriteInDb(
                customer_id=customer_id,
                product_id=product_id,
            )
        )

    async def remove_favorite(self, customer_id: int, product_id: int) -> None:
        self._favorites = [
            favorite
            for favorite in self._favorites
            if favorite.customer_id != customer_id
            or favorite.product_id != product_id
        ]

    async def set_admin(self, id: int) -> None:
        self._customers = [
            customer for customer in self._customers if customer.id == id
        ]
        self._customers[0].is_admin = True

    def _get_next_id(self) -> int:
        max_id = max((customer.id for customer in self._customers), default=0)
        return max_id + 1

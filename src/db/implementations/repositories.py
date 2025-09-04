from domain.customer import Customer

from ..base import CustomerRepository


class CustomerRepositoryImpl(CustomerRepository):
    def get_customer(
        *, email: str | None = None, id: int | None = None
    ) -> Customer: ...

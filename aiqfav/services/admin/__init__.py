import logging

from aiqfav.db.base import CustomerRepository
from aiqfav.domain.customer import CustomerCreate, CustomerPublic
from aiqfav.services.customer import CustomerService


class AdminService:
    def __init__(
        self,
        customer_service: CustomerService,
        customer_repo: CustomerRepository,
    ):
        self.customer_service = customer_service
        self.customer_repo = customer_repo

    async def create_admin(self, customer: CustomerCreate) -> CustomerPublic:
        """Create a new admin customer.

        Args:
            customer (CustomerCreate): the customer to create.

        Returns:
            CustomerPublic: the created customer.
        """
        logging.info('Creating admin customer %s', customer.email)

        customer_created = await self.customer_service.create_customer(
            customer
        )

        await self.customer_repo.set_admin(customer_created.id)
        return customer_created

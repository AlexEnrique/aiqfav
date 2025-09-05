import pytest
from faker import Faker

from aiqfav.db.base import CustomerRepository
from aiqfav.domain.customer import (
    CustomerCreate,
)
from aiqfav.services.admin import AdminService


@pytest.mark.asyncio
class TestAdminService:
    @pytest.fixture
    def customer_create(self, fake: Faker) -> CustomerCreate:
        return CustomerCreate(
            name=fake.name(),
            email=fake.email(),
            password=fake.password(),
        )

    async def test_create_admin(
        self,
        admin_service: AdminService,
        customer_create: CustomerCreate,
        customer_repo: CustomerRepository,
    ):
        customer = await admin_service.create_admin(customer_create)
        assert customer.id is not None

        customer_in_db = await customer_repo.get_customer(id=customer.id)
        assert customer_in_db.name == customer_create.name
        assert customer_in_db.email == customer_create.email
        assert customer_in_db.is_admin

import httpx
import pytest
from faker import Faker

from aiqfav.db.base import CustomerRepository
from aiqfav.domain.customer import (
    CustomerCreate,
    CustomerNotFound,
    CustomerWithPassword,
)
from aiqfav.services.customer import CustomerService
from aiqfav.services.customer.exceptions import EmailAlreadyExists
from tests._mocks.httpx import HttpxAsyncClientMock


@pytest.mark.asyncio
class TestCustomerService:
    @pytest.fixture
    def customer_with_password(self, fake: Faker) -> CustomerWithPassword:
        return CustomerWithPassword(
            name=fake.name(),
            email=fake.email(),
            hashed_password='$fake_hash$' + fake.password(),
        )

    @pytest.fixture
    def customer_create(self, fake: Faker) -> CustomerCreate:
        return CustomerCreate(
            name=fake.name(),
            email=fake.email(),
            password=fake.password(),
        )

    async def test_get_customer_by_id(
        self,
        customer_service: CustomerService,
        customer_with_password: CustomerWithPassword,
        customer_repo: CustomerRepository,
    ):
        customer_in_db = await customer_repo.create_customer(
            customer_with_password
        )
        customer = await customer_service.get_customer_by_id(customer_in_db.id)

        assert customer.id == customer_in_db.id
        assert customer.name == customer_in_db.name
        assert customer.email == customer_in_db.email

    async def test_get_customer_by_id_cache(
        self,
        customer_service: CustomerService,
        customer_with_password: CustomerWithPassword,
        customer_repo: CustomerRepository,
    ):
        customer_in_db = await customer_repo.create_customer(
            customer_with_password
        )
        customer = await customer_service.get_customer_by_id(customer_in_db.id)

        # Second call should hit the cache
        customer = await customer_service.get_customer_by_id(customer_in_db.id)

        assert customer.id == customer_in_db.id
        assert customer.name == customer_in_db.name
        assert customer.email == customer_in_db.email

    async def test_list_customers(
        self,
        customer_service: CustomerService,
        customer_with_password: CustomerWithPassword,
        customer_repo: CustomerRepository,
    ):
        customer_in_db = await customer_repo.create_customer(
            customer_with_password
        )
        customers = await customer_service.list_customers()
        assert len(customers) == 1
        assert customers[0].id == customer_in_db.id
        assert customers[0].name == customer_in_db.name
        assert customers[0].email == customer_in_db.email

    async def test_list_customers_cache(
        self,
        customer_service: CustomerService,
        customer_with_password: CustomerWithPassword,
        customer_repo: CustomerRepository,
    ):
        customer_in_db = await customer_repo.create_customer(
            customer_with_password
        )
        customers = await customer_service.list_customers()
        customers = await customer_service.list_customers()

        assert len(customers) == 1
        assert customers[0].id == customer_in_db.id
        assert customers[0].name == customer_in_db.name
        assert customers[0].email == customer_in_db.email

    async def test_create_customer(
        self,
        customer_service: CustomerService,
        customer_create: CustomerCreate,
        customer_repo: CustomerRepository,
    ):
        customer = await customer_service.create_customer(customer_create)
        assert customer.id is not None
        assert customer.name == customer_create.name
        assert customer.email == customer_create.email

        customer_in_db = await customer_repo.get_customer(id=customer.id)
        assert customer_in_db.hashed_password != customer_create.password

    async def test_create_customer_validates_existing_email(
        self,
        customer_service: CustomerService,
        customer_create: CustomerCreate,
        customer_repo: CustomerRepository,
    ):
        await customer_service.create_customer(customer_create)
        with pytest.raises(EmailAlreadyExists):
            await customer_service.create_customer(customer_create)

    async def test_delete_customer(
        self,
        customer_service: CustomerService,
        customer_with_password: CustomerWithPassword,
        customer_repo: CustomerRepository,
    ):
        customer = await customer_repo.create_customer(customer_with_password)
        await customer_service.delete_customer(customer.id)
        with pytest.raises(CustomerNotFound):
            await customer_service.get_customer_by_id(customer.id)

    async def test_check_is_admin(
        self,
        customer_service: CustomerService,
        customer_with_password: CustomerWithPassword,
        customer_repo: CustomerRepository,
    ):
        customer = await customer_repo.create_customer(customer_with_password)
        is_admin = await customer_service.check_is_admin(customer.id)
        assert not is_admin

        await customer_repo.set_admin(customer.id)
        is_admin = await customer_service.check_is_admin(customer.id)
        assert is_admin

    async def test_favorites_for_customer(
        self,
        customer_service: CustomerService,
        client_mock: HttpxAsyncClientMock,
        customer_with_password: CustomerWithPassword,
        customer_repo: CustomerRepository,
    ):
        client_mock.get.return_value = httpx.Response(
            status_code=200,
            json={
                'id': 1,
                'title': 'Product 1',
                'price': 100.0,
                'rating': {
                    'rate': 5.0,
                },
                'image': 'https://via.placeholder.com/150',
            },
        )

        customer = await customer_repo.create_customer(customer_with_password)
        favorites = await customer_service.list_favorites_for_customer(
            customer.id
        )
        assert len(favorites) == 0

        await customer_service.add_favorite(customer.id, 1)
        favorites = await customer_service.list_favorites_for_customer(
            customer.id
        )
        # Cache hit
        favorites = await customer_service.list_favorites_for_customer(
            customer.id
        )
        assert len(favorites) == 1
        assert favorites[0].id == 1

        await customer_service.remove_favorite(customer.id, 1)
        favorites = await customer_service.list_favorites_for_customer(
            customer.id
        )
        assert len(favorites) == 0

    async def test_check_email_valid(
        self,
        customer_with_password: CustomerWithPassword,
        customer_service: CustomerService,
        customer_repo: CustomerRepository,
    ):
        assert await customer_service.check_email_valid(
            customer_with_password.email
        )
        await customer_repo.create_customer(customer_with_password)
        assert not await customer_service.check_email_valid(
            customer_with_password.email
        )

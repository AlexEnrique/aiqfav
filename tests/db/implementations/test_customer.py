import pytest
from faker import Faker

from aiqfav.db.base import CustomerRepository
from aiqfav.domain.customer import CustomerNotFound, CustomerWithPassword


@pytest.mark.asyncio
class TestCustomerRepositoryImpl:
    @pytest.fixture
    def customer_with_password(self, fake: Faker):
        """Dados de exemplo para criar um cliente."""
        return CustomerWithPassword(
            name=fake.name(),
            email=fake.email(),
            hashed_password='$fake_hash$' + fake.password(),
        )

    async def test_create_customer(
        self,
        customer_repo_impl: CustomerRepository,
        customer_with_password: CustomerWithPassword,
    ):
        """Testa a criação de um cliente."""
        customer = await customer_repo_impl.create_customer(
            customer_with_password
        )

        assert customer.name == customer_with_password.name
        assert customer.email == customer_with_password.email
        assert (
            customer.hashed_password == customer_with_password.hashed_password
        )
        assert customer.id is not None
        assert customer.is_admin is False

    async def test_get_customer(
        self,
        customer_repo_impl: CustomerRepository,
        customer_with_password: CustomerWithPassword,
    ):
        """Testa a criação de um cliente."""
        customer = await customer_repo_impl.create_customer(
            customer_with_password
        )

        # Get by id
        customer = await customer_repo_impl.get_customer(id=customer.id)
        assert customer.name == customer_with_password.name
        assert customer.email == customer_with_password.email

        # Get by email
        customer = await customer_repo_impl.get_customer(email=customer.email)
        assert customer.name == customer_with_password.name
        assert customer.email == customer_with_password.email

    async def test_get_customer_not_found(
        self,
        customer_repo_impl: CustomerRepository,
        fake: Faker,
    ):
        """Testa a criação de um cliente."""
        # Get by id
        with pytest.raises(CustomerNotFound):
            await customer_repo_impl.get_customer(id=fake.random_int())

        # Get by email
        with pytest.raises(CustomerNotFound):
            await customer_repo_impl.get_customer(email=fake.email())

    async def test_list_customers(
        self,
        customer_repo_impl: CustomerRepository,
        customer_with_password: CustomerWithPassword,
    ):
        """Testa a criação de um cliente."""
        await customer_repo_impl.create_customer(customer_with_password)
        customers = await customer_repo_impl.list_customers()
        assert len(customers) == 1
        assert customers[0].name == customer_with_password.name
        assert customers[0].email == customer_with_password.email

    async def test_delete_customer(
        self,
        customer_repo_impl: CustomerRepository,
        customer_with_password: CustomerWithPassword,
    ):
        """Testa a criação de um cliente."""
        customer = await customer_repo_impl.create_customer(
            customer_with_password
        )

        await customer_repo_impl.delete_customer(customer.id)

        with pytest.raises(CustomerNotFound):
            await customer_repo_impl.get_customer(id=customer.id)

        with pytest.raises(CustomerNotFound):
            await customer_repo_impl.delete_customer(customer.id)

    async def test_set_admin(
        self,
        customer_repo_impl: CustomerRepository,
        customer_with_password: CustomerWithPassword,
    ):
        """Testa a criação de um cliente."""
        customer = await customer_repo_impl.create_customer(
            customer_with_password
        )
        await customer_repo_impl.set_admin(customer.id)
        customer = await customer_repo_impl.get_customer(id=customer.id)
        assert customer.is_admin

    async def test_favorites(
        self,
        customer_repo_impl: CustomerRepository,
        customer_with_password: CustomerWithPassword,
    ):
        """Testa a criação de um cliente."""
        customer = await customer_repo_impl.create_customer(
            customer_with_password
        )
        await customer_repo_impl.add_favorite(customer.id, 1)
        favorites = await customer_repo_impl.list_favorites_for_customer(
            customer.id
        )
        assert len(favorites) == 1
        assert favorites[0].product_id == 1

        await customer_repo_impl.remove_favorite(customer.id, 1)
        favorites = await customer_repo_impl.list_favorites_for_customer(
            customer.id
        )
        assert len(favorites) == 0

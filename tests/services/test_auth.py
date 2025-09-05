import pytest
from faker import Faker

from aiqfav.adapters.base import JwtAdapter
from aiqfav.db.base import CustomerRepository
from aiqfav.domain.customer import (
    CustomerCreate,
    CustomerInDb,
)
from aiqfav.services.auth import AuthService
from aiqfav.services.auth.exceptions import InvalidToken
from aiqfav.services.customer import CustomerService
from aiqfav.services.customer.exceptions import InvalidCredentials


@pytest.mark.asyncio
class TestAuthService:
    @pytest.fixture
    async def customer_and_password(
        self,
        fake: Faker,
        customer_service: CustomerService,
        customer_repo: CustomerRepository,
    ) -> tuple[CustomerInDb, str]:
        password = fake.password()
        customer = await customer_service.create_customer(
            CustomerCreate(
                name=fake.name(),
                email=fake.email(),
                password=password,
            )
        )
        customer_in_db = await customer_repo.get_customer(id=customer.id)
        return customer_in_db, password

    async def test_pair_tokens(
        self,
        auth_service: AuthService,
        customer_and_password: tuple[CustomerInDb, str],
        jwt_adapter: JwtAdapter,
    ):
        customer_in_db, password = customer_and_password
        access, refresh = await auth_service.pair_tokens(
            email=customer_in_db.email,
            password=password,
        )
        assert access is not None
        assert refresh is not None
        assert isinstance(access, str)
        assert isinstance(refresh, str)
        assert len(access) > 0
        assert len(refresh) > 0
        assert jwt_adapter.decode(access, audience=['access']) is not None
        assert jwt_adapter.decode(refresh, audience=['refresh']) is not None

    async def test_pair_tokens_invalid_email(
        self,
        auth_service: AuthService,
        fake: Faker,
    ):
        with pytest.raises(InvalidCredentials):
            await auth_service.pair_tokens(
                email=fake.email(),
                password=fake.password(),
            )

    async def test_pair_tokens_invalid_password(
        self,
        auth_service: AuthService,
        customer_and_password: tuple[CustomerInDb, str],
    ):
        customer_in_db, password = customer_and_password
        with pytest.raises(InvalidCredentials):
            await auth_service.pair_tokens(
                email=customer_in_db.email,
                password='invalid_password:' + password,
            )

    async def test_get_customer_id_from_token_and_refresh_token(
        self,
        auth_service: AuthService,
        customer_and_password: tuple[CustomerInDb, str],
        jwt_adapter: JwtAdapter,
    ):
        customer_in_db, password = customer_and_password
        access, refresh = await auth_service.pair_tokens(
            email=customer_in_db.email,
            password=password,
        )

        customer_id = auth_service.get_customer_id_from_token(
            access, token_type='access'
        )
        assert customer_id == customer_in_db.id

        new_access, new_refresh = auth_service.refresh_token(refresh)
        assert new_access is not None
        assert new_refresh is not None
        assert isinstance(new_access, str)
        assert isinstance(new_refresh, str)
        assert len(new_access) > 0
        assert len(new_refresh) > 0
        assert jwt_adapter.decode(new_access, audience=['access']) is not None
        assert (
            jwt_adapter.decode(new_refresh, audience=['refresh']) is not None
        )

    async def test_invalid_token(
        self,
        auth_service: AuthService,
        customer_and_password: tuple[CustomerInDb, str],
        jwt_adapter: JwtAdapter,
    ):
        customer_in_db, password = customer_and_password
        access, refresh = await auth_service.pair_tokens(
            email=customer_in_db.email,
            password=password,
        )
        with pytest.raises(InvalidToken):
            auth_service.get_customer_id_from_token(
                access, token_type='refresh'
            )

        with pytest.raises(InvalidToken):
            auth_service.get_customer_id_from_token(
                refresh, token_type='access'
            )

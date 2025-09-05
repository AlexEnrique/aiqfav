import pytest
from faker import Faker
from fastapi.testclient import TestClient

from aiqfav.db.base import CustomerRepository
from aiqfav.domain.customer import (
    CustomerCreate,
    CustomerPublic,
)
from aiqfav.services.auth import AuthService
from aiqfav.services.customer import CustomerService


@pytest.fixture
def http_client(override_env) -> TestClient:
    from aiqfav.api.app import create_app

    app = create_app()

    return TestClient(app)


@pytest.fixture
def password(fake: Faker) -> str:
    return fake.password()


@pytest.fixture
async def customer_non_admin(
    fake: Faker,
    password: str,
    customer_service_impl: CustomerService,
) -> CustomerPublic:
    return await customer_service_impl.create_customer(
        CustomerCreate(
            name=fake.name(),
            email=fake.email(),
            password=password,
        )
    )


@pytest.fixture
async def customer_admin(
    fake: Faker,
    password: str,
    customer_service_impl: CustomerService,
    customer_repo_impl: CustomerRepository,
) -> CustomerPublic:
    customer = await customer_service_impl.create_customer(
        CustomerCreate(
            name=fake.name(),
            email=fake.email(),
            password=password,
        )
    )
    await customer_repo_impl.set_admin(customer.id)
    return customer


@pytest.fixture
async def access_token_non_admin(
    password: str,
    customer_non_admin: CustomerPublic,
    auth_service_impl: AuthService,
) -> str:
    access_token, _ = await auth_service_impl.pair_tokens(
        email=customer_non_admin.email,
        password=password,
    )
    return access_token


@pytest.fixture
async def access_token_admin(
    password: str,
    customer_admin: CustomerPublic,
    auth_service_impl: AuthService,
) -> str:
    access_token, _ = await auth_service_impl.pair_tokens(
        email=customer_admin.email,
        password=password,
    )
    return access_token

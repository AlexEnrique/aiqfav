import pytest
from fastapi.testclient import TestClient

from aiqfav.domain.customer import CustomerPublic


@pytest.mark.asyncio
class TestCustomersEndpoints:
    async def test_list_customers_requires_token(
        self, http_client: TestClient
    ):
        response = http_client.get('/v1/customers')
        assert response.status_code == 401

    async def test_list_customers_requires_admin_token(
        self,
        http_client: TestClient,
        access_token_non_admin: str,
    ):
        response = http_client.get(
            '/v1/customers',
            headers={'Authorization': f'Bearer {access_token_non_admin}'},
        )
        assert response.status_code == 403

    @pytest.mark.skip(
        reason=(
            'Problema com as envs sendo lidas antes de serem sobrescritas '
            'pelo monkeypatch, fazendo com que o banco de dados utilizado '
            'seja o de desenvolvimento, não o de teste'
        )
    )
    async def test_list_customers_with_admin_token(
        self,
        http_client: TestClient,
        customer_admin: CustomerPublic,
        access_token_admin: str,
    ):
        response = http_client.get(
            '/v1/customers',
            headers={'Authorization': f'Bearer {access_token_admin}'},
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]['id'] == customer_admin.id
        assert response.json()[0]['name'] == customer_admin.name
        assert response.json()[0]['email'] == customer_admin.email

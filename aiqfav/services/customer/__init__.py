from passlib.context import CryptContext

from aiqfav.db.base import CustomerRepository
from aiqfav.domain.customer import (
    CustomerCreate,
    CustomerNotFound,
    CustomerPublic,
    CustomerWithPassword,
)

from .exceptions import EmailAlreadyExists, InvalidCredentials


class CustomerService:
    def __init__(
        self, customer_repo: CustomerRepository, pwd_context: CryptContext
    ):
        self.customer_repo = customer_repo
        self.pwd_context = pwd_context

    async def get_customer_by_id(self, id: int) -> CustomerPublic:
        customer_in_db = await self.customer_repo.get_customer(id=id)
        return CustomerPublic.model_validate(customer_in_db)

    async def list_customers(self) -> list[CustomerPublic]:
        customers_in_db = await self.customer_repo.list_customers()
        return [
            CustomerPublic.model_validate(customer)
            for customer in customers_in_db
        ]

    async def create_customer(
        self, customer: CustomerCreate
    ) -> CustomerPublic:
        try:
            customer_in_db = await self.customer_repo.get_customer(
                email=customer.email
            )
        except CustomerNotFound:
            pass
        else:
            raise EmailAlreadyExists('Já existe um cliente com este e-mail')

        hashed_password = self.pwd_context.hash(customer.password)
        customer_with_password = CustomerWithPassword(
            name=customer.name,
            email=customer.email,
            hashed_password=hashed_password,
        )
        customer_in_db = await self.customer_repo.create_customer(
            customer_with_password
        )
        return CustomerPublic.model_validate(customer_in_db)

    async def authenticate_customer(
        self, email: str, password: str
    ) -> CustomerPublic:
        invalid_credentials_exception = InvalidCredentials(
            'E-mail ou senha incorretos'
        )

        try:
            customer = await self.customer_repo.get_customer(email=email)
        except CustomerNotFound:
            raise invalid_credentials_exception

        if not self.pwd_context.verify(password, customer.hashed_password):
            raise invalid_credentials_exception

        return customer

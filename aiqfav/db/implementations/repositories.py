from aiqfav.domain.customer import Customer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ..base import CustomerRepository
from .models import Customer as CustomerModel


class CustomerRepositoryImpl(CustomerRepository):
    def __init__(
        self,
        async_session: async_sessionmaker[AsyncSession]
    ):
        self.async_session = async_session


    async def get_customer(
        *, email: str | None = None, id: int | None = None
    ) -> Customer: ...

    async def list_customers(self) -> list[Customer]:
        async with self.async_session() as session:
            stmt = select(CustomerModel)
            result = await session.execute(stmt)
            customers_in_db = result.scalars().all()
            return [Customer.model_validate(customer) for customer in customers_in_db]

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from aiqfav.domain.customer import (
    CustomerInDb,
    CustomerWithPassword,
)

from ..base import CustomerRepository
from .models import Customer as CustomerModel


class CustomerRepositoryImpl(CustomerRepository):
    def __init__(self, async_session: async_sessionmaker[AsyncSession]):
        self.async_session = async_session

    async def get_customer(
        self, *, email: str | None = None, id: int | None = None
    ) -> CustomerInDb:
        async with self.async_session() as session:
            stmt = select(CustomerModel)
            if email:
                stmt = stmt.where(CustomerModel.email == email)
            elif id:
                stmt = stmt.where(CustomerModel.id == id)
            result = await session.execute(stmt)
            customer = result.scalar_one_or_none()
            return CustomerInDb.model_validate(customer)

    async def list_customers(self) -> list[CustomerInDb]:
        async with self.async_session() as session:
            stmt = select(CustomerModel)
            result = await session.execute(stmt)
            customers_in_db = result.scalars().all()
            return [
                CustomerInDb.model_validate(customer)
                for customer in customers_in_db
            ]

    async def create_customer(
        self, customer: CustomerWithPassword
    ) -> CustomerInDb:
        async with self.async_session() as session:
            custmer_in_db = CustomerModel(**customer.model_dump())
            session.add(custmer_in_db)
            await session.commit()
            await session.refresh(custmer_in_db)
            return CustomerInDb.model_validate(custmer_in_db)

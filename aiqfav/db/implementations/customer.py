from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from aiqfav.domain.customer import (
    CustomerInDb,
    CustomerNotFound,
    CustomerWithPassword,
)
from aiqfav.domain.favorite import FavoriteInDb

from ..base import CustomerRepository
from .models import Customer as CustomerModel
from .models import Favorite as FavoriteModel


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

            if not customer:
                raise CustomerNotFound(f'Customer with id {id} not found')

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

    async def delete_customer(self, id: int) -> None:
        async with self.async_session() as session:
            customer_in_db = await session.get(CustomerModel, id)
            if not customer_in_db:
                raise CustomerNotFound(f'Customer with id {id} not found')

            stmt = delete(CustomerModel).where(CustomerModel.id == id)
            await session.execute(stmt)
            await session.commit()

    async def list_favorites_for_customer(
        self, customer_id: int
    ) -> list[FavoriteInDb]:
        async with self.async_session() as session:
            stmt = select(FavoriteModel).where(
                FavoriteModel.customer_id == customer_id
            )
            result = await session.execute(stmt)
            favorites_in_db = result.scalars().all()
            return [
                FavoriteInDb.model_validate(favorite)
                for favorite in favorites_in_db
            ]

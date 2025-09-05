from __future__ import annotations

from sqlalchemy import BigInteger, Boolean, ForeignKey, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = 'customer'

    id: Mapped[int] = mapped_column(
        BigInteger(), primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    is_admin: Mapped[bool] = mapped_column(Boolean(), default=False)
    hashed_password: Mapped[str] = mapped_column(String(255))

    favorites: Mapped[list[Favorite]] = relationship(
        back_populates='customer', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'Customer(id={self.id!r}, name={self.name!r}, email={self.email!r})'


class Favorite(Base):
    __tablename__ = 'favorite'

    customer_id: Mapped[int] = mapped_column(
        ForeignKey('customer.id', ondelete='CASCADE'),
        primary_key=True,
        index=True,
    )
    product_id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)

    customer: Mapped[Customer] = relationship(back_populates='favorites')

    def __repr__(self):
        return f'Favorite(customer_id={self.customer_id!r}, product_id={self.product_id!r})'

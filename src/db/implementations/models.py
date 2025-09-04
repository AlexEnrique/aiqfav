from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = 'customer'

    id: Mapped[int] = mapped_column(
        BigInteger(), primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(128))

    favorites: Mapped[list[Favorite]] = relationship(
        back_populates='customer', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'Customer(id={self.id!r}, name={self.name!r}, email={self.email!r})'


class Favorite(Base):
    __tablename__ = 'favorite'

    customer_id: Mapped[int] = mapped_column(
        ForeignKey('customer.id'), primary_key=True
    )
    product_id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)

    customer: Mapped[Customer] = relationship(back_populates='favorites')

    def __repr__(self):
        return f'Favorite(customer_id={self.customer_id!r}, product_id={self.product_id!r})'

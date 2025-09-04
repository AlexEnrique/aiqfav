from pydantic import BaseModel, Field, ConfigDict

from .favorite import Favorite


### Models
class CustomerBase(BaseModel):
    """Modelo base para um cliente"""
    name: str = Field(description='Nome do cliente', max_length=255)
    email: str = Field(description='E-mail do cliente', max_length=255)


class CustomerCreate(CustomerBase):
    """Modelo para criação de um cliente"""
    password: str = Field(description='Senha do cliente')


class Customer(CustomerBase):
    """Modelo para um cliente"""
    id: int = Field(description='ID do cliente', gt=0)

    model_config = ConfigDict(from_attributes=True)


class CustomerWithFavorites(CustomerBase):
    """Modelo para um cliente"""
    id: int = Field(description='ID do cliente', gt=0)
    favorites: list[Favorite] = Field(
        default_factory=list,
        description='Lista de produtos favoritos do cliente',
    )

    model_config = ConfigDict(from_attributes=True)


### Exceptions
class CustomerBaseException(Exception):
    """Base Exception related to customers"""


class CustomerNotFound(CustomerBaseException):
    """Exception when a customer is not found."""

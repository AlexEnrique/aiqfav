from pydantic import BaseModel, Field

from .favorite import Favorite


### Models
class Customer(BaseModel):
    id: int = Field(description='ID do cliente', gt=0)
    name: str = Field(description='Nome do cliente', max_length=255)
    email: str = Field(description='E-mail do cliente', max_length=255)
    favorites: list[Favorite] = Field(
        default_factory=list,
        description='Lista de produtos favoritos do cliente',
    )


### Exceptions
class CustomerBaseException(Exception):
    """Base Exception related to customers"""


class CustomerNotFound(CustomerBaseException):
    """Exception when a customer is not found."""

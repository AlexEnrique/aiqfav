from pydantic import BaseModel, ConfigDict, Field

from .favorite import Favorite


### Models
class CustomerBase(BaseModel):
    """Modelo base para um cliente"""

    name: str = Field(description='Nome do cliente', max_length=255)
    email: str = Field(description='E-mail do cliente', max_length=255)

    model_config = ConfigDict(from_attributes=True)


class CustomerCreate(CustomerBase):
    """Modelo para criação de um cliente"""

    password: str = Field(
        description='Senha do cliente (plana) - Não deve ser salvo no banco de dados, use CustomerWithPassword para salvar a senha hasheada'
    )


class CustomerPublic(CustomerBase):
    """Modelo para um cliente"""

    id: int = Field(description='ID do cliente', gt=0)


class CustomerWithFavorites(CustomerBase):
    """Modelo para um cliente"""

    id: int = Field(description='ID do cliente', gt=0)
    favorites: list[Favorite] = Field(
        default_factory=list,
        description='Lista de produtos favoritos do cliente',
    )


class CustomerWithPassword(CustomerBase):
    """Modelo para um cliente com senha"""

    hashed_password: str = Field(description='Hash da senha do cliente')


class CustomerInDb(CustomerPublic, CustomerWithPassword):
    """Modelo para um cliente no banco de dados"""


### Exceptions
class CustomerBaseException(Exception):
    """Base Exception related to customers"""


class CustomerNotFound(CustomerBaseException):
    """Exception when a customer is not found."""

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from aiqfav.utils.pydantic.types import Password

from .favorite import FavoriteInDb


### Models
class CustomerBase(BaseModel):
    """Modelo base para um cliente"""

    name: str = Field(description='Nome do cliente', max_length=255)
    email: str = Field(description='E-mail do cliente', max_length=255)

    model_config = ConfigDict(from_attributes=True)


class CustomerCreate(CustomerBase):
    """Modelo para criação de um cliente"""

    password: Password = Field(
        description=(
            'Senha do cliente (plana) - Não deve ser salvo no banco de '
            'dados, use CustomerWithPassword para salvar a senha hasheada. '
            'Deve conter pelo menos 8 caracteres, uma letra maiúscula, uma '
            'letra minúscula, um número e um símbolo especial.'
        )
    )


class CustomerPublic(CustomerBase):
    """Modelo para um cliente"""

    id: int = Field(description='ID do cliente', gt=0)


class CustomerWithFavorites(CustomerBase):
    """Modelo para um cliente"""

    id: int = Field(description='ID do cliente', gt=0)
    favorites: list[FavoriteInDb] = Field(
        default_factory=list,
        description='Lista de produtos favoritos do cliente',
    )


class CustomerWithPassword(CustomerBase):
    """Modelo para um cliente com senha"""

    hashed_password: str = Field(description='Hash da senha do cliente')


class CustomerInDb(CustomerBase):
    """Modelo para um cliente no banco de dados"""

    id: int = Field(description='ID do cliente', gt=0)
    is_admin: bool = Field(
        description='Se o cliente é administrador', default=False
    )
    hashed_password: str = Field(description='Hash da senha do cliente')


class EmailExistsResponse(BaseModel):
    """Modelo para a resposta de validação de e-mail"""

    email: str = Field(description='E-mail a ser validado')
    valid: bool = Field(
        description=(
            'Se o e-mail é válido, ou seja, se não existe um cliente '
            'com este e-mail'
        )
    )


### Exceptions
class CustomerBaseException(Exception):
    """Base Exception related to customers"""


class CustomerNotFound(CustomerBaseException):
    """Exception when a customer is not found."""


### Type Adapters
CustomerListAdapter = TypeAdapter(list[CustomerPublic])

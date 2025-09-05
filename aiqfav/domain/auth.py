from pydantic import BaseModel, Field

from aiqfav.utils.pydantic.types import Password


class AuthPairTokensRequest(BaseModel):
    email: str = Field(description='E-mail do cliente')
    password: Password = Field(description='Senha do cliente')


class AuthPairTokensResponse(BaseModel):
    access_token: str = Field(description='Token de acesso')
    refresh_token: str = Field(description='Token de refresh')

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from aiqfav.api.dependencies import get_auth_service
from aiqfav.domain.auth import (
    AuthPairTokensRequest,
    AuthPairTokensResponse,
    AuthRefreshTokenRequest,
)
from aiqfav.services.auth import AuthService, InvalidToken
from aiqfav.services.customer.exceptions import InvalidCredentials
from aiqfav.utils.api_errors import ErrorCodes, get_error_response

__all__ = ['router']

router = APIRouter(tags=['auth'])


@router.post(
    '/auth/pair',
    summary='Obter um par de tokens de acesso e refresh',
    description='Endpoint para obter um par de tokens de acesso e refresh',
    response_model=AuthPairTokensResponse,
)
async def pair_tokens(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    data: AuthPairTokensRequest,
):
    try:
        access_token, refresh_token = await auth_service.pair_tokens(
            data.email, data.password
        )
        return AuthPairTokensResponse(
            access_token=access_token, refresh_token=refresh_token
        )
    except InvalidCredentials:
        raise HTTPException(
            status_code=401,
            detail=get_error_response(
                error_code=ErrorCodes.INVALID_CREDENTIALS,
                message='E-mail ou senha incorretos',
            ),
        )


@router.post(
    '/auth/refresh',
    summary='Atualizar token de acesso',
    description='Endpoint para atualizar o token de acesso',
    response_model=AuthPairTokensResponse,
)
async def refresh_token(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    data: AuthRefreshTokenRequest,
):
    try:
        access_token, refresh_token = auth_service.refresh_token(
            data.refresh_token
        )
        return AuthPairTokensResponse(
            access_token=access_token, refresh_token=refresh_token
        )
    except InvalidToken:
        raise HTTPException(
            status_code=401,
            detail=get_error_response(
                error_code=ErrorCodes.INVALID_TOKEN,
                message='Token inválido ou expirado',
            ),
        )

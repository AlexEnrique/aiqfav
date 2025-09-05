from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, Response

from aiqfav.adapters.exceptions import StoreApiNotFoundError
from aiqfav.api.dependencies import get_current_customer, get_customer_service
from aiqfav.domain.customer import (
    CustomerCreate,
    CustomerNotFound,
    CustomerPublic,
)
from aiqfav.domain.favorite import FavoriteUpsert
from aiqfav.domain.product import ProductPublic
from aiqfav.services.customer import CustomerService
from aiqfav.services.customer.exceptions import EmailAlreadyExists
from aiqfav.utils.api_errors import ErrorCodes, get_error_response

__all__ = ['router']

router = APIRouter(tags=['customers'])


@router.get(
    '/customers',
    response_model=list[CustomerPublic],
    summary='Listar clientes',
    description='Endpoint para listar todos os clientes',
)
async def list_customers(
    customer_service: Annotated[
        CustomerService, Depends(get_customer_service)
    ],
):
    return await customer_service.list_customers()


@router.get(
    '/customers/me',
    response_model=CustomerPublic,
    summary='Buscar cliente por ID',
    description='Endpoint para buscar um cliente por ID',
)
async def get_me(
    customer: Annotated[CustomerPublic, Depends(get_current_customer)],
):
    """Endpoint para buscar o cliente autenticado"""
    return customer


@router.get(
    '/customers/{customer_id}',
    response_model=CustomerPublic,
    summary='Buscar cliente por ID',
    description='Endpoint para buscar um cliente por ID',
)
async def get_customer(
    customer_service: Annotated[
        CustomerService, Depends(get_customer_service)
    ],
    customer_id: int,
):
    """Endpoint para buscar um cliente por ID"""
    try:
        return await customer_service.get_customer_by_id(customer_id)
    except CustomerNotFound:
        raise HTTPException(
            status_code=404,
            detail=get_error_response(
                error_code=ErrorCodes.CUSTOMER_NOT_FOUND,
                message='Cliente não encontrado',
            ),
        )


@router.post(
    '/customers',
    response_model=CustomerPublic,
    status_code=201,
    summary='Criar cliente',
    description='Endpoint para criar um novo cliente',
)
async def create_customer(
    customer_service: Annotated[
        CustomerService, Depends(get_customer_service)
    ],
    customer: CustomerCreate,
):
    """Endpoint para criar um novo cliente"""
    try:
        customer_created = await customer_service.create_customer(customer)
        print(type(customer_created))
        return JSONResponse(
            status_code=201, content=customer_created.model_dump()
        )
    except EmailAlreadyExists:
        raise HTTPException(
            status_code=409,
            detail=get_error_response(
                error_code=ErrorCodes.EMAIL_ALREADY_EXISTS,
                message='Já existe um cliente com este e-mail',
            ),
        )


@router.delete(
    '/customers/{customer_id}',
    response_class=Response,
    summary='Deletar cliente',
    description='Endpoint para deletar um cliente',
)
async def delete_customer(
    customer_service: Annotated[
        CustomerService, Depends(get_customer_service)
    ],
    customer_id: int,
):
    """Endpoint para deletar um cliente"""
    try:
        await customer_service.delete_customer(customer_id)
        return Response(status_code=204)
    except CustomerNotFound:
        raise HTTPException(
            status_code=404,
            detail=get_error_response(
                error_code=ErrorCodes.CUSTOMER_NOT_FOUND,
                message='Cliente não encontrado',
            ),
        )


@router.get(
    '/customers/me/favorites',
    response_model=list[ProductPublic],
    summary='Listar produtos favoritos do cliente autenticado',
    description='Endpoint para listar todos os produtos favoritos do cliente autenticado',
)
async def list_favorites_me(
    customer_service: Annotated[
        CustomerService, Depends(get_customer_service)
    ],
    customer: Annotated[CustomerPublic, Depends(get_current_customer)],
):
    try:
        return await customer_service.list_favorites_for_customer(customer.id)
    except CustomerNotFound:
        raise HTTPException(
            status_code=404,
            detail=get_error_response(
                error_code=ErrorCodes.CUSTOMER_NOT_FOUND,
                message='Cliente não encontrado',
            ),
        )


@router.put(
    '/customers/me/favorites',
    summary='Adicionar produto favorito do cliente autenticado',
    response_model=ProductPublic,
    responses={
        200: {
            'description': 'Produto favorito adicionado com sucesso',
        },
        404: {
            'description': 'Cliente não encontrado',
        },
    },
    description=(
        'Endpoint para adicionar um produto aos favoritos do cliente autenticado. Este '
        'endpoint é idempotente, podendo ser chamado várias vezes com o '
        'mesmo payload, sem causar erros. Retorna 200 em caso de sucesso, '
        'contendo o produto adicionado.'
    ),
)
async def add_favorite_me(
    customer_service: Annotated[
        CustomerService, Depends(get_customer_service)
    ],
    customer: Annotated[CustomerPublic, Depends(get_current_customer)],
    payload: FavoriteUpsert,
):
    try:
        return await customer_service.add_favorite(
            customer.id, payload.product_id
        )
    except CustomerNotFound:
        raise HTTPException(
            status_code=404,
            detail=get_error_response(
                error_code=ErrorCodes.CUSTOMER_NOT_FOUND,
                message='Cliente não encontrado',
            ),
        )
    except StoreApiNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=get_error_response(
                error_code=ErrorCodes.PRODUCT_NOT_FOUND,
                message='Produto não encontrado',
            ),
        )


@router.delete(
    '/customers/me/favorites/{product_id}',
    summary='Remover produto dos favoritos do cliente autenticado',
    response_class=Response,
    status_code=204,
    responses={
        204: {
            'description': 'Produto favorito removido com sucesso',
        },
        404: {
            'description': 'Cliente não encontrado',
        },
    },
    description=(
        'Endpoint para remover um produto dos favoritos do cliente autenticado. '
        'Retorna 204 em caso de sucesso.'
    ),
)
async def remove_favorite_me(
    customer_service: Annotated[
        CustomerService, Depends(get_customer_service)
    ],
    customer: Annotated[CustomerPublic, Depends(get_current_customer)],
    product_id: int,
):
    try:
        await customer_service.remove_favorite(customer.id, product_id)
        return Response(status_code=204)
    except CustomerNotFound:
        raise HTTPException(
            status_code=404,
            detail=get_error_response(
                error_code=ErrorCodes.CUSTOMER_NOT_FOUND,
                message='Cliente não encontrado',
            ),
        )


@router.get(
    '/customers/{customer_id}/favorites',
    response_model=list[ProductPublic],
    summary='Listar produtos favoritos',
    description='Endpoint para listar todos os produtos favoritos de um cliente',
)
async def list_favorites(
    customer_service: Annotated[
        CustomerService, Depends(get_customer_service)
    ],
    customer_id: int,
):
    try:
        return await customer_service.list_favorites_for_customer(customer_id)
    except CustomerNotFound:
        raise HTTPException(
            status_code=404,
            detail=get_error_response(
                error_code=ErrorCodes.CUSTOMER_NOT_FOUND,
                message='Cliente não encontrado',
            ),
        )


@router.put(
    '/customers/{customer_id}/favorites',
    summary='Adicionar produto favorito',
    response_model=ProductPublic,
    responses={
        200: {
            'description': 'Produto favorito adicionado com sucesso',
        },
        404: {
            'description': 'Cliente não encontrado',
        },
    },
    description=(
        'Endpoint para adicionar um produto aos favoritos de um cliente. Este '
        'endpoint é idempotente, podendo ser chamado várias vezes com o '
        'mesmo payload, sem causar erros. Retorna 200 em caso de sucesso, '
        'contendo o produto adicionado.'
    ),
)
async def add_favorite(
    customer_service: Annotated[
        CustomerService, Depends(get_customer_service)
    ],
    customer_id: int,
    payload: FavoriteUpsert,
):
    try:
        return await customer_service.add_favorite(
            customer_id, payload.product_id
        )
    except CustomerNotFound:
        raise HTTPException(
            status_code=404,
            detail=get_error_response(
                error_code=ErrorCodes.CUSTOMER_NOT_FOUND,
                message='Cliente não encontrado',
            ),
        )
    except StoreApiNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=get_error_response(
                error_code=ErrorCodes.PRODUCT_NOT_FOUND,
                message='Produto não encontrado',
            ),
        )


@router.delete(
    '/customers/{customer_id}/favorites/{product_id}',
    summary='Remover produto dos favoritos',
    response_class=Response,
    status_code=204,
    responses={
        204: {
            'description': 'Produto favorito removido com sucesso',
        },
        404: {
            'description': 'Cliente não encontrado',
        },
    },
    description=(
        'Endpoint para remover um produto dos favoritos de um cliente. '
        'Retorna 204 em caso de sucesso.'
    ),
)
async def remove_favorite(
    customer_service: Annotated[
        CustomerService, Depends(get_customer_service)
    ],
    customer_id: int,
    product_id: int,
):
    try:
        await customer_service.remove_favorite(customer_id, product_id)
        return Response(status_code=204)
    except CustomerNotFound:
        raise HTTPException(
            status_code=404,
            detail=get_error_response(
                error_code=ErrorCodes.CUSTOMER_NOT_FOUND,
                message='Cliente não encontrado',
            ),
        )

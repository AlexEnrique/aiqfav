from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from aiqfav.api.dependencies import get_customer_service
from aiqfav.domain.customer import CustomerCreate
from aiqfav.services.customer import CustomerService
from aiqfav.services.customer.exceptions import EmailAlreadyExists
from aiqfav.utils.api_errors import ErrorCodes, get_error_response

router = APIRouter()


@router.get('/customers')
async def list_customers(
    customer_service: Annotated[
        CustomerService, Depends(get_customer_service)
    ],
):
    """Endpoint para listar todos os clientes"""
    return await customer_service.list_customers()


@router.post('/customers')
async def create_customer(
    customer_service: Annotated[
        CustomerService, Depends(get_customer_service)
    ],
    customer: CustomerCreate,
):
    """Endpoint para criar um novo cliente"""
    try:
        return await customer_service.create_customer(customer)
    except EmailAlreadyExists:
        raise HTTPException(
            status_code=409,
            detail=get_error_response(
                error_code=ErrorCodes.EMAIL_ALREADY_EXISTS,
                message='Já existe um cliente com este e-mail',
            ),
        )

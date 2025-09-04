from enum import StrEnum

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    type: str
    message: str


class ErrorCodes(StrEnum):
    EMAIL_ALREADY_EXISTS = 'email_already_exists'
    CUSTOMER_NOT_FOUND = 'customer_not_found'


def get_error_response(
    *, error_code: ErrorCodes, message: str
) -> dict[str, str]:
    return ErrorResponse(type=error_code.value, message=message).model_dump()

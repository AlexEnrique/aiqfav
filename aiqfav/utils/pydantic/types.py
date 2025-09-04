import re
from typing import Annotated

from pydantic import AfterValidator, Field
from pydantic_core import PydanticCustomError

__all__ = ['Password']


def validate_password(value: str) -> str:
    if not re.match(
        r'(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&\-_])[A-Za-z\d@$!%*?&\-_]{8,}',
        value,
    ):
        raise PydanticCustomError(
            'password_validation_error',
            'A senha deve conter pelo menos 8 caracteres, uma letra maiúscula, uma letra minúscula, um número e um símbolo especial.',
        )
    return value


Password = Annotated[
    str,
    Field(min_length=8),
    AfterValidator(validate_password),
]

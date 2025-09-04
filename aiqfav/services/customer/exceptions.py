class CustomerServiceException(Exception):
    """Exeção geral para operações de serviço de cliente."""


class EmailAlreadyExists(CustomerServiceException):
    """Exeção quando um e-mail já existe."""


class InvalidCredentials(CustomerServiceException):
    """Exeção quando as credenciais de um cliente são inválidas."""

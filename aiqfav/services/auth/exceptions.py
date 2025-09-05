class AuthServiceException(Exception):
    """Base exception for AuthService"""


class InvalidToken(AuthServiceException):
    """Exeção quando um token é inválido."""

from src.utils.exceptions import AuthenticationError


class NotAuthenticatedError(AuthenticationError):
    def __str__(self):
        return 'Token invalid or expired.'

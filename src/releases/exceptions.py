from src.utils.exceptions import NotFoundError


class ReleaseNotFoundError(NotFoundError):
    def __str__(self):
        return 'Release not found.'

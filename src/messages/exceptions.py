from src.utils.exceptions import NotFoundError


class ReadMessageDenied(PermissionError):
    def __str__(self):
        return 'Author is not permitted to read messages.'


class InsertMessageDenied(PermissionError):
    def __str__(self):
        return 'Author is not permitted to insert messages.'


class DeleteMessageDenied(PermissionError):
    def __str__(self):
        return 'Author is not permitted to delete messages.'


class MessageNotFoundError(NotFoundError):
    def __str__(self):
        return 'Message not found.'

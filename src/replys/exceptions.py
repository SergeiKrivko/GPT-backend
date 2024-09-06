from src.utils.exceptions import NotFoundError


class ReadReplyDenied(PermissionError):
    def __str__(self):
        return 'Author is not permitted to read replys.'


class InsertReplyDenied(PermissionError):
    def __str__(self):
        return 'Author is not permitted to insert replys.'


class DeleteReplyDenied(PermissionError):
    def __str__(self):
        return 'Author is not permitted to delete replys.'


class ReplyNotFoundError(NotFoundError):
    def __str__(self):
        return 'Reply not found.'

from src.utils.exceptions import NotFoundError


class ReadChatDenied(PermissionError):
    def __str__(self):
        return 'Author is not permitted to read this chat.'


class InsertChatDenied(PermissionError):
    def __str__(self):
        return 'Author is not permitted to insert chats.'


class DeleteChatDenied(PermissionError):
    def __str__(self):
        return 'Author is not permitted to delete this chat.'


class UpdateChatDenied(PermissionError):
    def __str__(self):
        return 'Author is not permitted to update this chat.'


class ChatNotFoundError(NotFoundError):
    def __str__(self):
        return 'Chat not found.'

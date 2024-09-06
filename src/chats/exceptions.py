from src.utils.exceptions import NotFoundError


class ReadChatDenied(PermissionError):
    def __str__(self):
        return 'Author is not permitted to read chats.'


class InsertChatDenied(PermissionError):
    def __str__(self):
        return 'Author is not permitted to insert chats.'


class DeleteChatDenied(PermissionError):
    def __str__(self):
        return 'Author is not permitted to delete chats.'


class ChatNotFoundError(NotFoundError):
    def __str__(self):
        return 'Chat not found.'

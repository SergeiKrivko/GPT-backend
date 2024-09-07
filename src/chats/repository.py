from src.utils.repository import TimeStampRepository
from src.chats.models import Chat


class ChatRepository(TimeStampRepository):
    model = Chat

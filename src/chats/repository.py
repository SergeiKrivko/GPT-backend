from src.utils.repository import SQLAlchemyRepository
from src.chats.models import Chat


class ChatRepository(SQLAlchemyRepository):
    model = Chat

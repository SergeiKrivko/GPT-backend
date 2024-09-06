from src.utils.repository import SQLAlchemyRepository
from src.messages.models import Message


class MessageRepository(SQLAlchemyRepository):
    model = Message

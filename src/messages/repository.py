from src.utils.repository import SQLAlchemyRepository, TimeStampRepository
from src.messages.models import Message


class MessageRepository(TimeStampRepository):
    model = Message

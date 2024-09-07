from sqlalchemy import Column, Uuid, String, Integer, Float, ForeignKey, TIMESTAMP

from src.chats.models import Chat
from src.utils.models import IModel


class Message(IModel):
    __tablename__ = 'message'

    uuid = Column(Uuid, primary_key=True, nullable=False)
    chat_uuid = Column(ForeignKey(Chat.uuid), nullable=False, index=True)
    created_at = Column(TIMESTAMP, nullable=False)
    deleted_at = Column(TIMESTAMP, nullable=True)
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)
    model = Column(String, nullable=True)
    temperature = Column(Float, nullable=False)

    def dict(self):
        return {
            'uuid': self.uuid,
            'chat_uuid': self.chat_uuid,
            'created_at': self.created_at,
            'deleted_at': self.deleted_at,
            'role': self.role,
            'content': self.content,
            'model': self.model,
            'temperature': self.temperature,
        }

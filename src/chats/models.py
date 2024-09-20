from sqlalchemy import Column, Uuid, String, Integer, Float, ForeignKey, TIMESTAMP, Boolean

from src.utils.models import IModel


class Chat(IModel):
    __tablename__ = 'chat'

    uuid = Column(Uuid, primary_key=True, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    deleted_at = Column(TIMESTAMP, nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    name = Column(String, nullable=False)
    model = Column(String, nullable=True)
    context_size = Column(Integer, nullable=False)
    temperature = Column(Float, nullable=False)
    pinned = Column(Boolean, nullable=False)
    archived = Column(Boolean, nullable=False)
    color = Column(Integer, nullable=True)
    user = Column(String, nullable=False)

    def dict(self):
        return {
            'uuid': self.uuid,
            'created_at': self.created_at,
            'deleted_at': self.deleted_at,
            'updated_at': self.updated_at,
            'name': self.name,
            'model': self.model,
            'context_size': self.context_size,
            'temperature': self.temperature,
            'pinned': self.pinned,
            'archived': self.archived,
            'color': self.color,
            'user': self.user
        }

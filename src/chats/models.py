from sqlalchemy import Column, Uuid, String, Integer, Float, ForeignKey, TIMESTAMP

from src.utils.models import IModel


class Chat(IModel):
    __tablename__ = 'chat'

    uuid = Column(Uuid, primary_key=True, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    deleted_at = Column(TIMESTAMP, nullable=True)
    name = Column(String, nullable=False)
    model = Column(String, nullable=True)
    context_size = Column(Integer, nullable=False)
    temperature = Column(Float, nullable=False)
    user = Column(String, nullable=False)

    def dict(self):
        return {
            'uuid': self.uuid,
            'created_at': self.created_at,
            'deleted_at': self.deleted_at,
            'name': self.name,
            'model': self.model,
            'context_size': self.context_size,
            'temperature': self.temperature,
            'user': self.user
        }

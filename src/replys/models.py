from sqlalchemy import Column, Uuid, String, ForeignKey

from src.messages.models import Message
from src.utils.models import IModel


class Reply(IModel):
    __tablename__ = 'reply'

    uuid = Column(Uuid, primary_key=True, nullable=False)
    from_uuid = Column(ForeignKey(Message.uuid), nullable=False)
    to_uuid = Column(ForeignKey(Message.uuid), nullable=False)
    type = Column(String, nullable=False)

    def dict(self):
        return {
            'uuid': self.uuid,
            'from_uuid': self.from_uuid,
            'to_uuid': self.to_uuid,
            'type': self.type,
        }

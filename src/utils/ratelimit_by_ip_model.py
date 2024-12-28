import uuid
from datetime import datetime

from sqlalchemy import Column, Uuid, String, TIMESTAMP

from src.utils.models import IModel


class RatelimitLog(IModel):
    __tablename__ = "ratelimit_log"

    uuid = Column(Uuid, primary_key=True, default=uuid.uuid4)
    ip_address = Column(String, index=True, nullable=False)
    timestamp = Column(TIMESTAMP, default=lambda: datetime.now(tz=None), nullable=False)

    def dict(self) -> dict:
        raise NotImplementedError

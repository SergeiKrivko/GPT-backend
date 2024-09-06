from typing import Literal
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class MessageRead(BaseModel):
    uuid: UUID
    chat_uuid: UUID
    created_at: datetime
    deleted_at: datetime | None
    role: str
    content: str
    model: str | None
    context_size: int
    temperature: float


class MessageCreate(BaseModel):
    chat_uuid: UUID
    role: str
    content: str

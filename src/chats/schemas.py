from typing import Literal
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class ChatRead(BaseModel):
    uuid: UUID
    created_at: datetime
    deleted_at: datetime | None
    name: str
    model: str | None
    context_size: int
    temperature: float
    pinned: bool
    archived: bool
    user: str


class ChatUpdate(BaseModel):
    name: str
    model: str | None
    context_size: int
    temperature: float
    pinned: bool
    archived: bool

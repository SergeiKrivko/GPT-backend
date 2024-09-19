from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class ReplyRead(BaseModel):
    uuid: UUID
    message_uuid: UUID
    reply_to: UUID
    type: Literal['prompt', 'context', 'explicit', 'implicit']


class ReplyCreate(BaseModel):
    reply_to: UUID
    type: Literal['prompt', 'context', 'explicit', 'implicit']

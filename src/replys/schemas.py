from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class ReplyRead(BaseModel):
    uuid: UUID
    from_uuid: UUID
    to_uuid: UUID
    type: Literal['prompt', 'context', 'explicit', 'implicit']


class ReplyCreate(BaseModel):
    to_uuid: UUID
    type: Literal['prompt', 'context', 'explicit', 'implicit']

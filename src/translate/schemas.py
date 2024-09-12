from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class TranslateCreate(BaseModel):
    text: str

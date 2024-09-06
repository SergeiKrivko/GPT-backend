from typing import Literal
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class UserRead(BaseModel):
    uid: str
    name: str
    email: str

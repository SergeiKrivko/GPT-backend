from typing import Literal
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class LogRead(BaseModel):
    application: str
    version: str
    log: str

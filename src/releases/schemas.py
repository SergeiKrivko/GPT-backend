from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class ReleaseAssetRead(BaseModel):
    version: str
    system: str
    url: str


class ReleaseRead(BaseModel):
    version: str
    description: str
    assets: list[ReleaseAssetRead]

from typing import Any

from pydantic import BaseModel


class TranslateCreate(BaseModel):
    text: str


class ExtractCreate(BaseModel):
    lang: str
    filetype: str = None
    image: Any

from functools import lru_cache
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends

from pydantic_settings import BaseSettings, SettingsConfigDict

import os

load_dotenv()

VERSION = "0.0.1"

FIREBASE_SA_KEY = os.getenv("FIREBASE_SA_KEY")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

OCR_API_KEY = os.getenv("OCR_API_KEY")


class RatelimitSettings(BaseSettings):
    requests: int
    period: int

    model_config = SettingsConfigDict(env_prefix="ratelimit_")


@lru_cache
def get_ratelimit_settings() -> RatelimitSettings:
    return RatelimitSettings()


class AdminCredentialsSettings(BaseSettings):
    login: str
    password: str

    model_config = SettingsConfigDict(env_prefix="admin_")


@lru_cache
def get_admin_credentials():
    return AdminCredentialsSettings()


AdminCredentialsDep = Annotated[
    AdminCredentialsSettings, Depends(get_admin_credentials)
]

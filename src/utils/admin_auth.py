import hmac
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from src.utils.config import AdminCredentialsDep

security = HTTPBasic()

BasicAuthCredentialsDep = Annotated[HTTPBasicCredentials, Depends(security)]


def compare_digest(a: str, b: str) -> bool:
    """Безопасное сравнение строк."""
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def basic_auth(
    credentials: BasicAuthCredentialsDep,
    admin_credentials: AdminCredentialsDep,
) -> HTTPBasicCredentials:
    """Авторизация через Basic Auth."""
    if not compare_digest(
        credentials.username, admin_credentials.login
    ) or not compare_digest(credentials.password, admin_credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials


AdminAuthDep = Annotated[HTTPBasicCredentials, Depends(basic_auth)]

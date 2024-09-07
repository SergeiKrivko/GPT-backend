from src.authentication.client import AuthClient
from src.authentication.exceptions import NotAuthenticatedError
from src.authentication.schemas import UserRead
from src.utils.exceptions import exception_handler
from src.utils.unitofwork import IUnitOfWork


class AuthenticationService:
    def __init__(self, auth_client: AuthClient):
        self.auth_client = auth_client

    @exception_handler
    async def get_authenticated_user(self, token: str):
            res = await self.auth_client.verify_id_token(token)
            return UserRead(uid=res['uid'], name=res.get('name'), email=res.get('email'))

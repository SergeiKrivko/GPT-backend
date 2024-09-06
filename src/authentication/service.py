from src.authentication.client import AuthClient
from src.authentication.exceptions import NotAuthenticatedError
from src.authentication.schemas import UserRead
from src.utils.unitofwork import IUnitOfWork


class AuthenticationService:
    def __init__(self, auth_client: AuthClient):
        self.auth_client = auth_client

    async def get_authenticated_user(self, uow: IUnitOfWork, token: str):
        try:
            res = await self.auth_client.verify_id_token(token)
            return UserRead(uid=res['uid'], name=res.get('name'), email=res.get('email'))
        except NotAuthenticatedError:
            return None

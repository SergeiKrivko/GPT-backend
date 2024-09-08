import asyncio
import json

from firebase_admin import auth
import firebase_admin.credentials
from firebase_admin.auth import ExpiredIdTokenError, InvalidIdTokenError

from src.authentication.exceptions import NotAuthenticatedError
from src.utils.config import FIREBASE_SA_KEY
from src.utils.exceptions import AuthenticationError


class AuthClient:
    def __init__(self):
        cred = firebase_admin.credentials.Certificate(json.loads(FIREBASE_SA_KEY))
        firebase_admin.initialize_app(cred)

    @staticmethod
    async def verify_id_token(id_token: str) -> dict:
        try:
            decoded_token = await asyncio.to_thread(lambda: auth.verify_id_token(id_token))
        except InvalidIdTokenError as e:
            print(e)
            raise NotAuthenticatedError
        if 'uid' not in decoded_token:
            raise NotAuthenticatedError
        return decoded_token

import asyncio
import json

from firebase_admin import auth, storage
import firebase_admin.credentials
from firebase_admin.auth import InvalidIdTokenError

from src.authentication.exceptions import NotAuthenticatedError
from src.utils.config import FIREBASE_SA_KEY


class FirebaseClient:
    def __init__(self):
        cred = firebase_admin.credentials.Certificate(json.loads(FIREBASE_SA_KEY))
        firebase_admin.initialize_app(cred)
        self.__storage = storage.bucket('gpt-chat-bf384.appspot.com')

    @staticmethod
    async def verify_id_token(id_token: str) -> dict:
        if not id_token:
            raise NotAuthenticatedError
        try:
            decoded_token = await asyncio.to_thread(lambda: auth.verify_id_token(id_token))
        except InvalidIdTokenError as e:
            raise NotAuthenticatedError
        if 'uid' not in decoded_token:
            raise NotAuthenticatedError
        return decoded_token

    async def upload_text_file(self, path, text):
        await asyncio.to_thread(lambda: self.__storage.blob(path).upload_from_string(text))

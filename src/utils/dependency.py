from typing import Annotated

from fastapi import Depends, Form
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.authentication.client import FirebaseClient
from src.authentication.schemas import UserRead
from src.authentication.service import AuthenticationService
from src.chats.repository import ChatRepository
from src.chats.service import ChatService
from src.messages.repository import MessageRepository
from src.messages.service import MessageService
from src.replys.repository import ReplyRepository
from src.replys.service import ReplyService
from src.sockets.manager import SocketManager
from src.translate.service import TranslateService
from src.releases.service import ReleasesService
from src.utils.unitofwork import IUnitOfWork, UnitOfWork

auth_client = FirebaseClient()
authentication_service = AuthenticationService(auth_client)

socket_manager = SocketManager(authentication_service)

chat_repository = ChatRepository()
chat_service = ChatService(chat_repository, socket_manager)

reply_repository = ReplyRepository()
reply_service = ReplyService(reply_repository)

message_repository = MessageRepository()
message_service = MessageService(message_repository, chat_service, reply_repository, socket_manager)

translate_service = TranslateService()

releases_service = ReleasesService()

security = HTTPBearer()


async def get_authentication_service():
    return authentication_service


async def get_chat_service():
    return chat_service


async def get_message_service():
    return message_service


async def get_translate_service():
    return translate_service


async def get_releases_service():
    return releases_service


async def get_authentication_token(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]):
    return credentials.credentials


AuthenticationServiceDep = Annotated[AuthenticationService, Depends(get_authentication_service)]
ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
MessageServiceDep = Annotated[MessageService, Depends(get_message_service)]

TranslateServiceDep = Annotated[TranslateService, Depends(get_translate_service)]
ReleasesServiceDep = Annotated[ReleasesService, Depends(get_releases_service)]

UOWDep = Annotated[IUnitOfWork, Depends(UnitOfWork)]
AuthenticationDep = Annotated[str, Depends(get_authentication_token)]
FirebaseDep = Annotated[FirebaseClient, Depends(lambda: auth_client)]
FormDep = Annotated[str | None, Form()]


async def get_authenticated_user(token: AuthenticationDep,
                                 service: AuthenticationServiceDep):
    res = await service.get_authenticated_user(token)
    return res


AuthenticatedUserDep = Annotated[UserRead, Depends(get_authenticated_user)]

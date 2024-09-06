from typing import Annotated

from fastapi import Depends, Form
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.authentication.client import AuthClient
from src.authentication.service import AuthenticationService
from src.messages.repository import MessageRepository
from src.messages.service import MessageService
from src.replys.repository import ReplyRepository
from src.replys.service import ReplyService

from src.chats.repository import ChatRepository
from src.chats.service import ChatService

from src.utils.unitofwork import IUnitOfWork, UnitOfWork

auth_client = AuthClient()
authentication_service = AuthenticationService(auth_client)

chat_repository = ChatRepository()
chat_service = ChatService(chat_repository)

reply_repository = ReplyRepository()
reply_service = ReplyService(reply_repository)

message_repository = MessageRepository()
message_service = MessageService(message_repository, chat_service, reply_service)

security = HTTPBearer()


async def get_authentication_service():
    return authentication_service


async def get_chat_service():
    return chat_service


async def get_message_service():
    return message_service


async def get_authentication_token(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]):
    return credentials.credentials


AuthenticationServiceDep = Annotated[AuthenticationService, Depends(get_authentication_service)]
ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
MessageServiceDep = Annotated[MessageService, Depends(get_message_service)]

UOWDep = Annotated[IUnitOfWork, Depends(UnitOfWork)]
AuthenticationDep = Annotated[str, Depends(get_authentication_token)]
FormDep = Annotated[str | None, Form()]

from uuid import UUID

from fastapi import APIRouter, UploadFile

from src.authentication.exceptions import NotAuthenticatedError
from src.messages.exceptions import ReadMessageDenied, MessageNotFoundError
from src.messages.schemas import MessageCreate
from src.utils.dependency import MessageServiceDep, AuthenticationDep, AuthenticationServiceDep, UOWDep, ChatServiceDep
from src.utils.exceptions import exception_handler
from src.utils.logic import equal_uuids

router = APIRouter(prefix='/messages', tags=['Messages'])


@router.get('')
@exception_handler
async def get_messages(message_service: MessageServiceDep,
                       chat_service: ChatServiceDep,
                       authentication_service: AuthenticationServiceDep,
                       uow: UOWDep,
                       token: AuthenticationDep):
    author = await authentication_service.get_authenticated_user(uow, token)
    if not author:
        raise NotAuthenticatedError

    chats = await chat_service.get_chats(uow, author.uid)
    messages = []
    for chat in chats:
        m = await message_service.get_messages(uow, chat.uuid)
        messages.extend(m)

    if not messages:
        raise MessageNotFoundError

    return {
        'data': messages,
        'detail': 'Chat was selected.'
    }


@router.get('/{uuid}')
@exception_handler
async def get_message(uuid: UUID,
                      message_service: MessageServiceDep,
                      chat_service: ChatServiceDep,
                      authentication_service: AuthenticationServiceDep,
                      uow: UOWDep,
                      token: AuthenticationDep):
    author = await authentication_service.get_authenticated_user(uow, token)
    if not author:
        raise NotAuthenticatedError

    message = await message_service.get_message(uow, uuid)
    if not message:
        raise MessageNotFoundError

    chat = await chat_service.get_chat(uow, message.chat_uuid)

    if not equal_uuids(author.uid, chat.user):
        raise ReadMessageDenied

    return {
        'data': message,
        'detail': 'Message was selected.'
    }


@router.post('')
@exception_handler
async def post_messages(message: MessageCreate,
                        message_service: MessageServiceDep,
                        authentication_service: AuthenticationServiceDep,
                        uow: UOWDep,
                        token: AuthenticationDep):
    author = await authentication_service.get_authenticated_user(uow, token)
    if not author:
        raise NotAuthenticatedError

    uuid = await message_service.add_message(uow, message)
    return {
        'data': str(uuid) if uuid else None,
        'detail': 'Message was added.'
    }


@router.delete('/{uuid}')
@exception_handler
async def delete_message(uuid: UUID,
                         message_service: MessageServiceDep,
                         chat_service: ChatServiceDep,
                         authentication_service: AuthenticationServiceDep,
                         uow: UOWDep,
                         token: AuthenticationDep):
    author = await authentication_service.get_authenticated_user(uow, token)
    if not author:
        raise NotAuthenticatedError

    message = await message_service.get_message(uow, uuid)
    if not message:
        raise MessageNotFoundError

    chat = await chat_service.get_chat(uow, message.chat_uuid)

    if not equal_uuids(author.uid, chat.user):
        raise ReadMessageDenied

    await message_service.mark_message_deleted(uow, uuid)

    return {
        'data': None,
        'detail': 'Message was marked deleted.'
    }

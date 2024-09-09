import datetime
from uuid import UUID

from fastapi import APIRouter

from src.authentication.exceptions import NotAuthenticatedError
from src.messages.exceptions import ReadMessageDenied, MessageNotFoundError, DeleteMessageDenied, InsertMessageDenied
from src.messages.schemas import MessageCreate
from src.utils.dependency import MessageServiceDep, UOWDep, ChatServiceDep, AuthenticatedUserDep
from src.utils.exceptions import exception_handler
from src.utils.logic import equal_uuids

router = APIRouter(prefix='/messages', tags=['Messages'])


@router.get('')
@exception_handler
async def get_messages(message_service: MessageServiceDep,
                       author: AuthenticatedUserDep,
                       uow: UOWDep,
                       chat_uuid: UUID = None,
                       created_after: datetime.datetime = None,
                       deleted_after: datetime.datetime = None,
                       ):
    if not author:
        raise NotAuthenticatedError

    messages = await message_service.get_messages(uow, user=author.uid, chat_uuid=chat_uuid,
                                                  created_after=created_after,
                                                  deleted_after=deleted_after)

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
                      author: AuthenticatedUserDep,
                      uow: UOWDep,
                      ):
    message = await message_service.get_message(uow, uuid)
    if not message:
        raise MessageNotFoundError

    if not equal_uuids(author.uid, message.user):
        raise ReadMessageDenied

    return {
        'data': message,
        'detail': 'Message was selected.'
    }


@router.post('')
@exception_handler
async def post_messages(message: MessageCreate,
                        message_service: MessageServiceDep,
                        chat_service: ChatServiceDep,
                        author: AuthenticatedUserDep,
                        uow: UOWDep,
                        ):
    chat = await chat_service.get_chat(uow, message.chat_uuid)

    if not equal_uuids(author.uid, chat.user):
        raise InsertMessageDenied

    uuid = await message_service.add_message(uow, chat, message, author.uid)
    return {
        'data': str(uuid) if uuid else None,
        'detail': 'Message was added.'
    }


@router.delete('/{uuid}')
@exception_handler
async def delete_message(uuid: UUID,
                         message_service: MessageServiceDep,
                         author: AuthenticatedUserDep,
                         uow: UOWDep,
                         ):
    message = await message_service.get_message(uow, uuid)
    if not message:
        raise MessageNotFoundError

    if not equal_uuids(author.uid, message.user):
        raise DeleteMessageDenied

    await message_service.mark_message_deleted(uow, uuid, author.uid)

    return {
        'data': str(uuid),
        'detail': 'Message was marked deleted.'
    }

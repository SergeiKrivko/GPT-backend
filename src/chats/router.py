from datetime import datetime
from uuid import UUID

from fastapi import APIRouter

from src.authentication.exceptions import NotAuthenticatedError
from src.chats.exceptions import ReadChatDenied, ChatNotFoundError, UpdateChatDenied, DeleteChatDenied
from src.chats.schemas import ChatUpdate
from src.utils.dependency import ChatServiceDep, UOWDep, AuthenticatedUserDep
from src.utils.exceptions import exception_handler
from src.utils.logic import equal_uuids

router = APIRouter(prefix='/chats', tags=['Chats'])


@router.get('')
@exception_handler
async def get_chats(
        chat_service: ChatServiceDep,
        author: AuthenticatedUserDep,
        uow: UOWDep,
        created_after: datetime = None,
        deleted_after: datetime = None,
):
    chats = await chat_service.get_chats(uow, author.uid, created_after, deleted_after)
    if not chats:
        raise ChatNotFoundError

    return {
        'data': chats,
        'detail': 'Chats were selected.'
    }


@router.get('/{uuid}')
@exception_handler
async def get_chat(uuid: UUID,
                   chat_service: ChatServiceDep,
                   author: AuthenticatedUserDep,
                   uow: UOWDep,
                   ):
    chat = await chat_service.get_chat(uow, uuid)
    if not chat:
        raise ChatNotFoundError

    if not equal_uuids(author.uid, chat.user):
        raise ReadChatDenied

    return {
        'data': chat,
        'detail': 'Chat was selected.'
    }


@router.post('')
@exception_handler
async def post_chats(chat_service: ChatServiceDep,
                     author: AuthenticatedUserDep,
                     uow: UOWDep,
                     ):
    if not author:
        raise NotAuthenticatedError

    uuid = await chat_service.add_chat(uow, author.uid)
    return {
        'data': str(uuid) if uuid else None,
        'detail': 'Chat was added.'
    }


@router.put('/{uuid}')
@exception_handler
async def update_chat(uuid: UUID,
                      chat_update: ChatUpdate,
                      chat_service: ChatServiceDep,
                      author: AuthenticatedUserDep,
                      uow: UOWDep,
                      ):
    if not author:
        raise NotAuthenticatedError

    chat = await chat_service.get_chat(uow, uuid)
    if not chat:
        raise ChatNotFoundError

    if not equal_uuids(author.uid, chat.user):
        raise UpdateChatDenied

    await chat_service.update_chat(uow, uuid, chat_update, author.uid)

    return {
        'data': str(uuid),
        'detail': 'Chat was updated.'
    }


@router.delete('/{uuid}')
@exception_handler
async def delete_chat(uuid: UUID,
                      chat_service: ChatServiceDep,
                      author: AuthenticatedUserDep,
                      uow: UOWDep,
                      ):
    if not author:
        raise NotAuthenticatedError

    chat = await chat_service.get_chat(uow, uuid)
    if not chat:
        raise ChatNotFoundError

    if not equal_uuids(author.uid, chat.user):
        raise DeleteChatDenied

    await chat_service.mark_chat_deleted(uow, uuid, author.uid)

    return {
        'data': str(uuid),
        'detail': 'Chat was marked deleted.'
    }

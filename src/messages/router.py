from uuid import UUID

from fastapi import APIRouter, UploadFile, BackgroundTasks

from src.authentication.exceptions import NotAuthenticatedError
from src.messages.exceptions import ReadMessageDenied, MessageNotFoundError
from src.utils.dependency import MessageServiceDep, AuthenticationDep, AuthenticationServiceDep, UOWDep
from src.utils.exceptions import exception_handler
from src.utils.logic import equal_uuids

router = APIRouter(prefix='/messages', tags=['Messages'])


@router.get('/{uuid}')
@exception_handler
async def get_message(uuid: UUID,
                   message_service: MessageServiceDep,
                   authentication_service: AuthenticationServiceDep,
                   uow: UOWDep,
                   token: AuthenticationDep):
    author = await authentication_service.get_authenticated_user(uow, token)
    if not author:
        raise NotAuthenticatedError

    message = await message_service.get_message(uow, uuid)
    if not message:
        raise MessageNotFoundError

    if not equal_uuids(author.uuid, message.user):
        raise ReadMessageDenied

    return {
        'data': message,
        'detail': 'Message was selected.'
    }


@router.post('')
@exception_handler
async def post_messages(message_service: MessageServiceDep,
                     authentication_service: AuthenticationServiceDep,
                     uow: UOWDep,
                     token: AuthenticationDep,
                     file: UploadFile = None):
    author = await authentication_service.get_authenticated_user(uow, token)
    if not author:
        raise NotAuthenticatedError

    uuid = await message_service.add_message(uow, author.uuid, file.file)
    return {
        'data': str(uuid) if uuid else None,
        'detail': 'Message was added.'
    }

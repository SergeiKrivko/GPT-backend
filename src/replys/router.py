from uuid import UUID

from fastapi import APIRouter, UploadFile, BackgroundTasks

from src.authentication.exceptions import NotAuthenticatedError
from src.replys.exceptions import ReadReplyDenied, ReplyNotFoundError
from src.utils.dependency import ReplyServiceDep, AuthenticationDep, AuthenticationServiceDep, UOWDep
from src.utils.exceptions import exception_handler
from src.utils.logic import equal_uuids

router = APIRouter(prefix='/replys', tags=['Replys'])


@router.get('/{uuid}')
@exception_handler
async def get_reply(uuid: UUID,
                   reply_service: ReplyServiceDep,
                   authentication_service: AuthenticationServiceDep,
                   uow: UOWDep,
                   token: AuthenticationDep):
    author = await authentication_service.get_authenticated_user(uow, token)
    if not author:
        raise NotAuthenticatedError

    reply = await reply_service.get_reply(uow, uuid)
    if not reply:
        raise ReplyNotFoundError

    if not equal_uuids(author.uuid, reply.user):
        raise ReadReplyDenied

    return {
        'data': reply,
        'detail': 'Reply was selected.'
    }


@router.post('')
@exception_handler
async def post_replys(reply_service: ReplyServiceDep,
                     authentication_service: AuthenticationServiceDep,
                     uow: UOWDep,
                     token: AuthenticationDep,
                     background_tasks: BackgroundTasks,
                     file: UploadFile = None):
    author = await authentication_service.get_authenticated_user(uow, token)
    if not author:
        raise NotAuthenticatedError

    uuid = await reply_service.add_reply(uow, author.uuid, file.file, background_tasks)
    return {
        'data': str(uuid) if uuid else None,
        'detail': 'Reply was added.'
    }

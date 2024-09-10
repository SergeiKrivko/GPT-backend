from datetime import datetime
from uuid import UUID

from fastapi import APIRouter

from src.authentication.exceptions import NotAuthenticatedError
from src.chats.exceptions import ReadChatDenied, ChatNotFoundError, UpdateChatDenied, DeleteChatDenied
from src.chats.schemas import ChatUpdate
from src.gpt import gpt
from src.utils.dependency import ChatServiceDep, UOWDep, AuthenticatedUserDep
from src.utils.exceptions import exception_handler
from src.utils.logic import equal_uuids

router = APIRouter(prefix='/gpt', tags=['GPT'])


@router.get('/models')
@exception_handler
async def get_models_handler():
    return {
        'data': gpt.get_models(),
        'detail': 'GPT models were selected.'
    }

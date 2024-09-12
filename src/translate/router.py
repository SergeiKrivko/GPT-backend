from datetime import datetime
from uuid import UUID

from fastapi import APIRouter

from src.authentication.exceptions import NotAuthenticatedError
from src.chats.exceptions import ReadChatDenied, ChatNotFoundError, UpdateChatDenied, DeleteChatDenied
from src.chats.schemas import ChatUpdate
from src.gpt import gpt
from src.translate.schemas import TranslateCreate
from src.utils.dependency import ChatServiceDep, UOWDep, AuthenticatedUserDep, TranslateServiceDep
from src.utils.exceptions import exception_handler
from src.utils.logic import equal_uuids

router = APIRouter(prefix='/translate', tags=['Translate'])


@router.post('/detect')
@exception_handler
async def post_detect_handler(src: TranslateCreate, translate_service: TranslateServiceDep):
    res = await translate_service.detect(src.text)
    return {
        'data': {
            'lang': res.result.id,
        },
        'detail': 'GPT models were selected.'
    }


@router.post('/translate')
@exception_handler
async def post_translate_handler(src: TranslateCreate, dst: str, translate_service: TranslateServiceDep):
    res = await translate_service.translate(src.text, dst)
    return {
        'data': {
            'res': res.result,
            'src': res.source_language.id,
            'dst': res.destination_language.id,
        },
        'detail': 'GPT models were selected.'
    }

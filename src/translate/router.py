from fastapi import APIRouter, UploadFile

from src.translate.schemas import TranslateCreate, ExtractCreate
from src.utils.dependency import TranslateServiceDep
from src.utils.exceptions import exception_handler

router = APIRouter(prefix='/translate', tags=['Translate'])


@router.post('/detect')
@exception_handler
async def post_detect_handler(src: TranslateCreate, translate_service: TranslateServiceDep):
    res = await translate_service.detect(src.text)
    return {
        'data': {
            'lang': res.result.id,
        },
        'detail': 'Language detected.'
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
        'detail': 'Text was translated.'
    }


@router.post('/extract')
@exception_handler
async def post_extract_handler(src: ExtractCreate, translate_service: TranslateServiceDep):
    res = await translate_service.extract_text(src.image, src.filetype, src.lang)
    return {
        'data': res,
        'detail': 'Text was extracted.'
    }

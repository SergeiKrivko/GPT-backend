import asyncio

import aiohttp
from loguru import logger

from translatepy import Translator
from translatepy.models import LanguageResult, TranslationResult
from translatepy.translators import YandexTranslate

from src.translate.exceptions import ExtractFailedError
from src.utils import config


class TranslateService:
    def __init__(self):
        self.__translator = Translator([YandexTranslate])
        self.__ocr_session = aiohttp.ClientSession()

    async def detect(self, text):
        res: LanguageResult = await asyncio.to_thread(lambda: self.__translator.language(text))
        logger.debug(f"Language detected: {res.result}")
        return res

    async def translate(self, text, lang):
        res: TranslationResult = await asyncio.to_thread(lambda: self.__translator.translate(text, lang))
        logger.debug(f"Message translated: {res.result}")
        return res

    async def extract_text(self, image: str, filetype: str, lang='eng'):
        async with self.__ocr_session.post("https://api.ocr.space/parse/image", data={
            'apikey': config.OCR_API_KEY,
            'language': lang,
            'filetype': filetype,
            'base64Image': image,
        }) as resp:
            res = await resp.json()
            if res.get('ErrorMessage'):
                raise ExtractFailedError(res.get('ErrorMessage'))
            return res['ParsedResults'][0]['ParsedText']



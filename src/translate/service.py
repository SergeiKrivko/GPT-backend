import asyncio

from translatepy import Translator
from translatepy.models import LanguageResult, TranslationResult
from translatepy.translators import YandexTranslate


class TranslateService:
    def __init__(self):
        self.__translator = Translator([YandexTranslate])

    async def detect(self, text):
        res: LanguageResult = await asyncio.to_thread(lambda: self.__translator.language(text))
        print(res.result)
        return res

    async def translate(self, text, lang):
        res: TranslationResult = await asyncio.to_thread(lambda: self.__translator.translate(text, lang))
        print(res.result)
        return res



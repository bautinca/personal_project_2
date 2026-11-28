import html

import httpx

from app.hexagon.errors import TextTooLongToTranslate, TranslationUnavailable
from app.hexagon.ports import Translator

URL = "https://api.mymemory.translated.net/get"
MAX_BYTES = 500  # Limite de MyMemory por consulta.


# Adaptador del puerto Translator que usa la API publica de MyMemory.
class MyMemoryTranslator(Translator):
    def __init__(self, client: httpx.Client):
        self._client = client

    def translate(self, text: str) -> str:
        if len(text.encode()) > MAX_BYTES:
            raise TextTooLongToTranslate()
        try:
            response = self._client.get(URL, params={"q": text, "langpair": "es|en"})
            response.raise_for_status()
            body = response.json()
            # MyMemory puede responder HTTP 200 ante un error: el estado real viene en el cuerpo
            # y el mensaje de error ocupa el lugar de la traduccion.
            status = int(body["responseStatus"])
            translation = body["responseData"]["translatedText"]
            quota_finished = body.get("quotaFinished")
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as error:
            raise TranslationUnavailable() from error
        if status != 200 or quota_finished or not isinstance(translation, str) or not translation:
            raise TranslationUnavailable()
        return html.unescape(translation)

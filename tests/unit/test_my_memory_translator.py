import httpx
import pytest

from app.adapters.translation.my_memory_translator import MyMemoryTranslator
from app.hexagon.errors import TextTooLongToTranslate, TranslationUnavailable


# MockTransport responde en lugar de la red: estos tests no llaman a MyMemory.
def translator_with(handler):
    return MyMemoryTranslator(httpx.Client(transport=httpx.MockTransport(handler)))


def responding(status_code=200, **kwargs):
    return translator_with(lambda request: httpx.Response(status_code, **kwargs))


def body(translation, status=200, quota_finished=False):
    return {
        "responseData": {"translatedText": translation},
        "responseStatus": status,
        "quotaFinished": quota_finished,
    }


def test_returns_translation_and_sends_spanish_to_english_query():
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json=body("hello & goodbye"))

    assert translator_with(handler).translate("hola & chau") == "hello & goodbye"
    assert requests[0].url.host == "api.mymemory.translated.net"
    assert dict(requests[0].url.params) == {"q": "hola & chau", "langpair": "es|en"}


def test_decodes_html_entities():
    assert responding(json=body("I don&#39;t know")).translate("no se") == "I don't know"


def test_accepts_text_at_the_byte_limit():
    assert responding(json=body("ok")).translate("a" * 500) == "ok"


# El limite es en bytes: la "ñ" ocupa dos.
@pytest.mark.parametrize("text", ["a" * 501, "ñ" * 251])
def test_rejects_long_text_without_calling_the_api(text):
    def handler(request):
        pytest.fail("No deberia llamar a la API")

    with pytest.raises(TextTooLongToTranslate):
        translator_with(handler).translate(text)


@pytest.mark.parametrize(
    "response",
    [
        # Error informado en el cuerpo de una respuesta HTTP 200.
        {"json": body("QUERY LENGTH LIMIT EXCEEDED", status="403")},
        {"json": body("MYMEMORY WARNING", status=429, quota_finished=True)},
        {"json": body("MYMEMORY WARNING", quota_finished=True)},
        {"json": body("")},
        {"json": body(None)},
        {"json": {"responseStatus": 200, "responseData": None}},
        {"json": {}},
        {"text": "<html>no es JSON</html>"},
        {"status_code": 500, "json": body("hello")},
    ],
)
def test_invalid_responses_mean_unavailable(response):
    with pytest.raises(TranslationUnavailable):
        responding(**response).translate("hola")


@pytest.mark.parametrize("error", [httpx.ConnectError, httpx.ReadTimeout])
def test_network_errors_mean_unavailable(error):
    def handler(request):
        raise error("fallo de red", request=request)

    with pytest.raises(TranslationUnavailable):
        translator_with(handler).translate("hola")

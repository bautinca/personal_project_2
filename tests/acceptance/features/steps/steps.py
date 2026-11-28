from behave import given, then, when

from app.hexagon.errors import TranslationUnavailable
from app.version import read_version


@given("la aplicacion esta disponible")
def step_app_available(context):
    assert context.client is not None


@when('el usuario envia el texto "{text}"')
def step_send_text(context, text):
    context.response = context.client.post("/", data={"text": text})


def find_entry_id(context, text):
    entries = context.client.get("/entries").json()
    return next(e["id"] for e in entries if e["text"] == text)


@when('el usuario elimina el texto "{text}"')
def step_delete_text(context, text):
    context.response = context.client.post(f"/entries/{find_entry_id(context, text)}/delete")


@when('el usuario modifica el texto "{text}" por "{new_text}"')
def step_update_text(context, text, new_text):
    entry_id = find_entry_id(context, text)
    context.response = context.client.post(f"/entries/{entry_id}/edit", data={"text": new_text})


# Igual que el navegador: recargar repite la ultima peticion que produjo la pagina actual.
@when("el usuario recarga la pagina")
def step_reload(context):
    last = context.response.request
    context.response = context.client.request(last.method, last.url, content=last.content, headers=last.headers)


@when("consulto el endpoint de health")
def step_health(context):
    context.response = context.client.get("/health")


@when("consulto el endpoint de version")
def step_version(context):
    context.response = context.client.get("/version")


@then("la respuesta es exitosa")
def step_ok(context):
    assert context.response.status_code == 200


@then('el texto "{text}" aparece en la pagina')
def step_text_in_page(context, text):
    assert text in context.response.text


@then('el texto "{text}" no aparece en la pagina')
def step_text_not_in_page(context, text):
    assert text not in context.response.text


@then('el texto "{text}" aparece una sola vez en la tabla')
def step_text_once(context, text):
    assert context.response.text.count(f"<td>{text}</td>") == 1


@then('el estado es "{status}"')
def step_status(context, status):
    assert context.response.json()["status"] == status


@then("la version es la definida en el archivo VERSION")
def step_version_value(context):
    assert context.response.json()["version"] == read_version()


@given("el servicio de traduccion no esta disponible")
def step_translator_down(context):
    context.translator.error = TranslationUnavailable()


@when('el usuario traduce el texto "{text}"')
def step_translate_text(context, text):
    context.response = context.client.post(f"/entries/{find_entry_id(context, text)}/translate")


@when("el usuario vuelve a la pagina principal")
def step_visit_index(context):
    context.response = context.client.get("/")


# El traductor falso antepone "[en] " al texto original.
@then('se muestra la traduccion de "{text}"')
def step_translation_shown(context, text):
    assert f"[en] {text}" in context.response.text


@then('no se muestra la traduccion de "{text}"')
def step_translation_not_shown(context, text):
    assert f"[en] {text}" not in context.response.text


@then('se muestra el aviso "{message}"')
def step_warning_shown(context, message):
    assert message in context.response.text

import re

import pytest

from app.hexagon.errors import TextTooLongToTranslate, TranslationUnavailable
from app.version import read_version


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_version(client):
    r = client.get("/version")
    assert r.status_code == 200
    assert r.json() == {"version": read_version()}


def test_index_page_shows_entries(client):
    client.post("/", data={"text": "texto en tabla"})
    r = client.get("/")
    assert r.status_code == 200
    assert "texto en tabla" in r.text
    assert "enviar" in r.text


# Crea la entrada como lo hace la pagina y devuelve su id.
def create_entry(client, text):
    client.post("/", data={"text": text})
    return client.get("/entries").json()[-1]["id"]


def test_list_entries(client):
    first_id = create_entry(client, "primero")
    second_id = create_entry(client, "segundo")

    r = client.get("/entries")

    assert r.status_code == 200
    assert r.json() == [{"id": first_id, "text": "primero"}, {"id": second_id, "text": "segundo"}]


def test_delete_from_form_only_removes_selected_entry(client):
    deleted_id = create_entry(client, "a borrar")
    kept_id = create_entry(client, "se queda")

    client.post(f"/entries/{deleted_id}/delete")

    assert client.get("/entries").json() == [{"id": kept_id, "text": "se queda"}]


def test_delete_from_form_redirects_to_index(client):
    entry_id = create_entry(client, "borrar desde la pagina")

    r = client.post(f"/entries/{entry_id}/delete", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/"
    assert client.get("/entries").json() == []


def test_delete_missing_entry_from_form_keeps_other_entries(client):
    create_entry(client, "se queda")

    r = client.post("/entries/999/delete")
    assert r.status_code == 200
    assert "se queda" in r.text


def test_index_page_shows_delete_button(client):
    entry_id = create_entry(client, "con boton")

    r = client.get("/")
    assert f'action="/entries/{entry_id}/delete"' in r.text
    assert "eliminar" in r.text


def test_create_from_form_redirects_to_index(client):
    r = client.post("/", data={"text": "desde el formulario"}, follow_redirects=False)

    assert r.status_code == 303
    assert r.headers["location"] == "/"
    assert [e["text"] for e in client.get("/entries").json()] == ["desde el formulario"]


def test_update_from_form_redirects_to_index(client):
    entry_id = create_entry(client, "original")

    r = client.post(f"/entries/{entry_id}/edit", data={"text": "desde la pagina"}, follow_redirects=False)

    assert r.status_code == 303
    assert r.headers["location"] == "/"
    assert client.get("/entries").json() == [{"id": entry_id, "text": "desde la pagina"}]


def test_update_missing_entry_from_form_keeps_other_entries(client):
    entry_id = create_entry(client, "se queda")

    r = client.post("/entries/999/edit", data={"text": "nada"})

    assert r.status_code == 200
    assert client.get("/entries").json() == [{"id": entry_id, "text": "se queda"}]


def test_update_from_form_without_text_returns_422_and_keeps_entry(client):
    entry_id = create_entry(client, "original")

    r = client.post(f"/entries/{entry_id}/edit", data={})

    assert r.status_code == 422
    assert client.get("/entries").json() == [{"id": entry_id, "text": "original"}]


def test_index_page_shows_edit_form(client):
    entry_id = create_entry(client, "editable")

    r = client.get("/")

    assert f'action="/entries/{entry_id}/edit"' in r.text
    assert 'value="editable"' in r.text
    assert "modificar" in r.text


TRANSLATION_ERRORS = [
    (TextTooLongToTranslate, 422, "El texto es demasiado largo para traducirlo"),
    (TranslationUnavailable, 503, "No se pudo traducir, intenta mas tarde"),
]


def test_translate_from_form_shows_translation_only_in_that_response(client):
    entry_id = create_entry(client, "hola")

    r = client.post(f"/entries/{entry_id}/translate")

    assert r.status_code == 200
    assert "<em>[en] hola</em>" in r.text
    assert client.get("/entries").json() == [{"id": entry_id, "text": "hola"}]
    assert "[en] hola" not in client.get("/").text


@pytest.mark.parametrize("error, status_code, message", TRANSLATION_ERRORS)
def test_translate_from_form_shows_errors_and_keeps_entries(client, translator, error, status_code, message):
    entry_id = create_entry(client, "hola")
    translator.error = error()

    r = client.post(f"/entries/{entry_id}/translate")

    assert r.status_code == status_code
    assert message in r.text
    assert "<td>hola" in r.text


def test_translate_missing_entry_from_form_redirects_to_index(client):
    r = client.post("/entries/999/translate", follow_redirects=False)

    assert r.status_code == 303
    assert r.headers["location"] == "/"


def test_index_page_shows_translate_button_without_calling_translator(client, translator):
    entry_id = create_entry(client, "hola")

    r = client.get("/")

    assert f'action="/entries/{entry_id}/translate"' in r.text
    assert "traducir" in r.text
    assert translator.requested == []


def test_version_file_has_a_valid_format():
    assert re.fullmatch(r"\d+\.\d+\.\d+", read_version())

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_version(client):
    r = client.get("/version")
    assert r.status_code == 200
    assert r.json() == {"version": "10.3"}


def test_create_and_list_entry(client):
    r = client.post("/entries", json={"text": "hola mundo"})
    assert r.status_code == 200
    data = r.json()
    assert data["text"] == "hola mundo"
    assert "id" in data

    r = client.get("/entries")
    assert r.status_code == 200
    entries = r.json()
    assert len(entries) == 1
    assert entries[0]["text"] == "hola mundo"


def test_index_page_shows_entries(client):
    client.post("/", data={"text": "texto en tabla"})
    r = client.get("/")
    assert r.status_code == 200
    assert "texto en tabla" in r.text
    assert "enviar" in r.text


def create_entry(client, text):
    return client.post("/entries", json={"text": text}).json()["id"]


def test_delete_entry(client):
    entry_id = create_entry(client, "a borrar")

    r = client.delete(f"/entries/{entry_id}")
    assert r.status_code == 204
    assert client.get("/entries").json() == []


def test_delete_only_removes_selected_entry(client):
    deleted_id = create_entry(client, "a borrar")
    kept_id = create_entry(client, "se queda")

    client.delete(f"/entries/{deleted_id}")

    assert client.get("/entries").json() == [{"id": kept_id, "text": "se queda"}]


def test_delete_missing_entry_returns_404(client):
    r = client.delete("/entries/999")
    assert r.status_code == 404
    assert r.json() == {"detail": "Entrada no encontrada"}


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

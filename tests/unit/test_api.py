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

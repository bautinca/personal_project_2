# Controlador HTTP: traduce peticiones HTTP a llamadas a Sistema y sus resultados a respuestas HTTP.
from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .bootstrap import get_sistema
from .hexagon.errors import EntryNotFound
from .hexagon.sistema import Sistema
from .schemas import EntryCreate, EntryRead
from .version import read_version

APP_VERSION = read_version()

# Configuración de Jinja2 para renderizar plantillas HTML desde el directorio "app/templates".
templates = Jinja2Templates(directory="app/templates")


# Creación de la instancia de FastAPI con título y versión. El esquema de la base lo gestiona Alembic antes de arrancar.
app = FastAPI(title="Text Entries", version=APP_VERSION)


# Endoint de salud de la aplicación que devuelve un JSON con el estado "ok" simplemente
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"version": APP_VERSION}


@app.get("/", response_class=HTMLResponse)
def index(request: Request, sistema: Sistema = Depends(get_sistema)):
    return templates.TemplateResponse(
        request, "index.html", {"entries": sistema.list_entries(), "version": APP_VERSION}
    )


# Se redirige tras guardar (Post/Redirect/Get) para que recargar la pagina no vuelva a enviar el formulario.
@app.post("/")
def create_from_form(text: str = Form(...), sistema: Sistema = Depends(get_sistema)):
    sistema.add_entry(text)
    return RedirectResponse("/", status_code=303)


# Los formularios HTML solo soportan GET y POST, por eso la interfaz web elimina mediante un POST.
# Si la entrada ya no existe (por ejemplo, una pagina desactualizada) simplemente se vuelve al listado.
@app.post("/entries/{entry_id}/delete")
def delete_from_form(entry_id: int, sistema: Sistema = Depends(get_sistema)):
    try:
        sistema.delete_entry(entry_id)
    except EntryNotFound:
        pass
    return RedirectResponse("/", status_code=303)


@app.get("/entries", response_model=list[EntryRead])
def list_entries(sistema: Sistema = Depends(get_sistema)):
    return sistema.list_entries()


@app.post("/entries", response_model=EntryRead)
def create_entry(payload: EntryCreate, sistema: Sistema = Depends(get_sistema)):
    return sistema.add_entry(payload.text)


@app.delete("/entries/{entry_id}", status_code=204)
def delete_entry(entry_id: int, sistema: Sistema = Depends(get_sistema)):
    try:
        sistema.delete_entry(entry_id)
    except EntryNotFound:
        raise HTTPException(status_code=404, detail="Entrada no encontrada") from None

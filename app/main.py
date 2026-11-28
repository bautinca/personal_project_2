# Controlador HTTP: traduce peticiones HTTP a llamadas a Sistema y sus resultados a respuestas HTTP.
from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .bootstrap import get_sistema
from .hexagon.errors import EntryNotFound, TextTooLongToTranslate, TranslationUnavailable
from .hexagon.sistema import Sistema
from .schemas import EntryRead
from .version import read_version

APP_VERSION = read_version()

# Codigo HTTP y mensaje para cada error de traduccion.
TRANSLATION_ERRORS = {
    TextTooLongToTranslate: (422, "El texto es demasiado largo para traducirlo"),
    TranslationUnavailable: (503, "No se pudo traducir, intenta mas tarde"),
}

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


def render_index(request: Request, sistema: Sistema, status_code: int = 200, **extra):
    context = {"entries": sistema.list_entries(), "version": APP_VERSION, **extra}
    return templates.TemplateResponse(request, "index.html", context, status_code=status_code)


@app.get("/", response_class=HTMLResponse)
def index(request: Request, sistema: Sistema = Depends(get_sistema)):
    return render_index(request, sistema)


# Se redirige tras guardar (Post/Redirect/Get) para que recargar la pagina no vuelva a enviar el formulario.
@app.post("/")
def create_from_form(text: str = Form(...), sistema: Sistema = Depends(get_sistema)):
    sistema.add_entry(text)
    return RedirectResponse("/", status_code=303)


# Los formularios HTML solo soportan GET y POST, por eso la interfaz web modifica y elimina mediante un POST.
# Si la entrada ya no existe (por ejemplo, una pagina desactualizada) simplemente se vuelve al listado.
@app.post("/entries/{entry_id}/edit")
def update_from_form(entry_id: int, text: str = Form(...), sistema: Sistema = Depends(get_sistema)):
    try:
        sistema.update_entry(entry_id, text)
    except EntryNotFound:
        pass
    return RedirectResponse("/", status_code=303)


@app.post("/entries/{entry_id}/delete")
def delete_from_form(entry_id: int, sistema: Sistema = Depends(get_sistema)):
    try:
        sistema.delete_entry(entry_id)
    except EntryNotFound:
        pass
    return RedirectResponse("/", status_code=303)


# No redirige como los demas formularios: no guarda nada y la traduccion solo vive en esta respuesta.
@app.post("/entries/{entry_id}/translate", response_class=HTMLResponse)
def translate_from_form(request: Request, entry_id: int, sistema: Sistema = Depends(get_sistema)):
    try:
        translation = sistema.translate_entry(entry_id)
    except EntryNotFound:
        return RedirectResponse("/", status_code=303)
    except (TextTooLongToTranslate, TranslationUnavailable) as error:
        status_code, message = TRANSLATION_ERRORS[type(error)]
        return render_index(request, sistema, status_code, translated_id=entry_id, translation_error=message)
    return render_index(request, sistema, translated_id=entry_id, translation=translation)


# Solo lectura: la usa el smoke test para comprobar que la app llega a la base de datos.
@app.get("/entries", response_model=list[EntryRead])
def list_entries(sistema: Sistema = Depends(get_sistema)):
    return sistema.list_entries()

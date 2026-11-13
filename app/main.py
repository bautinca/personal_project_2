import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import Base, engine, SessionLocal
from .models import Entry
from .schemas import EntryCreate, EntryRead

# Version de la aplicacion obtenida de la variable de entorno APP_VERSION, si no está definida, usamos "10.3" como valor por defecto.
APP_VERSION = os.getenv("APP_VERSION", "10.3")

# Configuración de Jinja2 para renderizar plantillas HTML desde el directorio "app/templates".
templates = Jinja2Templates(directory="app/templates")

# Al arrancar la aplicacion se inicializa la base de datos de desarrollo local, creando las tablas definidas en los modelos ORM si no existen.
def init_db():
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    return SessionLocal()

# El ciclo de vida de la aplicación se define mediante un contexto asíncrono que inicializa la base de datos al arrancar la aplicación y luego cierra la sesión de la base de datos al finalizar.
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

# Creación de la instancia de FastAPI con título, versión y ciclo de vida definido.
app = FastAPI(title="Text Entries", version=APP_VERSION, lifespan=lifespan)

# Endoint de salud de la aplicación que devuelve un JSON con el estado "ok" simplemente
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"version": APP_VERSION}


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    db = get_session()
    try:
        entries = db.query(Entry).order_by(Entry.id).all()
        return templates.TemplateResponse(
            request, "index.html", {"entries": entries, "version": APP_VERSION}
        )
    finally:
        db.close()


@app.post("/", response_class=HTMLResponse)
def create_from_form(request: Request, text: str = Form(...)):
    db = get_session()
    try:
        entry = Entry(text=text)
        db.add(entry)
        db.commit()
        db.refresh(entry)
        entries = db.query(Entry).order_by(Entry.id).all()
        return templates.TemplateResponse(
            request, "index.html", {"entries": entries, "version": APP_VERSION}
        )
    finally:
        db.close()


@app.get("/entries")
def list_entries():
    db = get_session()
    try:
        entries = db.query(Entry).order_by(Entry.id).all()
        return [EntryRead.model_validate(e) for e in entries]
    finally:
        db.close()


@app.post("/entries", response_model=EntryRead)
def create_entry(payload: EntryCreate):
    db = get_session()
    try:
        entry = Entry(text=payload.text)
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return EntryRead.model_validate(entry)
    finally:
        db.close()

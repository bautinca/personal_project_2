# Text Entries App

Aplicacion simple en FastAPI + PostgreSQL, containerizada con Docker.

## Levantar en desarrollo

```bash
docker compose up --build
```

App disponible en http://localhost:8000

## Tests

Unitarios:
```bash
docker compose exec app pytest
```

Aceptacion (behave):
```bash
docker compose exec app behave
```

Para correr tests contra la DB de testing, usar DATABASE_URL apuntando a db_test:
```bash
DATABASE_URL=postgresql+psycopg2://app:app@db_test:5432/appdb_test
```

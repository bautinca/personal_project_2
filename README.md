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

## Linter (ruff)

Revisar el codigo:
```bash
docker compose exec app ruff check .
```

Corregir automaticamente lo que se pueda:
```bash
docker compose exec app ruff check --fix .
```

Formatear el codigo:
```bash
docker compose exec app ruff format .
```

## Pipeline CI local

Corre el linter, los tests unitarios y de integracion, y los tests de aceptacion contra la DB de testing. Se detiene en la primera etapa que falla.

```bash
./ci.sh
```

## GitHub Actions

En cada push y pull request a `main`, el workflow `.github/workflows/ci.yml` corre el linter, los tests unitarios y de integracion, y los tests de aceptacion. No usa `ci.sh`: si cambian las etapas, hay que actualizar ambos.

## Deploy a produccion

Cada tag nuevo despliega su commit en Render (con la base de datos en Supabase), siempre que antes pasen el linter y los tests. Ver `.github/workflows/deploy.yml`.

```bash
git tag v1.0.0
git push origin v1.0.0
```

### Configuracion inicial (una sola vez)

1. **Supabase:** crear un proyecto. En *Connect*, copiar la cadena de **Session pooler** (puerto 5432), reemplazar la contrasena (codificando caracteres especiales) y agregar `?sslmode=require` al final.
2. **Supabase:** desactivar la Data API (*Integrations > Data API > Enable Data API*). La app se conecta directo a Postgres y no la usa.
3. **Render:** *New > Blueprint*, elegir este repositorio (usa `render.yaml`) y cargar `DATABASE_URL` con la cadena anterior.
4. **GitHub:** en *Settings > Secrets and variables > Actions*, crear los secretos:
   - `RENDER_DEPLOY_HOOK_URL`: en el servicio de Render, *Settings > Deploy Hook*.
   - `RENDER_API_KEY`: en Render, *Account Settings > API Keys*.
   - `RENDER_SERVICE_ID`: el identificador `srv-...` que aparece en la URL del servicio.

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

## Migraciones (Alembic)

El esquema de la base se gestiona con migraciones en `app/adapters/persistence/migrations/versions/`. El contenedor aplica las pendientes (`alembic upgrade head`) antes de arrancar la app, en local y en produccion.

Para cambiar el esquema:

1. Modificar el modelo en `app/adapters/persistence/models.py`.
2. Generar la migracion (con los contenedores levantados) y **revisar el archivo generado**:
   ```bash
   docker compose exec --user "$(id -u):$(id -g)" app alembic revision --autogenerate -m "descripcion del cambio"
   ```
3. Aplicarla en desarrollo:
   ```bash
   docker compose restart app
   ```

Otros comandos:
```bash
docker compose exec app alembic current        # revision aplicada
docker compose exec app alembic history        # historial
docker compose exec app alembic downgrade -1   # revierte la ultima (puede borrar datos)
```

En produccion, la migracion corre mientras la version anterior sigue atendiendo, asi que conviene que los cambios sean compatibles con ella (por ejemplo, agregar columnas opcionales y borrar las viejas en un deploy posterior).

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

La version de la app se define a mano en el archivo `VERSION` y el tag tiene que ser identico (sin `v`); si no coinciden, no se despliega.

```bash
echo "1.0.2" > VERSION
git commit -am "Version 1.0.2"
git push
git tag 1.0.2
git push origin 1.0.2
```

Despues del deploy corre un **smoke test** contra produccion: verifica que `/version` coincida con el archivo `VERSION` y que `/health`, `/entries` (acceso a la base) y `/` respondan. Solo lee datos. La logica esta en `smoke.sh` y la URL de produccion en `PRODUCTION_URL` dentro del workflow. Tambien se puede correr a mano (requiere `curl` y `jq`):

```bash
./smoke.sh https://personal-project-2-1kzb.onrender.com
```

### Configuracion inicial (una sola vez)

1. **Supabase:** crear un proyecto. En *Connect*, copiar la cadena de **Session pooler** (puerto 5432), reemplazar la contrasena (codificando caracteres especiales) y agregar `?sslmode=require` al final.
2. **Supabase:** desactivar la Data API (*Integrations > Data API > Enable Data API*). La app se conecta directo a Postgres y no la usa.
3. **Render:** *New > Blueprint*, elegir este repositorio (usa `render.yaml`) y cargar `DATABASE_URL` con la cadena anterior.
4. **GitHub:** en *Settings > Secrets and variables > Actions*, crear los secretos:
   - `RENDER_DEPLOY_HOOK_URL`: en el servicio de Render, *Settings > Deploy Hook*.
   - `RENDER_API_KEY`: en Render, *Account Settings > API Keys*.
   - `RENDER_SERVICE_ID`: el identificador `srv-...` que aparece en la URL del servicio

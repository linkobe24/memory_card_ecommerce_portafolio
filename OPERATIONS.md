# OPERATIONS – MemoryCard

Guía operativa para levantar y mantener el proyecto **MemoryCard** usando el `Makefile` recién añadido. El repositorio contiene:

- `frontend/`: Next.js 15.5 (React 19, Turbopack, Tailwind).
- `backend/`: FastAPI + SQLAlchemy async + Pytest.
- `docker-compose.yml`: Postgres 15, Redis 7, pgAdmin, API y frontend.

## 1. Prerrequisitos locales

| Herramienta | Versión sugerida | Uso |
| ----------- | ---------------- | --- |
| Docker & Docker Compose | Docker Desktop 4.x+ | Stack completo y servicios de datos. |
| Python 3.11 | `python3 --version` | Backend fuera de contenedores (`venv`). |
| Node.js 20 + npm 10 | `node --version` | Frontend Next.js. |
| GNU Make | viene con Xcode CLT / build-essential | Orquestador de comandos. |

> Nota: si solo usarás Docker, Node y Python únicamente se necesitan para ejecutar tests sin contenedores.

## 2. Uso rápido del Makefile

| Target | Propósito |
| ------ | --------- |
| `make env` | Copia `.env` y `frontend/.env.local` desde los ejemplos si aún no existen. |
| `make docker-up` / `docker-up-logs` | Construye y levanta todo el stack (modo daemon o adjunto a logs). |
| `make docker-down` / `docker-destroy` | Detiene servicios (el segundo también elimina volúmenes). |
| `make docker-logs` / `docker-ps` | Sigue logs de backend/frontend o inspecciona el estado. |
| `make infra-up` / `infra-down` | Levanta solo Postgres + Redis para desarrollo local híbrido. |
| `make backend-install` / `frontend-install` | Resuelve dependencias en `backend/.venv` y `frontend/node_modules`. |
| `make backend-dev` / `frontend-dev` | Inicia FastAPI (port 8000) y Next.js (port 3000). Ejecutar en terminales separadas. |
| `make backend-test` | Corre Pytest usando la config de `backend/pytest.ini`. |
| `make frontend-build` / `lint` | Construye Next.js o ejecuta linting. |
| `make clean` | Borra `frontend/node_modules`, `frontend/.next` y `backend/.venv`. |

Ejecutá `make help` en cualquier momento para ver la lista completa con descripciones.

## 3. Flujos operativos recomendados

### 3.1 Preparación inicial
1. `make env` – asegura los archivos de configuración.
2. `make backend-install` y `make frontend-install` – deja listas las dependencias si vas a trabajar fuera de Docker.

### 3.2 Stack completo con Docker (recomendado)
1. `make docker-up` – construye imágenes y levanta Postgres, Redis, pgAdmin, backend y frontend.
2. Navegá a `http://localhost:3000` (frontend) o `http://localhost:8000/docs` (API).
3. `make docker-logs` para inspeccionar servicios específicos o `make docker-up-logs` si querés seguir todo el output al arrancar.
4. `make docker-down` al terminar; usa `make docker-destroy` solo cuando necesites un reset completo de datos (borra los volúmenes `postgres_data`, `redis_data` y `pgadmin_data`).

### 3.3 Desarrollo híbrido (backend/frontend locales + datos en Docker)
1. `make infra-up` – levanta únicamente Postgres y Redis (requeridos por FastAPI).
2. En una terminal: `make backend-dev` (requiere haber corrido `make backend-install`). El servidor FastAPI queda en `http://localhost:8000` con recarga en caliente.
3. En otra terminal: `make frontend-dev` (requiere `make frontend-install`). Next.js queda en `http://localhost:3000` usando Turbopack.
4. Detenés los servicios locales con `Ctrl+C` y la infraestructura con `make infra-down`.

### 3.4 Tests y calidad
- Backend: `make backend-test` ejecuta Pytest siguiendo `backend/pytest.ini`.
- Frontend:
  - `make frontend-build` valida que el proyecto compile igual que en CI/CD.
  - `make lint` aplica las reglas de `eslint-config-next`.

### 3.5 Limpieza y mantenimiento
- `make clean` elimina dependencias locales para forzar instalaciones frescas.
- Volver a crear `.env` o `.env.local` simplemente repitiendo `make env` (no sobrescribe si ya existen).

## 4. Troubleshooting

- **Servicios no levantan**: ejecutá `make docker-ps` para revisar estados y `make docker-logs` para inspeccionar errores específicos.
- **Cambios en dependencias**: vuelve a correr `make backend-install` o `make frontend-install` tras modificar `requirements.txt` o `package.json`.
- **Errores de conexión DB/Redis en desarrollo híbrido**: confirmá que `make infra-up` sigue activo y que `DATABASE_URL`/`REDIS_URL` en `.env` apuntan a `localhost` o al host adecuado según el escenario.
- **Port conflicts**: ajustá los puertos en `docker-compose.yml` o exportá variables antes de `make docker-up` si tu setup requiere otros puertos.

Con este flujo, el Makefile actúa como punto único para levantar la infraestructura, ejecutar los servidores y correr validaciones, facilitando reproducibilidad entre ambientes locales y de CI.

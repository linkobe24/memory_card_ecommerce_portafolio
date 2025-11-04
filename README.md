# 🎮 MemoryCard – E-Commerce Full Stack

> Proyecto full-stack educativo y profesional para portafolio.
> Desarrollado con **Next.js 15.5 + FastAPI + PostgreSQL + Docker Compose**.

---

## 🚀 Descripción general

MemoryCard es una tienda digital de videojuegos que simula un entorno de comercio electrónico completo.  
El objetivo del proyecto es **demostrar dominio técnico y buenas prácticas de ingeniería** desde el diseño de la base de datos hasta la interfaz de usuario y la infraestructura Docker.

---

## 🧱 Stack principal

| Capa                | Tecnología                                                  | Detalle                                                                        |
| ------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------ |
| **Frontend**        | Next.js 15.5, TypeScript, Tailwind CSS, Zustand + TanStack Query | Landing pública, catálogo, carrito, checkout simulado y panel admin. Turbopack habilitado.           |
| **Backend**         | FastAPI, SQLAlchemy async, Pydantic v2                      | API modular con autenticación JWT, CRUD productos, carrito, órdenes y reseñas. |
| **Base de datos**   | PostgreSQL 15                                               | Relacional, persistente (Docker volume).                                       |
| **Infraestructura** | Docker Compose                                              | Orquestación de frontend, backend y DB.                                        |
| **Pagos**           | Stripe Test Mode                                            | Simulación segura de flujo de pago.                                            |
| **Tests**           | Pytest, HTTPX                                               | Casos básicos de autenticación, carrito y pagos.                               |

---

## 🧩 Arquitectura general

┌──────────────┐
│ FRONTEND │ Next.js 15.5 + Turbopack
│ (Port 3000) │
└──────┬───────┘
│ API Calls
┌──────▼───────┐
│ BACKEND │ FastAPI + SQLAlchemy async
│ (Port 8000) │
└──────┬───────┘
│ SQL
┌──────▼───────┐
│ POSTGRESQL │ DB relacional persistente
└──────────────┘

_(Nginx se incluye opcionalmente para entorno productivo o hosting unificado.)_

---

## 🎯 Objetivos de aprendizaje

1. Practicar arquitectura full-stack moderna con Docker.
2. Implementar autenticación JWT y roles (User / Admin).
3. Simular flujo de pago real con Stripe Test Mode.
4. Crear API REST robusta con tests automatizados.
5. Diseñar un frontend atractivo y funcional tipo tienda.

---

## 🧠 Estructura del repositorio

memory_card/
├── backend/
│ ├── app/ # Código FastAPI
│ ├── tests/ # Pytest
│ └── Dockerfile
├── frontend/
│ ├── app/ # Next.js App Router
│ ├── store/ # Zustand
│ ├── context/ # Context API (Auth)
│ └── Dockerfile
├── docker-compose.yml
└── README.md

---

## 🛠️ Cómo ejecutar el proyecto

### Prerrequisitos

- Docker y Docker Compose (para opción recomendada).
- Python 3.11 + `pip` (si deseas correr el backend sin Docker).
- Node.js 20 y `npm` (si deseas correr el frontend sin Docker).

### Opción 1 · Docker Compose (recomendada)

1. Duplicá las variables de entorno si querés personalizarlas:
   ```bash
   cp .env.example .env
   cp frontend/.env.local.example frontend/.env.local
   ```
2. Construí y levantá los servicios:
   ```bash
   docker compose up --build
   ```
3. El frontend queda disponible en `http://localhost:3000` y la API FastAPI en `http://localhost:8000`.
4. Para detener todo:
   ```bash
   docker compose down
   ```

### Opción 2 · Ejecución local (sin Docker)

1. Levantá PostgreSQL y Redis (podés usar Docker igualmente):
   ```bash
   docker compose up postgres redis
   ```
2. Backend (FastAPI):
   ```bash
   cd backend
   cp ../.env.example .env  # Ajustá valores si es necesario
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
3. Frontend (Next.js):
   ```bash
   cd frontend
   cp .env.local.example .env.local  # NEXT_PUBLIC_API_URL debe apuntar al backend
   npm install
   npm run dev
   ```
4. Abrí `http://localhost:3000` para usar la aplicación. La API seguirá en `http://localhost:8000`.

> Tip: Ejecutá los servidores en terminales separadas o usá un process manager (p. ej. `npm run dev` + `uvicorn`) según tu preferencia.

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

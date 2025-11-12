SHELL := /bin/bash

DOCKER_COMPOSE ?= docker compose
BACKEND_DIR ?= backend
FRONTEND_DIR ?= frontend
VENV_DIR ?= $(BACKEND_DIR)/.venv
PYTHON ?= python3
ENV_FILE ?= .env
ENV_EXAMPLE ?= .env.example
FRONTEND_ENV ?= $(FRONTEND_DIR)/.env.local
FRONTEND_ENV_EXAMPLE ?= $(FRONTEND_DIR)/.env.local.example

.DEFAULT_GOAL := help

.PHONY: help env docker-build docker-up docker-up-logs docker-down docker-destroy docker-logs docker-ps infra-up infra-down infra-logs backend-venv backend-install backend-dev backend-test frontend-install frontend-dev frontend-build lint clean

help: ## Muestra los comandos disponibles
	@printf "\nMemoryCard Makefile\n\n"
	@grep -E '^[a-zA-Z0-9_-]+:.*##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*##"; printf "Targets:\n"} {printf "  %-20s %s\n", $$1, $$2}'

env: $(ENV_FILE) $(FRONTEND_ENV) ## Copia los archivos .env si no existen

$(ENV_FILE):
	@if [ ! -f $(ENV_FILE) ]; then \
		cp $(ENV_EXAMPLE) $(ENV_FILE); \
		echo "Creado $(ENV_FILE) desde $(ENV_EXAMPLE)"; \
	else \
		echo "$(ENV_FILE) ya existe, se mantiene"; \
	fi

$(FRONTEND_ENV):
	@if [ ! -f $(FRONTEND_ENV) ]; then \
		cp $(FRONTEND_ENV_EXAMPLE) $(FRONTEND_ENV); \
		echo "Creado $(FRONTEND_ENV) desde $(FRONTEND_ENV_EXAMPLE)"; \
	else \
		echo "$(FRONTEND_ENV) ya existe, se mantiene"; \
	fi

docker-build: ## Construye las imágenes Docker sin levantarlas
	$(DOCKER_COMPOSE) build

docker-up: env ## Levanta todo el stack en segundo plano
	$(DOCKER_COMPOSE) up --build -d

docker-up-logs: env ## Levanta todo el stack y sigue los logs
	$(DOCKER_COMPOSE) up --build

docker-down: ## Detiene los contenedores sin borrar volúmenes
	$(DOCKER_COMPOSE) down

docker-destroy: ## Detiene los contenedores y elimina volúmenes
	$(DOCKER_COMPOSE) down -v

docker-logs: ## Sigue los logs de backend y frontend
	$(DOCKER_COMPOSE) logs -f backend frontend

docker-ps: ## Lista el estado de todos los servicios compose
	$(DOCKER_COMPOSE) ps

infra-up: env ## Levanta solo Postgres y Redis para desarrollo local
	$(DOCKER_COMPOSE) up -d postgres redis

infra-down: ## Detiene Postgres y Redis sin borrar volúmenes
	$(DOCKER_COMPOSE) stop postgres redis

infra-logs: ## Sigue los logs de Postgres y Redis
	$(DOCKER_COMPOSE) logs -f postgres redis

backend-venv: ## Crea el entorno virtual del backend si no existe
	@if [ ! -d $(VENV_DIR) ]; then \
		$(PYTHON) -m venv $(VENV_DIR); \
		echo "Entorno virtual creado en $(VENV_DIR)"; \
	else \
		echo "Ya existe $(VENV_DIR), se reutiliza"; \
	fi

backend-install: backend-venv ## Instala dependencias del backend
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install -r $(BACKEND_DIR)/requirements.txt

backend-dev: env backend-install ## Inicia FastAPI con autoreload
	PYTHONPATH=$(BACKEND_DIR) $(VENV_DIR)/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

backend-test: backend-install ## Ejecuta pytest del backend
	PYTHONPATH=$(BACKEND_DIR) $(VENV_DIR)/bin/pytest -c $(BACKEND_DIR)/pytest.ini

frontend-install: ## Instala dependencias del frontend
	npm install --prefix $(FRONTEND_DIR)

frontend-dev: env frontend-install ## Inicia Next.js (Turbopack)
	npm run dev --prefix $(FRONTEND_DIR)

frontend-build: frontend-install ## Genera el build estático de Next.js
	npm run build --prefix $(FRONTEND_DIR)

lint: ## Ejecuta lint en el frontend
	npm run lint --prefix $(FRONTEND_DIR)

clean: ## Limpia artefactos locales (node_modules, .next y venv)
	rm -rf $(FRONTEND_DIR)/node_modules $(FRONTEND_DIR)/.next $(VENV_DIR)

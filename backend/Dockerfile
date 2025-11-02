FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# copiar todo el codigo de la aplicacion
COPY . .

EXPOSE 8000

# comando para iniciar uvicorn con hot-reload
#--host 0.0.0.0 permite conexiones desde fuera del contenedor
CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

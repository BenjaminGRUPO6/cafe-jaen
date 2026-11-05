# Imagen de producción de un solo servicio (Render): la API también entrega la app.
# Local no la necesita: se usa `python dev.py start`.

# Etapa 1: compila el front-end (PWA)
FROM node:22-slim AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# Etapa 2: API en Python con la app compilada en /app/static
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    STATIC_DIR=/app/static
WORKDIR /app
COPY backend/pyproject.toml ./
COPY backend/src ./src
RUN pip install --no-cache-dir .
COPY backend/alembic.ini ./
COPY backend/migrations ./migrations
COPY backend/scripts ./scripts
COPY --from=frontend /frontend/dist ./static

EXPOSE 8000
CMD ["sh", "scripts/start_server.sh"]

"""Sirve el front-end compilado (PWA) desde la misma API.

Se usa en el despliegue de un solo servicio (Render): la app y la API comparten dominio,
así que no hace falta CORS. En desarrollo local el front-end lo sirve Vite.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.types import Scope

INDEX = "index.html"


class SinglePageApp(StaticFiles):
    """Archivos estáticos con respaldo a index.html para las rutas del front-end (/decision…)."""

    async def get_response(self, path: str, scope: Scope) -> Response:
        # Las rutas /api desconocidas deben responder 404, no la app.
        # En Windows Starlette entrega la ruta con «\\»: se normaliza antes de comparar
        normalized = path.replace("\\", "/")
        if normalized == "api" or normalized.startswith("api/"):
            raise HTTPException(status_code=404)
        try:
            return await super().get_response(path, scope)
        except HTTPException as error:
            if error.status_code != 404:
                raise
            return await super().get_response(INDEX, scope)


def mount_single_page_app(app: FastAPI, directory: str) -> None:
    """Monta la app en «/». Debe llamarse después de registrar las rutas de la API."""
    folder = Path(directory)
    if not (folder / INDEX).is_file():
        raise RuntimeError(f"No se encontró {INDEX} en {folder}: compila el front-end primero")
    app.mount("/", SinglePageApp(directory=folder, html=True), name="frontend")

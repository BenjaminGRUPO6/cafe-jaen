# 0008 — Herramientas de desarrollo simples: dev.py, SQLite en local y Dependabot

**Estado:** aceptada (v1.1, 04/11/2026)

**Contexto.** Para levantar la app hacía falta Docker (PostgreSQL), `make` (que no existe en
Windows) y varios comandos en dos terminales. Esto dificultaba mostrar avances, incorporar al
compañero en otra computadora y mantener las dependencias al día.

**Decisión.**
- `dev.py` en la raíz: un solo script con la biblioteca estándar de Python que hace `setup`,
  `demo`, `start` (API y app juntas), `test`, `check`, `admin` y `reset`, igual en Windows,
  macOS y Linux. El `Makefile` queda como atajo opcional que llama a `dev.py`.
- **SQLite por defecto** en desarrollo (`sqlite:///./cafe_jaen.db`): un archivo, nada que
  instalar. PostgreSQL se mantiene para producción (`DATABASE_URL`, `docker-compose.yml`). El
  código no cambia porque la persistencia está detrás de puertos y SQLAlchemy.
- `setup` crea `backend/.env` con un `JWT_SECRET` aleatorio: ningún secreto se escribe a mano.
- **Dependabot** abre cada semana un PR por dependencia desactualizada (pip, npm y GitHub
  Actions); la CI lo valida antes de aceptarlo.
- `.python-version` (3.12) y `frontend/.nvmrc` (22) fijan las versiones esperadas.

**Consecuencias.** De cero a la app corriendo: `python dev.py setup`, `python dev.py demo`,
`python dev.py start`. SQLite no se usa para el experimento (allí va PostgreSQL con copias de
seguridad, HU10). Las pruebas siguen usando SQLite en memoria, como antes.

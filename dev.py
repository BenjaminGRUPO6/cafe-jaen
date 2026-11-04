#!/usr/bin/env python3
"""Tareas del proyecto en un solo comando, iguales en Windows, macOS y Linux.

Solo usa la biblioteca estándar de Python, así que funciona antes de instalar nada.

    python dev.py setup     instala todo (una sola vez)
    python dev.py demo      prepara la base de datos con datos de demostración
    python dev.py start     levanta la API y la app juntas (Ctrl+C para detener)
    python dev.py test      pruebas del backend y del frontend
    python dev.py check     todo lo que revisa la integración continua (CI)
    python dev.py admin 9XXXXXXXX   crea una cuenta del equipo (rol administrador)
    python dev.py reset     borra la base de datos local para empezar de cero
"""

from __future__ import annotations

import argparse
import os
import secrets
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
VENV = BACKEND / ".venv"
IS_WINDOWS = os.name == "nt"
LOCAL_DB = BACKEND / "cafe_jaen.db"

# Modo demostración: precio sintético que se mueve cada minuto y bolsa «abierta» todo el día
DEMO_ENV = {
    "QUOTATION_SOURCES": '["demo"]',
    "MARKET_OPENS": "00:00",
    "MARKET_CLOSES": "23:59",
}


def venv_bin(name: str) -> str:
    folder = "Scripts" if IS_WINDOWS else "bin"
    suffix = ".exe" if IS_WINDOWS else ""
    return str(VENV / folder / f"{name}{suffix}")


def npm() -> str:
    return "npm.cmd" if IS_WINDOWS else "npm"


def run(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> None:
    """Ejecuta un comando y se detiene con un mensaje claro si falla."""
    print(f"\n→ {' '.join(command)}  ({cwd.name})", flush=True)
    full_env = {**os.environ, "PYTHONPATH": "src", **(env or {})}
    result = subprocess.run(command, cwd=cwd, env=full_env, check=False)
    if result.returncode != 0:
        sys.exit(f"\n✗ Falló: {' '.join(command)}")


def require(tool: str, hint: str) -> None:
    if shutil.which(tool) is None:
        sys.exit(f"✗ No se encontró «{tool}». {hint}")


def ensure_env_file() -> None:
    """Crea backend/.env desde .env.example con un secreto aleatorio (solo si no existe)."""
    target = BACKEND / ".env"
    if target.exists():
        return
    template = (ROOT / ".env.example").read_text(encoding="utf-8")
    secret = secrets.token_urlsafe(48)
    content = template.replace("cambia-esto-por-un-secreto-largo-y-aleatorio", secret)
    target.write_text(content, encoding="utf-8")
    print("✓ Se creó backend/.env (SQLite local y un JWT_SECRET aleatorio)")


MIN_NODE = (20, 0)


def check_node_version() -> None:
    """Las herramientas del front-end (Vite 6, Vitest 3, ESLint 9) funcionan desde Node 20;
    con una versión menor npm puede omitir binarios nativos y el front-end no arranca."""
    require("node", "Instala Node.js 22 LTS desde https://nodejs.org")
    raw = subprocess.run(
        ["node", "--version"], check=True, capture_output=True, text=True
    ).stdout.strip()
    parts = tuple(int(x) for x in raw.lstrip("v").split(".")[:2])
    if parts < MIN_NODE:
        sys.exit(
            f"✗ Tienes Node {raw}; se necesita Node 20 o superior. "
            "Instala Node 22 LTS desde https://nodejs.org, abre una terminal nueva "
            "y vuelve a ejecutar: python dev.py setup"
        )


def cmd_setup(_: argparse.Namespace) -> None:
    require(npm(), "Instala Node.js 22 LTS desde https://nodejs.org")
    check_node_version()
    # Reinstala desde cero si quedó una instalación incompleta de una versión anterior de Node
    node_modules = FRONTEND / "node_modules"
    if node_modules.exists():
        shutil.rmtree(node_modules)
    if not VENV.exists():
        run([sys.executable, "-m", "venv", str(VENV)], ROOT)
    run([venv_bin("python"), "-m", "pip", "install", "--upgrade", "pip"], BACKEND)
    run([venv_bin("python"), "-m", "pip", "install", "-e", ".[dev]"], BACKEND)
    run([npm(), "ci"], FRONTEND)
    ensure_env_file()
    print("\n✓ Listo. Siguiente paso: python dev.py demo")


def migrate() -> None:
    run([venv_bin("alembic"), "upgrade", "head"], BACKEND)


def cmd_demo(_: argparse.Namespace) -> None:
    ensure_env_file()
    migrate()
    run([venv_bin("python"), "scripts/seed_demo_data.py"], BACKEND)
    run([venv_bin("python"), "scripts/run_daily_cycle.py"], BACKEND, DEMO_ENV)
    print("\n✓ Datos de demostración listos. Código de invitación: DEMO-0001")
    print("  Siguiente paso: python dev.py start")


def cmd_start(args: argparse.Namespace) -> None:
    check_node_version()
    ensure_env_file()
    migrate()
    api_env = {**os.environ, "PYTHONPATH": "src", **({} if args.real else DEMO_ENV)}
    api = subprocess.Popen(
        [venv_bin("uvicorn"), "main:app", "--reload", "--app-dir", "src", "--port", "8000"],
        cwd=BACKEND,
        env=api_env,
    )
    web = subprocess.Popen([npm(), "run", "dev", "--", "--port", "5173"], cwd=FRONTEND)
    mode = "precios reales (Yahoo y Stooq)" if args.real else "demostración (precio sintético)"
    print(f"\n☕ Café Jaén en modo {mode}")
    print("   App: http://localhost:5173   ·   API: http://localhost:8000/docs")
    print("   Ctrl+C para detener las dos.\n", flush=True)
    try:
        while api.poll() is None and web.poll() is None:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        # Detiene ambos procesos aunque uno de ellos haya fallado
        for process in (api, web):
            if process.poll() is None:
                if IS_WINDOWS:
                    process.terminate()
                else:
                    process.send_signal(signal.SIGINT)
        for process in (api, web):
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()


def cmd_test(_: argparse.Namespace) -> None:
    run([venv_bin("pytest"), "-q"], BACKEND)
    run([npm(), "test"], FRONTEND)


def cmd_check(_: argparse.Namespace) -> None:
    run([venv_bin("ruff"), "check", "."], BACKEND)
    run([venv_bin("ruff"), "format", "--check", "."], BACKEND)
    run([venv_bin("mypy")], BACKEND)
    run([venv_bin("lint-imports")], BACKEND)
    run([venv_bin("pytest"), "-q", "--cov-fail-under=80"], BACKEND)
    run([npm(), "run", "lint"], FRONTEND)
    run([npm(), "test"], FRONTEND)
    run([npm(), "run", "build"], FRONTEND)
    print("\n✓ Todo en verde: igual que la integración continua")


def cmd_admin(args: argparse.Namespace) -> None:
    ensure_env_file()
    migrate()
    run([venv_bin("python"), "scripts/create_admin.py", "--phone", args.phone], BACKEND)


def cmd_reset(_: argparse.Namespace) -> None:
    if LOCAL_DB.exists():
        LOCAL_DB.unlink()
        print(f"✓ Se borró {LOCAL_DB.relative_to(ROOT)}. Ejecuta: python dev.py demo")
    else:
        print("No hay base de datos local que borrar.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("setup", help="instala todo (una sola vez)").set_defaults(func=cmd_setup)
    commands.add_parser("demo", help="datos de demostración").set_defaults(func=cmd_demo)
    start = commands.add_parser("start", help="levanta la API y la app")
    start.add_argument("--real", action="store_true", help="usa precios reales en vez de la demo")
    start.set_defaults(func=cmd_start)
    commands.add_parser("test", help="pruebas").set_defaults(func=cmd_test)
    commands.add_parser("check", help="todo lo que revisa la CI").set_defaults(func=cmd_check)
    admin = commands.add_parser("admin", help="crea una cuenta del equipo")
    admin.add_argument("phone", help="número de celular de 9 dígitos")
    admin.set_defaults(func=cmd_admin)
    commands.add_parser("reset", help="borra la base de datos local").set_defaults(func=cmd_reset)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

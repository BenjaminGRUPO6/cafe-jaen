# ☕ Café Jaén

Aplicación web con agentes inteligentes para mejorar la percepción del valor de mercado en los
caficultores de Jaén (tesis UPAO, 2026).

El caficultor ve **en vivo, como en una pantalla de bolsa, a cuánto se vende el café en el
mundo** (bolsa de Nueva York, consultada en varias webs a la vez) y en **soles por quintal**, su
gráfico, un **pronóstico a 7 días**, la recomendación **«¿Vendo ahora o espero?»** y un
**asesor** en lenguaje sencillo. Así deja de decidir por el boca a boca. Detrás, seis agentes
coordinados por un supervisor mantienen los datos al día sin intervención humana.

> **Versión:** v1.0 (MVP, plan XP v3.0) · **Metodología:** Extreme Programming (XP) · **Arquitectura:** monolito modular hexagonal

---

## Contenido

1. [Qué hace el MVP](#qué-hace-el-mvp)
2. [Arquitectura en 1 minuto](#arquitectura-en-1-minuto)
3. [Cómo ejecutarlo](#cómo-ejecutarlo)
4. [Estructura del repositorio](#estructura-del-repositorio)
5. [Convenciones](#convenciones)
6. [Calidad y pruebas](#calidad-y-pruebas)
7. [Documentación](#documentación)

---

## Qué hace el MVP

| Historia | Qué ve el caficultor | Agente |
|---|---|---|
| HU01 | Registro con **código de invitación** (solo grupo experimental) y consentimiento | — |
| HU02 | Precio de la bolsa consultado **cada minuto en varias webs**, consolidado por mediana | Recolector |
| HU03 | **Precio en vivo tipo bolsa**: ¢USD/lb y S/ por quintal, sube/baja, hora y fuentes; se actualiza solo | Analista |
| HU04 | Gráfico de **hoy** (minuto a minuto), 30 y 90 días | Analista |
| HU05 | **¿Vendo ahora o espero?** con su motivo y su porcentaje de acierto | Estratega de venta |
| HU06 | Pronóstico a 7 días con su rango | Predictor |
| HU07 | Coordinación de agentes y trazas | Supervisor |
| HU08 | Preguntas en lenguaje natural sin datos inventados | Asesor |
| HU09 | Letra grande, se instala en el celular y funciona sin señal | — |
| HU10–11 | Producción, manual e inducción | — |
| HU12 | **Precio estimado en Jaén** por tipo de café: la bolsa × el porcentaje que pagan las cooperativas (el equipo anota sus precios en la pantalla «Equipo») | Analista |

> **Sobre el «tiempo real»:** los datos de la bolsa ICE al segundo requieren licencia; las webs
> gratuitas publican con algunos minutos de retraso. La app muestra siempre la **hora de la
> cotización** ([decisión 0006](docs/decisiones/0006-varias-fuentes-y-sse.md)).

La medición de los indicadores de la tesis (TAI, NCP, NPP) **no** se hace en la app: se usan los
instrumentos del Anexo 1, igual para el grupo experimental y el de control
([decisión 0003](docs/decisiones/0003-medicion-fuera-de-la-app.md)).

## Arquitectura en 1 minuto

![Arquitectura hexagonal](docs/img/arquitectura-hexagonal.png)

- **Módulos** (`backend/src/`): `identity`, `market`, `forecasting`, `decision`, `advisor`, `orchestration` y el kernel `shared`.
- **Cada módulo** tiene tres capas: `domain` (reglas del negocio, sin frameworks) → `application`
  (casos de uso y agentes) → `infrastructure` (FastAPI, SQLAlchemy, webs de la bolsa, BCRP, LangGraph, LLM).
- **Los módulos no se importan entre sí.** Se comunican con mensajes `AgentMessage` a través del
  **Agente Supervisor**. Estas reglas las verifica `import-linter` en cada commit.
- **`main.py`** es la raíz de composición: el único lugar donde se crean los adaptadores.

| Agente | Módulo | Qué hace |
|---|---|---|
| Supervisor | `orchestration` | Recibe cada solicitud, la entrega al agente correcto y registra la traza |
| Recolector | `market` | Cada minuto consulta varias webs del precio de Nueva York, publica la mediana, descarta la web discrepante y guarda; tipo de cambio del BCRP |
| Analista | `market` | Convierte a S/ por quintal, calcula la variación frente al cierre anterior, arma el gráfico y estima el precio en Jaén con los precios de cooperativas |
| Predictor | `forecasting` | Elige entre ELM y modelo base (menor MAPE) y pronostica 7 días hábiles |
| Estratega de venta | `decision` | Con el precio en vivo y el pronóstico recomienda vender ahora, esperar o «sin señal clara», explicando por qué |
| Asesor | `advisor` | Responde preguntas pidiendo los datos a los otros agentes (con salvaguarda contra números inventados) |

Más detalle en [docs/arquitectura.md](docs/arquitectura.md).

## Cómo ejecutarlo

Requisitos: Python 3.11+, Node 22, Docker (para PostgreSQL).

```bash
cp .env.example backend/.env      # y cambia JWT_SECRET
docker compose up -d db           # PostgreSQL local
make setup                        # entorno de Python + dependencias del front-end
make demo                         # (opcional) datos SINTÉTICOS para probar sin internet
make api-demo                     # API SIN internet: precio sintético que se mueve cada minuto
make web                          # App en http://localhost:5173
```

Con los datos de demostración, crea tu cuenta con el código **DEMO-0001** y ejecuta `make cycle`
para tener pronóstico y recomendación. Para anotar precios de cooperativas, crea una cuenta del
equipo con `make admin PHONE=9XXXXXXXX` e ingresa con ella: aparece la opción «Equipo».

Para datos reales: `make api` (consulta Yahoo Finance y Stooq con la bolsa abierta),
`PYTHONPATH=src python scripts/load_price_history.py --years 5`, `make cycle` (primer
pronóstico), `make spike` (elegir las webs) y `make backtest` (acierto de la regla de venta).
Ver [docs/operacion.md](docs/operacion.md).

## Estructura del repositorio

```
cafe-jaen/
├── backend/
│   ├── src/
│   │   ├── shared/          AgentMessage, contrato de agentes, puertos comunes
│   │   ├── identity/        usuarios y códigos de invitación
│   │   ├── market/          agentes Recolector y Analista (precio mundial en vivo)
│   │   ├── forecasting/     agente Predictor (ELM y modelo base)
│   │   ├── decision/        agente Estratega de venta («¿vendo o espero?»)
│   │   ├── advisor/         agente Asesor
│   │   ├── orchestration/   agente Supervisor (LangGraph) y ciclo diario
│   │   └── main.py          raíz de composición
│   ├── migrations/          Alembic (una migración por iteración)
│   ├── scripts/             spike de fuentes, carga de histórico, prueba retrospectiva, datos demo
│   └── tests/               unit/ · integration/ · acceptance/
├── frontend/src/
│   ├── shared/              cliente API, sesión, componentes, textos en español
│   └── features/            auth · live (precio, estimado en Jaén y gráfico) · decision · forecast · advisor · admin
└── docs/                    arquitectura, decisiones, XP, operación
```

## Convenciones

- **Código en inglés; comentarios y docstrings en español.** Los textos que ve el caficultor
  están en `frontend/src/shared/texts/es.ts`.
- Ramas `feature/huXX-descripcion`, commits `tipo(módulo): descripción en español`
  (p. ej., `feat(market): consolida el precio de varias webs por mediana`).
- Detalle completo en [docs/estandar-de-codigo.md](docs/estandar-de-codigo.md).

## Calidad y pruebas

```bash
make test   # pytest (unitarias, integración, aceptación) + Vitest
make load   # prueba de carga con 30 usuarios (Locust)
make lint   # ruff, mypy, import-linter, eslint, prettier
```

- **TDD**: las reglas del dominio se escribieron prueba primero.
- Cada prueba de aceptación del backlog (PA-xx-x) está identificada en las pruebas; ver
  [docs/xp/trazabilidad.md](docs/xp/trazabilidad.md).
- CI en GitHub Actions: estilo, tipos, contratos de arquitectura, pruebas (cobertura ≥ 80 %) y build.

## Documentación

| Documento | Contenido |
|---|---|
| [docs/arquitectura.md](docs/arquitectura.md) | Capas, módulos, agentes, flujo de una consulta |
| [docs/metafora.md](docs/metafora.md) | Metáfora del sistema (XP) |
| [docs/tarjetas-crc.md](docs/tarjetas-crc.md) | Tarjetas CRC de las clases principales |
| [docs/estandar-de-codigo.md](docs/estandar-de-codigo.md) | Idioma, nombres, buenas prácticas, Git |
| [docs/decisiones/](docs/decisiones/) | Registro de decisiones de arquitectura (ADR) |
| [docs/xp/trazabilidad.md](docs/xp/trazabilidad.md) | Historia → archivos → pruebas |
| [docs/xp/iteraciones.md](docs/xp/iteraciones.md) | Qué se entregó en cada iteración (plan, tareas, pruebas de aceptación) |
| [docs/xp/tareas.md](docs/xp/tareas.md) | Las 37 tareas de ingeniería y su entregable |
| [docs/manual/](docs/manual/) | Manual de usuario y guía de inducción (Word) |
| [Reporte de pruebas](docs/xp/iteracion-3/Reporte_de_pruebas_Cafe_Jaen.docx) | Resultados de pruebas, carga y defectos corregidos |
| [CHANGELOG.md](CHANGELOG.md) | Cambios de cada versión |
| [docs/operacion.md](docs/operacion.md) | Despliegue, carga de datos, respaldos |

**Equipo:** Chavez Canaquiri, Jhon Xavier · Reyes Guerrero, Luis Benjamin — Asesor: Cieza Mostacero, Segundo Edwin.

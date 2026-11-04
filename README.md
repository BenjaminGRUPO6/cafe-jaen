# ☕ Café Jaén

Aplicación web con agentes inteligentes para mejorar la percepción del valor de mercado en los
caficultores de Jaén (tesis UPAO, 2026).

El caficultor ve **en vivo, como en una pantalla de bolsa, a cuánto se vende el café en el
mundo** (bolsa de Nueva York, consultada en varias webs a la vez), lo que se paga **en Jaén** por
su tipo de café, el gráfico del precio, un **pronóstico a 7 días**, la recomendación **«¿Vendo
ahora o espero?»** y un **asesor** que responde en lenguaje sencillo. Detrás, seis agentes
coordinados por un supervisor mantienen los datos al día sin intervención humana.

> **Versión:** v1.1 (plan XP v4.0) · **Metodología:** Extreme Programming (XP) ·
> **Arquitectura:** monolito modular hexagonal + sistema multiagente con supervisor

| Integrante | GitHub | Rol en XP | Lidera |
|---|---|---|---|
| Chavez Canaquiri, Jhon Xavier | [jhon1212-beep](https://github.com/jhon1212-beep) | Programador · encargado de seguimiento | Precio mundial en vivo, pronóstico, «¿Vendo?», animaciones |
| Reyes Guerrero, Luis Benjamin | [BenjaminGRUPO6](https://github.com/BenjaminGRUPO6) | Programador · entrenador (coach) | Usuarios, supervisor, asesor, interfaz, plataforma |

**Asesor:** Cieza Mostacero, Segundo Edwin.

<p>
  <img src="docs/img/capturas/02-precio.png" width="200" alt="Precio de la bolsa en vivo">
  <img src="docs/img/capturas/06-pronostico-jaen.png" width="200" alt="Pronóstico a 7 días en la bolsa y en Jaén">
  <img src="docs/img/capturas/05-vendo.png" width="200" alt="¿Vendo ahora o espero?">
  <img src="docs/img/capturas/07-asesor.png" width="200" alt="Asesor">
</p>

---

## Contenido

1. [Qué hace la aplicación](#qué-hace-la-aplicación)
2. [Cómo se relaciona con los indicadores de la tesis](#cómo-se-relaciona-con-los-indicadores-de-la-tesis)
3. [Arquitectura](#arquitectura)
4. [Estructura del repositorio](#estructura-del-repositorio)
5. [Tecnologías](#tecnologías)
6. [Cómo ejecutarlo en tu computadora (paso a paso)](#cómo-ejecutarlo-en-tu-computadora-paso-a-paso)
7. [Subirlo a GitHub como evidencia](#subirlo-a-github-como-evidencia)
8. [Calidad, pruebas y criterios de aceptación](#calidad-pruebas-y-criterios-de-aceptación)
9. [Plan XP y división del trabajo](#plan-xp-y-división-del-trabajo)
10. [Convenciones de código](#convenciones-de-código)
11. [Trabajo futuro](#trabajo-futuro)
12. [Documentación](#documentación)

---

## Qué hace la aplicación

| Historia | Qué ve o hace el caficultor | Agente |
|---|---|---|
| HU01 | Registro con **código de invitación** (solo grupo experimental) y consentimiento informado | — |
| HU02 | Precio de la bolsa consultado **cada minuto en varias webs**, consolidado por mediana | Recolector |
| HU03 | **Precio en vivo tipo bolsa**: ¢USD/lb y S/ por quintal, sube/baja, hora y fuentes; se actualiza solo | Analista |
| HU04 | Gráfico de **hoy** (minuto a minuto), 30 y 90 días, con máximo, mínimo y variación | Analista |
| HU05 | **¿Vendo ahora o espero?** con su motivo en números y su porcentaje de acierto | Estratega de venta |
| HU06 | Pronóstico a 7 días con su rango, **en la bolsa y estimado en Jaén** por tipo de café | Predictor |
| HU07 | Coordinación de agentes con mensajes estándar y trazas | Supervisor |
| HU08 | Preguntas en lenguaje natural, sin precios inventados | Asesor |
| HU09 | Letra grande, se instala en el celular y muestra el último precio sin señal | — |
| HU10–11 | Producción, manual de usuario e inducción | — |
| HU12 | **Precio estimado en Jaén**: la bolsa × el porcentaje que pagan las cooperativas (el equipo anota sus precios en «Equipo») | Analista |
| HU15 | Interfaz dinámica: colores vivos, precio que rueda al cambiar, animaciones que responden al toque | — |
| HU16 | Ejecución local en un paso (Windows, macOS, Linux) y dependencias que se actualizan solas | — |

> **Sobre el «tiempo real»:** los datos de la bolsa ICE al segundo requieren licencia; las webs
> gratuitas publican con algunos minutos de retraso. La app muestra siempre la **hora de la
> cotización** ([decisión 0006](docs/decisiones/0006-varias-fuentes-y-sse.md)).

## Cómo se relaciona con los indicadores de la tesis

Los indicadores se miden **fuera de la app**, con los mismos instrumentos para el grupo
experimental (GE) y el grupo control (GC) ([decisión 0003](docs/decisiones/0003-medicion-fuera-de-la-app.md)).
La app es la intervención que recibe solo el GE.

| Indicador | Cómo se mide | Qué hace la app para mejorarlo |
|---|---|---|
| **TAI** = tf − ti (minutos) | Ficha de observación con cronómetro | El precio aparece al abrir la app y se actualiza solo cada minuto |
| **NCP**ᵢ = aciertos / preguntas × 100 | Cuestionario de conocimiento del precio | Precio de la bolsa, variación y precio estimado en Jaén por tipo de café |
| **TPP** = [1 − \|Pp − Pr\| / Pr] × 100 | Ficha: precio predicho vs. precio real (S/ por quintal de pergamino) | Pronóstico a 7 días **en Jaén**, en la misma unidad que se predice ([decisión 0009](docs/decisiones/0009-pronostico-en-jaen.md)) |
| Usabilidad (SUS) | Cuestionario SUS, solo al GE | — |

El acceso es solo con código de invitación (uno por participante del GE), así el GC no puede
entrar a la app.

## Arquitectura

### Monolito modular hexagonal

Una sola aplicación y una sola base de datos, dividida en **módulos independientes**. Cada
módulo tiene tres capas y las dependencias apuntan siempre hacia adentro:

```
infrastructure  ──▶  application  ──▶  domain
(FastAPI, SQLAlchemy,   (casos de uso      (reglas del negocio,
 webs de la bolsa,       y agentes)          sin frameworks; define
 LangGraph, LLM)                             los puertos)
```

![Arquitectura hexagonal](docs/img/arquitectura-hexagonal.png)

Tres contratos de [`import-linter`](backend/.importlinter) lo vigilan en cada commit y en la CI:

| Contrato | Qué obliga |
|---|---|
| Capas hexagonales | `infrastructure → application → domain`: el dominio no conoce FastAPI, la base de datos ni las webs |
| Módulos independientes | `identity`, `market`, `forecasting`, `decision`, `advisor` y `orchestration` no se importan entre sí: hablan con mensajes `AgentMessage` |
| Kernel compartido | `shared` no depende de ningún módulo |

Gracias a esto, cambiar Yahoo por otra web o SQLite por PostgreSQL es cambiar un adaptador, sin
tocar las reglas del negocio.

### Cómo funciona

```mermaid
flowchart LR
    subgraph Celular["Celular del caficultor (PWA React)"]
        UI["Precio · Gráfico · ¿Vendo? · 7 días · Asesor"]
    end
    subgraph Servidor["Servidor: monolito FastAPI"]
        API["Routers de cada módulo"]
        SUP["Supervisor (LangGraph)"]
        REC["Recolector"]
        ANA["Analista"]
        PRE["Predictor"]
        EST["Estratega de venta"]
        ASE["Asesor"]
        PLAN["Planificador (APScheduler)"]
    end
    DB[("SQLite en local /<br/>PostgreSQL en producción")]
    WEB["Yahoo · Stooq (bolsa de NY)<br/>BCRP (tipo de cambio)"]

    UI -- "HTTPS + token" --> API
    API -- "precio en vivo (SSE)" --> UI
    API --> SUP
    PLAN -- "cada minuto y 14:05" --> SUP
    SUP -- "REQUEST / INFORM / FAILURE" --> REC & ANA & PRE & EST & ASE
    REC --> WEB
    REC & ANA & PRE --> DB
```

| Agente | Módulo | Qué hace |
|---|---|---|
| Supervisor | `orchestration` | Recibe cada pedido y lo envía al agente correcto; registra la traza |
| Recolector | `market` | Consulta varias webs, publica la mediana y descarta la que discrepa |
| Analista | `market` | Precio en S/ por quintal, variación, histórico y estimado en Jaén |
| Predictor | `forecasting` | Pronóstico a 7 días con ELM y modelo base; elige el de menor error (MAPE) |
| Estratega de venta | `decision` | «Vender ahora», «Esperar» o «Sin señal clara», con umbral de 3 % |
| Asesor | `advisor` | Responde preguntas usando los datos de los otros agentes, sin inventar números |

**Los tres flujos principales:**

1. **Precio en vivo (cada minuto, lunes a viernes):** planificador → Recolector → varias webs →
   mediana validada → `live_quotes` → el celular la recibe por SSE y los dígitos del precio ruedan.
2. **Ciclo diario (14:05, hora de Lima):** cierre del día → histórico → nuevo pronóstico →
   recomendación lista.
3. **Consulta del caficultor:** pantalla → API → Supervisor → Estratega o Asesor → respuesta
   `INFORM` (o `FAILURE` controlado, nunca un error 500).

Detalle completo, diagramas y propiedades de agente inteligente en
[docs/arquitectura.md](docs/arquitectura.md).

## Estructura del repositorio

```
cafe-jaen/
├── dev.py                         ← tareas en un comando (Windows, macOS y Linux)
├── backend/                       ← MONOLITO (FastAPI + Python)
│   ├── src/
│   │   ├── main.py                ← raíz de composición: crea adaptadores y los inyecta
│   │   ├── shared/                ← kernel: AgentMessage, contrato de agentes, configuración
│   │   ├── identity/              ← registro, ingreso, roles
│   │   ├── market/                ← precio en vivo y estimado en Jaén (Recolector, Analista)
│   │   ├── forecasting/           ← pronóstico (Predictor)
│   │   ├── decision/              ← «¿Vendo ahora o espero?» (Estratega)
│   │   ├── advisor/               ← asesor (Asesor)
│   │   └── orchestration/         ← supervisor (LangGraph) y planificador
│   ├── migrations/                ← Alembic 0001–0003
│   ├── scripts/                   ← demo, admin, ciclo diario, spike, backtest, carga
│   ├── tests/                     ← unit/ · integration/ · acceptance/ · load/
│   └── .importlinter              ← contratos de arquitectura
├── frontend/                      ← PWA (React + Vite + Framer Motion)
│   └── src/
│       ├── features/              ← una carpeta por pantalla
│       │   ├── live/              ← precio en vivo, estimado en Jaén, gráfico
│       │   ├── forecast/          ← pronóstico (bolsa y Jaén)
│       │   ├── decision/  advisor/  admin/  auth/
│       └── shared/
│           ├── api/               ← cliente HTTP y flujo en vivo (SSE)
│           ├── motion/            ← animaciones: Ticker, Sparkline, Reveal, Segmented…
│           ├── components/  hooks/  auth/
│           ├── texts/es.ts        ← todos los textos que ve el caficultor
│           └── styles.css         ← paleta «Cosecha» y diseño
├── docs/                          ← arquitectura, decisiones (ADR), XP, paleta, manual
├── .github/                       ← CI y Dependabot
├── docker-compose.yml             ← opcional: PostgreSQL + API como en producción
└── Makefile                       ← atajos opcionales (llaman a dev.py)
```

Cada módulo del backend repite las mismas capas. Ejemplo, `market`:

```
market/
├── domain/          live_price.py · consensus.py · price_validator.py · market_hours.py
│   │                local_price.py · quintal_price.py
│   └── ports/       QuotationSource · PriceRepository   ← interfaces
├── application/     collect_prices.py · get_live_price.py · get_price_history.py · record_local_price.py
│   └── agents/      collector_agent.py (Recolector) · analyst_agent.py (Analista)
└── infrastructure/
    ├── sources/     yahoo · stooq · demo · bcrp           ← adaptadores de las webs
    ├── persistence/ repositorios SQLAlchemy
    └── api/         market_router.py (/prices/live, /history, /stream, /admin/local-prices)
```

## Tecnologías

| Capa | Herramienta | Por qué |
|---|---|---|
| Backend | Python 3.12, FastAPI, Pydantic | API tipada y documentada sola en `/docs` |
| Agentes | LangGraph | Grafo del supervisor: un nodo por agente |
| Datos | SQLAlchemy + Alembic; **SQLite** en local, **PostgreSQL** en producción | Sin instalar nada para desarrollar |
| Pronóstico | NumPy (ELM y modelo base) | Liviano y explicable |
| Planificador | APScheduler | Cada minuto y ciclo diario |
| Frontend | React 19, Vite 6, TypeScript, Recharts, Framer Motion | PWA instalable y rápida en 3G; Vite 6 corre desde Node 20 |
| Diseño | Framer Motion, Bricolage Grotesque, Atkinson Hyperlegible Next | Interfaz viva y legible al sol ([paleta](docs/paleta.md)) |
| Calidad | pytest, Vitest, ruff, mypy, import-linter, ESLint, Prettier | Las mismas revisiones en local y en la CI |
| Mantenimiento | `dev.py`, GitHub Actions, Dependabot | Un comando para todo y actualizaciones semanales validadas |

**Simplificado en v1.1** ([decisión 0008](docs/decisiones/0008-herramientas-simples.md)):
- **Sin Docker en local:** SQLite por defecto.
- **Sin `make` obligatorio:** `dev.py` funciona también en Windows.
- **Sin secretos escritos a mano:** el `setup` los genera.
- **Dependencias al día:** Dependabot abre los PR de actualización.

## Cómo ejecutarlo en tu computadora (paso a paso)

### 1. Instala los requisitos (una sola vez)

| Programa | Versión | Descarga |
|---|---|---|
| Python | 3.11 o más nuevo (recomendado 3.12) | https://www.python.org/downloads/ (en Windows marca «Add python.exe to PATH») |
| Node.js | 20 o 22 (probado con 22.11 y 22.22) | https://nodejs.org |
| Git | cualquiera reciente | https://git-scm.com |

Comprueba en una terminal (PowerShell, Terminal o la de VS Code):

```bash
python --version     # en macOS/Linux puede ser: python3 --version
node --version
git --version
```

### 2. Descarga el proyecto

```bash
git clone https://github.com/<usuario>/cafe-jaen.git
cd cafe-jaen
```

(O descomprime el `.zip` y abre una terminal dentro de la carpeta `cafe-jaen`.)

### 3. Instala las dependencias

```bash
python dev.py setup
```

- **Qué hace:** crea el entorno de Python (`backend/.venv`), instala el backend y el frontend, y crea `backend/.env` con un secreto aleatorio.
- **Tiempo:** tarda unos minutos la primera vez.
- **Atajos:** en macOS/Linux usa `python3` si `python` no existe; en Windows también funciona `py dev.py setup`.

### 4. Carga los datos de demostración

```bash
python dev.py demo
```

Carga 2 años de precios sintéticos, precios de cooperativas de ejemplo, el primer pronóstico y la
recomendación. Crea el código de invitación **DEMO-0001**.

### 5. Levanta la aplicación

```bash
python dev.py start
```

- Abre **http://localhost:5173** en el navegador; para verla como en el celular, usa el modo dispositivo con F12.
- Toca «¿Primera vez? Crea tu cuenta», usa el código **DEMO-0001** y cualquier celular de 9 dígitos.
- En modo demostración el precio cambia cada minuto, aunque no haya internet ni la bolsa esté abierta.
- La documentación de la API está en http://localhost:8000/docs.
- Para detener todo, presiona **Ctrl+C**.

### Comandos disponibles

| Comando | Qué hace |
|---|---|
| `python dev.py setup` | Instala todo (una sola vez) |
| `python dev.py demo` | Prepara los datos de demostración |
| `python dev.py start` | API + app en modo demostración |
| `python dev.py start --real` | API + app con precios reales (Yahoo y Stooq; necesita internet) |
| `python dev.py admin 9XXXXXXXX` | Crea una cuenta del equipo para anotar precios de cooperativas («Equipo») |
| `python dev.py test` | Pruebas del backend y del frontend |
| `python dev.py check` | Todo lo que revisa la CI (estilo, tipos, arquitectura, pruebas, build) |
| `python dev.py reset` | Borra la base de datos local para empezar de cero |

En macOS/Linux también existen atajos con `make` (`make start`, `make check`, `make backtest`…).

### Problemas frecuentes

| Problema | Solución |
|---|---|
| `python` no se reconoce (Windows) | Reinstala Python marcando «Add python.exe to PATH» o usa `py dev.py …` |
| `npm` no se reconoce | Instala Node.js 22 LTS y abre una terminal nueva |
| `Cannot find native binding` | Instalación incompleta de `node_modules`: vuelve a ejecutar `python dev.py setup` (la borra y la reinstala) |
| Aviso `npm warn EBADENGINE eslint-visitor-keys` | Es solo un aviso de una herramienta de revisión de código; no afecta a la app |
| El puerto 8000 o 5173 está ocupado | Cierra la otra app que lo usa, o reinicia la computadora |
| «Código no válido» al registrarte | Cada código sirve una sola vez: ejecuta `python dev.py reset` y `python dev.py demo` |
| No aparece el «Precio estimado en Jaén» | Ejecuta `python dev.py demo` (carga cooperativas de ejemplo) o anótalas con una cuenta del equipo |

### Datos reales y producción

- **Precios reales:** `python dev.py start --real` consulta Yahoo Finance y Stooq cuando la bolsa de Nueva York está abierta (04:15–13:30, hora de Nueva York).
- **Histórico real:** carga el histórico con `scripts/load_price_history.py --years 5`.
- **Producción:** `docker-compose.yml` levanta PostgreSQL y la API, y `DATABASE_URL` apunta a PostgreSQL.
- **Más detalle:** [docs/operacion.md](docs/operacion.md) explica la carga de datos, los respaldos y el despliegue.

## Subirlo a GitHub como evidencia

El historial de Git ya trae **un commit por tarea de ingeniería (T01–T42)** y las etiquetas de
cada iteración (`v0.0`, `v0.1`, `v0.2`, `v1.0`, `v1.1`).

1. En GitHub, crea un repositorio vacío llamado `cafe-jaen`, sin README ni licencia.
2. Desde la carpeta del proyecto:

   ```bash
   git remote add origin https://github.com/<usuario>/cafe-jaen.git
   git push -u origin main
   git push origin --tags
   ```

3. En **Settings → Collaborators**, invita al compañero ([jhon1212-beep](https://github.com/jhon1212-beep)
   o [BenjaminGRUPO6](https://github.com/BenjaminGRUPO6)).
4. En la pestaña **Actions** verás la CI en verde. Desde la siguiente semana, Dependabot abrirá
   sus PR de actualización.

## Calidad, pruebas y criterios de aceptación

```bash
python dev.py check
```

- **Qué revisa:** ruff, mypy, import-linter, pytest con cobertura ≥ 80 %, ESLint, Prettier, Vitest y el build de Vite.
- **Resultado actual:** 185 pruebas del backend (cobertura 97,6 %) y 17 del frontend.
- **TDD:** las reglas del dominio se escribieron con la prueba primero.
- **Criterios de aceptación:** cada historia los tiene, y cada uno corresponde a una prueba de aceptación (PA-xx-x). El estado de cada PA, automatizada o manual, está en el README de cada iteración ([docs/xp/iteraciones.md](docs/xp/iteraciones.md)).
- **Trazabilidad:** [docs/xp/trazabilidad.md](docs/xp/trazabilidad.md) relaciona cada historia con sus archivos y sus pruebas.
- **Requisitos no funcionales:**
  - Texto ≥ 16 px y contraste AA ([docs/paleta.md](docs/paleta.md)).
  - Precio en vivo < 3 s en 3G.
  - Carga con 30 usuarios, p95 < 3 s.
  - Funciona en 360 px y sin conexión.

## Plan XP y división del trabajo

Una iteración 0 de exploración y tres iteraciones de dos semanas. Son 42,5 puntos (≈ 170 h, con 1
punto = 4 h ideales), repartidos en partes iguales:

| Integrante | Historias que lidera | Puntos | Horas |
|---|---|---|---|
| [jhon1212-beep](https://github.com/jhon1212-beep) — Chavez C., J. X. | HU02, HU03, HU05, HU06, HU12 (+ T40, T42) | 23 | 92 |
| [BenjaminGRUPO6](https://github.com/BenjaminGRUPO6) — Reyes G., L. B. | HU01, HU04, HU07, HU08, HU09, HU10, HU11, HU15, HU16 | 23 | 92 |

Las tareas en pareja (T02, T14, T34) cuentan para ambos. El detalle por tarea está en
[docs/xp/tareas.md](docs/xp/tareas.md); por iteración, en [docs/xp/iteraciones.md](docs/xp/iteraciones.md).

**Flujo de trabajo en pareja:**
- Cada tarea se trabaja en una rama `feature/huXX-descripcion` y se integra con un PR que revisa el compañero.
- La CI debe quedar en verde antes de unir el PR.
- Se integra a `main` al menos una vez al día (integración continua).

## Convenciones de código

- **Código en inglés; comentarios y docstrings en español.** Los textos que ve el caficultor
  están en `frontend/src/shared/texts/es.ts`.
- Commits `tipo(módulo): descripción en español`, por ejemplo
  `feat(market): consolida el precio de varias webs por mediana`. Los tipos son `feat`, `fix`,
  `test`, `docs`, `refactor`, `build` y `chore`.
- Reglas del negocio solo en `domain/`; nada de lógica en los routers ni en los componentes.
- Detalle completo en [docs/estandar-de-codigo.md](docs/estandar-de-codigo.md).

## Trabajo futuro

| Idea | Por qué no está en esta versión |
|---|---|
| Alertas de precio por notificación (HU13) | Opcional si la velocidad del equipo lo permite |
| Bolsa de Londres (robusta) como referencia (HU14) | Opcional |
| Estimado en Jaén con porcentajes que cambien en el tiempo, calculado en el backend | Hoy basta con la mediana de 30 días ([decisión 0009](docs/decisiones/0009-pronostico-en-jaen.md)) |
| Datos de la bolsa al segundo | ICE cobra licencia por datos en tiempo real |
| Pronóstico a 30 días con reentrenamiento automático | Requiere más datos y seguimiento |
| Consultas por voz, WhatsApp o SMS | Costo y complejidad de terceros |
| App nativa Android/iOS | La PWA cubre la necesidad |
| Ampliación a otras provincias o cultivos | Fuera de la delimitación de la tesis |

## Documentación

| Documento | Contenido |
|---|---|
| [docs/arquitectura.md](docs/arquitectura.md) | Capas, módulos, agentes y flujos |
| [docs/paleta.md](docs/paleta.md) | Paleta «Cosecha», tipografías, contraste y animaciones |
| [docs/decisiones/](docs/decisiones/) | Registro de decisiones de arquitectura (ADR 0001–0009) |
| [docs/xp/](docs/xp/) | Iteraciones, tareas T01–T42, trazabilidad y pruebas de aceptación |
| [docs/metafora.md](docs/metafora.md) · [docs/tarjetas-crc.md](docs/tarjetas-crc.md) | Metáfora del sistema y tarjetas CRC (XP) |
| [docs/estandar-de-codigo.md](docs/estandar-de-codigo.md) | Idioma, nombres, buenas prácticas y Git |
| [docs/operacion.md](docs/operacion.md) | Despliegue, carga de datos y respaldos |
| [docs/manual/](docs/manual/) | Manual de usuario y guía de inducción (Word) |
| [CHANGELOG.md](CHANGELOG.md) | Cambios de cada versión |

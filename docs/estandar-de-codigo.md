# Estándar de código

## Idioma

| Elemento | Idioma | Ejemplo |
|---|---|---|
| Clases, funciones, variables, archivos | Inglés | `PriceConverter.to_quintal()` |
| Rutas de la API y campos JSON | Inglés | `GET /api/prices/live` → `{"price_soles": …, "quoted_at": …}` |
| Tablas y columnas | Inglés, `snake_case` plural | `quotations`, `exchange_rates` |
| Comentarios y docstrings | **Español** | `"""Convierte la cotización a soles por quintal."""` |
| Mensajes de error para el caficultor | Español | `"Celular o contraseña incorrectos"` |
| Textos de la interfaz | Español, en `frontend/src/shared/texts/es.ts` | `texts.live.title` |
| Rutas del navegador | Español (las ve el caficultor) | `/grafico`, `/vender` |
| Commits | Tipo en inglés + descripción en español | `feat(market): consolida el precio de varias webs por mediana` |

## Nombres

| Elemento | Python | TypeScript |
|---|---|---|
| Clases / tipos | `PascalCase` | `PascalCase` |
| Funciones y variables | `snake_case` | `camelCase` |
| Constantes | `UPPER_SNAKE_CASE` | `UPPER_SNAKE_CASE` |
| Puertos | Rol: `QuotationProvider` | — |
| Adaptadores | Tecnología + puerto: `YFinanceQuotationProvider` | — |
| Casos de uso | Verbo + objeto: `GetLivePrice`, `GetSellingAdvice` | Hooks: `useApi`, `useLivePrice` |
| Agentes | Rol + `Agent`: `AnalystAgent` | — |
| Pruebas | `test_<comportamiento>` | `describe/it` en español |

## Buenas prácticas obligatorias

1. El dominio no conoce frameworks; los casos de uso solo usan puertos.
2. Inyección de dependencias por constructor; los adaptadores solo se crean en `main.py`.
3. Objetos de valor inmutables (`@dataclass(frozen=True)`) que se validan al crearse.
4. `Decimal` para dinero, nunca `float` en el dominio.
5. Sin números mágicos: constantes con nombre o `Settings`.
6. Tipado estático: `mypy --strict` en `domain` y `application`; TypeScript `strict`.
7. Errores de negocio como excepciones propias; se traducen a HTTP solo en el adaptador de la API.
8. Secretos solo en variables de entorno (`.env` nunca se versiona).
9. Logs sin datos personales.
10. Los comentarios explican el **porqué**, no el qué. No se deja código comentado.
11. Funciones cortas, una responsabilidad.

## Git

- `main` protegida; ramas `feature/huXX-descripcion` de máximo un día de trabajo.
- `git pull --rebase origin main` antes de empezar y antes de abrir el PR.
- Todo PR lo revisa el otro integrante (o se hizo en pareja). Plantilla en `.github/`.
- Zonas compartidas (`shared/`, `main.py`, `migrations/`): en pareja o con aviso previo.
- Una migración por PR, generada sobre `main` actualizado.

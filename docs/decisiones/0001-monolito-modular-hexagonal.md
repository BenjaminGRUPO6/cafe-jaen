# 0001 — Monolito modular con arquitectura hexagonal

**Estado:** aceptada (Iteración 0)

**Contexto:** dos desarrolladores a tiempo parcial, un solo servidor, necesidad de probar el
negocio con TDD y de trabajar en paralelo sin conflictos. Es la arquitectura que el equipo ya usa
en el Taller Integrador.

**Decisión:** un solo despliegue dividido en módulos (`identity`, `market`, `forecasting`,
`advisor`, `orchestration`), cada uno con `domain` / `application` / `infrastructure`.
Las reglas se verifican con `import-linter`.

**Consecuencias:** el dominio se prueba sin base de datos ni internet; cambiar una fuente o el LLM
es cambiar un adaptador; cada integrante lidera módulos distintos. A cambio, hay más archivos que
en un proyecto plano.

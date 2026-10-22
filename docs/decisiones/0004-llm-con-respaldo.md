# 0004 — LLM opcional con salvaguarda de números

**Estado:** aceptada (Iteración 2)

**Decisión:** el Asesor usa el puerto `LanguageModel`. Por defecto, un modelo por palabras clave
(sin internet ni costo); opcionalmente, la API de Anthropic. Toda respuesta pasa por
`is_grounded`: si contiene un número que no está en los datos, se reemplaza por una plantilla.

**Consecuencias:** el asesor nunca muestra un precio inventado (PA-08-2) y la app funciona aunque
el LLM no esté disponible.

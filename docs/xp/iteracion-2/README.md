# Iteración 2 (11/11/2026 – 24/11/2026)

**Objetivo:** El caficultor ve el gráfico tipo bolsa, el pronóstico a 7 días, conversa con el asesor y usa la app sin señal.

**Entrega:** etiqueta `v0.2` · **Puntos planificados:** 12 (48 h)

## Historias

| HU | Historia | Prioridad | Pts | Responsable |
|---|---|---|---|---|
| HU04 | Gráfico tipo bolsa | Media | 2 | Reyes G., L. B. |
| HU06 | Pronóstico del precio a 7 días (bolsa y Jaén) | Alta | 4 | Chavez C., J. X. |
| HU08 | Asesor conversacional | Alta | 4 | Reyes G., L. B. |
| HU09 | Interfaz sencilla y sin conexión | Media | 2 | Reyes G., L. B. |

## Tareas de ingeniería

| Tarea | HU | Tarea | Tipo | Pts | Resp. | Estado | Entregable |
|---|---|---|---|---|---|---|---|
| T17 | HU04 | Caso de uso GetPriceHistory (intradía y diario) + endpoint GET /prices/history | Desarrollo | 1 | Reyes G., L. B. | Terminada | market/application/get_price_history.py (hoy, 30, 90) |
| T18 | HU04 | Componente de gráfico tipo bolsa | Desarrollo | 1 | Reyes G., L. B. | Terminada | features/live/ChartPage.tsx |
| T19 | HU06 | Dataset histórico y evaluación de modelos (ELM vs. modelo base) | Investigación | 1 | Chavez C., J. X. | Terminada | scripts/evaluate_forecast_models.py · docs/xp/iteracion-2/evaluacion-modelos.md · decisiones/0005 |
| T20 | HU06 | Modelos ELM y base + Agente Predictor con job diario | Desarrollo | 1 | Chavez C., J. X. | Terminada | forecasting/ (modelos, GenerateForecast, ForecasterAgent) · migración 0002 |
| T21 | HU06 | Endpoint GET /forecast y vista del pronóstico | Desarrollo | 1 | Chavez C., J. X. | Terminada | forecasting/infrastructure/api/ · features/forecast/ForecastPage.tsx |
| T38 | HU06 | Pronóstico estimado en Jaén por tipo de café en la pantalla «7 días» (alineado con la TPP) | Desarrollo | 1 | Chavez C., J. X. | Terminada | features/forecast/localForecast.ts · ForecastPage.tsx · decisiones/0009 |
| T22 | HU08 | Puerto LanguageModel + adaptador del proveedor LLM y modelo por palabras clave | Desarrollo | 1 | Reyes G., L. B. | Terminada | advisor/domain/ports/language_model.py · infrastructure/llm/ |
| T23 | HU08 | Agente Asesor con herramientas y salvaguarda de números | Desarrollo | 2 | Reyes G., L. B. | Terminada | advisor/domain/ · advisor/application/ · decisiones/0004 |
| T24 | HU08 | Batería de 20 pruebas de aceptación y pantalla de chat | Pruebas | 1 | Reyes G., L. B. | Terminada | tests/acceptance/test_advisor_battery.py · features/advisor/AdvisorPage.tsx |
| T25 | HU09 | Ajustes de accesibilidad (tamaños, contraste, navegación) | Mejora | 1 | Reyes G., L. B. | Terminada | shared/styles.css · docs/xp/iteracion-2/accesibilidad.md |
| T26 | HU09 | Service worker y caché del último precio | Desarrollo | 1 | Reyes G., L. B. | Terminada | features/live/lastPriceCache.ts · vite.config.ts (PWA) |

## Pruebas de aceptación

| Código | Escenario | Resultado esperado | Estado | Evidencia |
|---|---|---|---|---|
| PA-04-1 | Elegir Hoy, 30 días y 90 días | El gráfico muestra el periodo elegido | Pendiente · la ejecuta el Cliente | Pantalla «Gráfico» (Hoy, 30 y 90 días) |
| PA-04-2 | Tocar un punto del gráfico en un celular de 360 px | Se ven la hora o fecha y el precio, sin desplazamiento horizontal | Pendiente · la ejecuta el Cliente | Pantalla «Gráfico» en celular de 360 px |
| PA-04-3 | Pedir el histórico intradía con cotizaciones cada minuto | La API devuelve los puntos de hoy en orden | Aprobada (automatizada en CI) | test_price_queries.py::test_intraday_history_returns_today_minute_by_minute, integration::test_daily_cycle_collects_and_forecasts |
| PA-06-1 | Ejecutar el script de evaluación | Tabla con MAPE y RMSE del ELM y del modelo base; modelo elegido documentado | Pendiente · requiere datos reales | scripts/evaluate_forecast_models.py · docs/xp/iteracion-2/evaluacion-modelos.md |
| PA-06-2 | Ejecutar el ciclo diario tras el cierre | Se genera un pronóstico nuevo a 7 días con su rango | Aprobada (automatizada en CI) | integration::test_daily_cycle_collects_and_forecasts |
| PA-06-3 | Abrir la vista del pronóstico | Muestra valor esperado, rango y el aviso «pronóstico referencial» | Pendiente · la ejecuta el Cliente | Pantalla «Pronóstico» (ver manual de usuario) |
| PA-06-4 | Pronóstico de la bolsa S/ 1500 y cooperativas convencionales al 72 % | El día muestra S/ 1080,00 en Jaén; al elegir otro tipo usa su porcentaje; sin precios de cooperativas solo muestra la bolsa | Aprobada (automatizada en CI) | frontend/src/features/forecast/localForecast.test.ts |
| PA-08-1 | Preguntar «¿a cuánto está el café hoy?» | Responde en menos de 5 s con el mismo precio, hora y fuente de la pantalla en vivo | Aprobada (automatizada en CI) | integration::test_advisor_answers_with_the_same_price_as_home · p95 32 ms en carga |
| PA-08-2 | Ejecutar la batería de 20 preguntas de prueba | 0 precios inventados; todas las respuestas citan la fuente | Aprobada (automatizada en CI) | acceptance/test_advisor_battery.py (20 preguntas, modelo por palabras clave) |
| PA-08-3 | Preguntar «¿quién ganó el partido de ayer?» | Responde «no tengo esa información» | Aprobada (automatizada en CI) | test_answer_question.py::test_off_topic_question_gets_no_information |
| PA-09-1 | Auditar la app (accesibilidad) | Texto ≥ 16 px y contraste AA sin errores | Aprobada en CI · falta revisión del Cliente | docs/xp/iteracion-2/accesibilidad.md (tamaños y contraste AA verificados) |
| PA-09-2 | Activar el modo avión después de una consulta | Muestra el último precio con la leyenda «sin conexión» | Aprobada en CI · falta revisión del Cliente | lastPriceCache.test.ts · aviso «sin conexión» en la pantalla Precio |
| PA-09-3 | Abrir la app desde Chrome en Android | Ofrece instalarla en la pantalla de inicio | Pendiente · requiere producción | La instalación PWA requiere HTTPS |

## Registro de la iteración (llenar al cerrar)

| Dato | Valor |
|---|---|
| Puntos planificados | 12 |
| Puntos terminados (velocidad real) | |
| Horas reales — Chavez C., J. X. | |
| Horas reales — Reyes G., L. B. | |
| Fecha de la revisión con el Cliente | |
| Historias aceptadas por el Cliente | |

## Retrospectiva (llenar en la reunión)

- **¿Qué funcionó bien?**
- **¿Qué no funcionó?**
- **Una mejora concreta para la siguiente iteración:**

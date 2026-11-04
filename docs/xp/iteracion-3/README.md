# Iteración 3 (25/11/2026 – 08/12/2026)

**Objetivo:** «¿Vendo ahora o espero?», precio estimado en Jaén calibrado con cooperativas, producción v1.0 e inducción al GE.

**Entrega:** etiqueta `v1.0` · **Puntos planificados:** 13.5 (54 h)

## Historias

| HU | Historia | Prioridad | Pts | Responsable |
|---|---|---|---|---|
| HU05 | ¿Vendo ahora o espero? | Alta | 4 | Chavez C., J. X. |
| HU10 | Puesta en producción | Alta | 2 | Reyes G., L. B. |
| HU11 | Manual e inducción | Media | 1 | Reyes G., L. B. |
| HU12 | Precio estimado en Jaén (calibrado con cooperativas) | Alta | 3 | Chavez C., J. X. |
| HU15 | Interfaz dinámica y llamativa | Media | 2 | Reyes G., L. B. |
| HU16 | Ejecución local en un paso y mantenimiento | Media | 1.5 | Reyes G., L. B. |

## Tareas de ingeniería

| Tarea | HU | Tarea | Tipo | Pts | Resp. | Estado | Entregable |
|---|---|---|---|---|---|---|---|
| T27 | HU05 | Regla de dominio SellingDecision (TDD) | Desarrollo | 1 | Chavez C., J. X. | Terminada | decision/domain/selling_decision.py |
| T28 | HU05 | Agente Estratega de venta: pide precio y pronóstico vía supervisor; herramienta del asesor | Desarrollo | 1 | Chavez C., J. X. | Terminada | decision/application/ · agents/strategist_agent.py · herramienta del asesor |
| T29 | HU05 | Endpoint GET /decision/today y tarjeta «¿Vendo ahora o espero?» | Desarrollo | 1 | Chavez C., J. X. | Terminada | decision/infrastructure/api/ · features/decision/DecisionPage.tsx |
| T30 | HU05 | Prueba retrospectiva de la regla con 5 años de datos (porcentaje de acierto) | Investigación | 1 | Chavez C., J. X. | Terminada | decision/domain/backtest.py · scripts/backtest_selling_rule.py · docs/xp/iteracion-3/prueba-retrospectiva.md · decisiones/0007 |
| T31 | HU10 | Despliegue de API, base de datos y front-end | Configuración | 1 | Reyes G., L. B. | Terminada | backend/Dockerfile · docker-compose.yml · docs/operacion.md |
| T32 | HU10 | Prueba de carga y reporte de pruebas | Pruebas | 1 | Chavez C., J. X. | Terminada | tests/load/locustfile.py · docs/xp/iteracion-3/Reporte_de_pruebas_Cafe_Jaen.docx |
| T33 | HU11 | Manual de usuario | Documentación | 0.5 | Reyes G., L. B. | Terminada | docs/manual/Manual_de_usuario_Cafe_Jaen.docx |
| T34 | HU11 | Sesión de inducción con el GE | Capacitación | 0.5 | Pareja | Material listo · sesión pendiente | docs/manual/Guia_de_induccion_Cafe_Jaen.docx (la sesión la realiza el equipo) |
| T35 | HU12 | Modelo LocalPriceObservation y estimador por mediana de porcentajes (TDD) | Desarrollo | 1 | Chavez C., J. X. | Terminada | market/domain/local_price.py · tests/unit/market/test_local_price.py |
| T36 | HU12 | Rol administrador, caso de uso RecordLocalPrice y endpoints /admin/local-prices | Desarrollo | 1 | Reyes G., L. B. | Terminada | identity (rol admin, scripts/create_admin.py) · market/application/record_local_price.py · /admin/local-prices · migración 0003 |
| T37 | HU12 | Pantalla «Equipo» para anotar precios y tarjeta «Precio estimado en Jaén» con filtro por tipo | Desarrollo | 1 | Reyes G., L. B. | Terminada | features/admin/AdminPage.tsx · features/live/LocalEstimateCard.tsx · features/auth/RequireAdmin.tsx |
| T39 | HU15 | Sistema de diseño v2: paleta «Cosecha», tipografías, bloques (bento) y barra inferior flotante | Mejora | 1 | Reyes G., L. B. | Terminada | shared/styles.css · docs/paleta.md · shared/components/Brand.tsx |
| T40 | HU15 | Animaciones con Framer Motion: precio que rueda, línea del día, pastillas, veredicto, rangos, chat y carga | Desarrollo | 1 | Chavez C., J. X. | Terminada | shared/motion/ (Ticker, Sparkline, Reveal, Segmented, PageTransition) · pantallas |
| T41 | HU16 | dev.py multiplataforma (setup, demo, start, test, check, admin, reset), SQLite por defecto y demo con cooperativas | Configuración | 1 | Reyes G., L. B. | Terminada | dev.py · settings.py (SQLite) · scripts/seed_demo_data.py · decisiones/0008 |
| T42 | HU16 | Dependabot, versiones fijadas (.python-version, .nvmrc) y README con arquitectura y paso a paso | Documentación | 0.5 | Chavez C., J. X. | Terminada | .github/dependabot.yml · .python-version · frontend/.nvmrc · README.md |

## Pruebas de aceptación

| Código | Escenario | Resultado esperado | Estado | Evidencia |
|---|---|---|---|---|
| PA-05-1 | Precio S/ 1140; pronóstico a 7 días S/ 1190 (rango 1150–1230) | «Esperar», con el motivo y los números | Aprobada (automatizada en CI) | test_selling_decision.py::test_waits_when_forecast_rises_and_range_stays_above_today |
| PA-05-2 | Precio S/ 1140; pronóstico a 7 días S/ 1090 | «Vender ahora», con el motivo y los números | Aprobada (automatizada en CI) | test_selling_decision.py::test_sells_now_when_forecast_falls_more_than_threshold |
| PA-05-3 | Precio S/ 1140; pronóstico S/ 1150 (+0,9 %) | «Sin señal clara» | Aprobada (automatizada en CI) | test_selling_decision.py::test_small_change_gives_no_clear_signal |
| PA-05-4 | Precio desactualizado o sin pronóstico del día | No recomienda y explica por qué | Aprobada (automatizada en CI) | test_selling_decision.py::test_does_not_recommend_without_fresh_data, test_strategist_agent.py |
| PA-10-1 | Abrir la URL pública | Carga con certificado HTTPS válido | Pendiente · requiere producción | Despliegue con Dockerfile (docs/operacion.md) |
| PA-10-2 | Revisar las copias de seguridad tras 2 días | Existen 2 copias diarias y una se restaura con éxito | Pendiente · requiere producción | Respaldo diario con pg_dump |
| PA-10-3 | Prueba de carga con 30 usuarios | p95 menor a 3 s y 0 errores | Aprobada con observación (prueba local) | tests/load/locustfile.py · p95 global 100 ms; registro simultáneo p95 3,3 s |
| PA-11-1 | Revisar el manual con el Cliente | Máximo 6 páginas con capturas; el Cliente lo aprueba | Pendiente · la ejecuta el Cliente | docs/manual/Manual_de_usuario_Cafe_Jaen.docx |
| PA-11-2 | Realizar la sesión de inducción | Lista de asistencia firmada; cada participante ingresa al menos una vez | Pendiente · la ejecuta el Cliente | docs/manual/Guia_de_induccion_Cafe_Jaen.docx |
| PA-12-1 | El administrador anota «Coop. A, convencional, S/ 900» con la bolsa a S/ 1140,89; un caficultor intenta lo mismo | Se guarda con 78,9 % de la bolsa; al caficultor se le niega (403) | Aprobada (automatizada en CI) | integration::test_only_the_team_can_record_cooperative_prices, test_jwt_token_service.py::test_token_carries_the_role_for_team_routes |
| PA-12-2 | Anotar S/ 90 por error de escritura | Se rechaza con «revisa si está bien escrito» | Aprobada (automatizada en CI) | test_local_price.py::test_rejects_prices_that_look_mistyped, integration (400 «revisa si está bien escrito») |
| PA-12-3 | Precios convencionales de 78,9 %, 78,2 % y 79,1 % con la bolsa a S/ 1200 | Estimado S/ 947,37 (mediana); cambia cuando cambia la bolsa; los tipos sin datos no muestran estimado | Aprobada (automatizada en CI) | test_local_price.py::test_estimate_uses_median_ratio_of_each_coffee_type, test_live_price_estimate_moves_with_the_exchange_and_ignores_old_prices |
| PA-12-4 | El caficultor elige «Orgánico» en la pantalla Precio | Ve el estimado de ese tipo, cuántos precios lo respaldan y sus fechas; aviso si son menos de 3 | Aprobada en CI · falta revisión del Cliente | Pantalla «Precio» con filtro por tipo, probada con datos DEMO; falta revisión del Cliente |
| PA-15-1 | Revisar contraste y tamaños de la paleta v2 | Contraste AA o mejor en todos los pares; ningún texto menor a 16 px | Aprobada en CI · falta revisión del Cliente | docs/paleta.md (tabla de contraste) · texto mínimo 16 px |
| PA-15-2 | Llega un precio nuevo con la pantalla «Precio» abierta | Los dígitos ruedan y el número se ilumina; con «reducir movimiento» cambia sin animación | Pendiente · la ejecuta el Cliente | Pantalla «Precio» con datos DEMO (el precio cambia cada minuto) |
| PA-15-3 | Abrir todas las pantallas en un celular de 360 px | Sin desplazamiento horizontal; la barra inferior se ve completa | Aprobada en CI · falta revisión del Cliente | Capturas en 360 px y 390 px (sin desplazamiento horizontal) |
| PA-15-4 | Leer la pantalla «Precio» con lector de pantalla | Se anuncia el precio completo, no dígito por dígito | Aprobada (automatizada en CI) | frontend/src/shared/motion/Ticker.test.tsx |
| PA-16-1 | En una computadora limpia: python dev.py setup, demo y start | App en localhost:5173 con precio en vivo, estimado en Jaén, pronóstico y recomendación | Aprobada en CI · falta revisión del Cliente | README «Cómo ejecutarlo» · probado desde un clon limpio |
| PA-16-2 | Revisar backend/.env después del setup | Existe, con JWT_SECRET aleatorio, y Git lo ignora | Aprobada (automatizada en CI) | dev.py ensure_env_file · .gitignore (.env) |
| PA-16-3 | Ejecutar python dev.py check | Mismo resultado que la CI: todo en verde | Aprobada (automatizada en CI) | python dev.py check · .github/workflows/ci.yml |

## Registro de la iteración (llenar al cerrar)

| Dato | Valor |
|---|---|
| Puntos planificados | 13.5 |
| Puntos terminados (velocidad real) | |
| Horas reales — Chavez C., J. X. | |
| Horas reales — Reyes G., L. B. | |
| Fecha de la revisión con el Cliente | |
| Historias aceptadas por el Cliente | |

## Retrospectiva (llenar en la reunión)

- **¿Qué funcionó bien?**
- **¿Qué no funcionó?**
- **Una mejora concreta para la siguiente iteración:**

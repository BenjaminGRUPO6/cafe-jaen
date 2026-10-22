# Iteración 1 (28/10/2026 – 10/11/2026)

**Objetivo:** El caficultor ingresa con su código y ve el precio mundial del café en vivo, consolidado de varias fuentes y en S/ por quintal.

**Entrega:** etiqueta `v0.1` · **Puntos planificados:** 13 (52 h)

## Historias

| HU | Historia | Prioridad | Pts | Responsable |
|---|---|---|---|---|
| HU01 | Acceso con código de invitación | Alta | 3 | Reyes G., L. B. |
| HU02 | Precio mundial desde varias fuentes | Alta | 4 | Chavez C., J. X. |
| HU03 | Precio en vivo tipo bolsa | Alta | 3 | Chavez C., J. X. |
| HU07 | Coordinación de agentes (supervisor) | Alta | 3 | Reyes G., L. B. |

## Tareas de ingeniería

| Tarea | HU | Tarea | Tipo | Pts | Resp. | Estado | Entregable |
|---|---|---|---|---|---|---|---|
| T04 | HU01 | Entidades User e InvitationCode y puerto UserRepository (TDD) | Desarrollo | 1 | Reyes G., L. B. | Terminada | identity/domain/ |
| T05 | HU01 | Casos de uso RegisterUser y AuthenticateUser + adaptador SQLAlchemy | Desarrollo | 1 | Reyes G., L. B. | Terminada | identity/application/ · identity/infrastructure/ |
| T06 | HU01 | Pantallas de registro, consentimiento e inicio de sesión | Desarrollo | 1 | Reyes G., L. B. | Terminada | frontend/src/features/auth/ · shared/auth/ |
| T07 | HU02 | Puerto QuotationSource + adaptadores de las webs del precio de Nueva York (Yahoo Finance, Stooq) | Desarrollo | 1 | Chavez C., J. X. | Terminada | market/domain/ports/sources.py · infrastructure/sources/ (Yahoo, Stooq, BCRP, DEMO) |
| T08 | HU02 | Consolidación multifuente (mediana y descarte de la fuente discrepante) y validación (TDD) | Desarrollo | 1 | Chavez C., J. X. | Terminada | market/domain/consensus.py · price_validator.py · market_hours.py |
| T09 | HU02 | Tipo de cambio BCRP y repositorio de cotizaciones intradía | Desarrollo | 1 | Chavez C., J. X. | Terminada | market/infrastructure/persistence/ (live_quotes, cierres) · migración 0001 |
| T10 | HU02 | Agente Recolector y job cada minuto en horario de bolsa | Desarrollo | 1 | Chavez C., J. X. | Terminada | market/application/collect_prices.py · agents/collector_agent.py · scheduler (cada minuto) |
| T11 | HU03 | PriceConverter (TDD) y Agente Analista: caso de uso GetLivePrice | Desarrollo | 1 | Chavez C., J. X. | Terminada | market/domain/quintal_price.py · live_price.py · application/get_live_price.py · agents/analyst_agent.py |
| T12 | HU03 | Endpoint GET /prices/live y flujo en vivo GET /prices/stream (Server-Sent Events) | Desarrollo | 1 | Chavez C., J. X. | Terminada | market/infrastructure/api/market_router.py (/prices/live, /prices/stream) |
| T13 | HU03 | Pantalla «Precio en vivo» tipo bolsa | Desarrollo | 1 | Chavez C., J. X. | Terminada | features/live/LivePricePage.tsx · shared/api/stream.ts · hooks/useLivePrice.ts |
| T14 | HU07 | Kernel compartido: AgentMessage y puerto Agent | Diseño | 1 | Pareja | Terminada | shared/domain/ (AgentMessage, contrato, puertos) |
| T15 | HU07 | Grafo del supervisor en LangGraph y caso de uso DispatchRequest | Desarrollo | 1 | Reyes G., L. B. | Terminada | orchestration/application/ · infrastructure/langgraph/ · scheduler/ |
| T16 | HU07 | Registro de trazas de los agentes | Desarrollo | 1 | Reyes G., L. B. | Terminada | orchestration/domain/trace.py · infrastructure/persistence/ |

## Pruebas de aceptación

| Código | Escenario | Resultado esperado | Estado | Evidencia |
|---|---|---|---|---|
| PA-01-1 | Ingresar un código válido no usado, celular y contraseña de 8+ caracteres | Se crea la cuenta y el código queda marcado como usado | Aprobada (automatizada en CI) | unit/identity/test_register_user.py::test_registers_user_and_redeems_code |
| PA-01-2 | Ingresar un código inválido o ya usado (simula un participante del GC) | Mensaje «código no válido»; no se crea la cuenta | Aprobada (automatizada en CI) | test_rejects_unknown_code, test_rejects_used_code, integration::test_register_with_invalid_code_is_rejected |
| PA-01-3 | Intentar entrar sin aceptar el consentimiento | No permite continuar; al aceptar se guardan fecha y versión | Aprobada en CI · falta revisión del Cliente | test_requires_consent, RegisterPage.test.tsx |
| PA-01-4 | Revisar la BD y abrir la app al día siguiente | La contraseña no está en texto plano y la sesión sigue activa | Aprobada (automatizada en CI) | test_password_is_never_stored_in_plain_text, test_jwt_token_service.py |
| PA-02-1 | Tres fuentes responden 300,10; 300,20 y 300,15 ¢/lb | Se publica la mediana 300,15 con 3 fuentes coincidentes | Aprobada (automatizada en CI) | test_consensus.py::test_publishes_median_when_three_sources_agree, test_collect_prices.py::test_saves_median_of_sources_with_their_names |
| PA-02-2 | Dos fuentes dan 300 ¢/lb y una 310 ¢/lb (+3,3 %) | Se publica 300 ¢/lb y se descarta la fuente discrepante con registro | Aprobada (automatizada en CI) | test_consensus.py::test_discards_source_far_from_the_median, test_collect_prices.py::test_discards_disagreeing_source_and_reports_it |
| PA-02-3 | Fijar el reloj con la bolsa cerrada | El job no consulta y se muestra el último cierre | Aprobada (automatizada en CI) | test_collect_prices.py::test_does_not_query_sources_with_market_closed, test_market_hours.py |
| PA-02-4 | Todas las fuentes fallan | Se conserva el último valor válido marcado «desactualizado» y se registra el incidente | Aprobada (automatizada en CI) | test_collect_prices.py::test_all_sources_down_keeps_last_valid_value, test_one_source_down_does_not_stop_the_collection |
| PA-03-1 | Convertir 300 ¢/lb con tipo de cambio 3,75 y factor local 1 | S/ 1140,89 por quintal | Aprobada (automatizada en CI) | test_quintal_price.py::test_converts_ice_quote_to_soles_per_quintal |
| PA-03-2 | Cierre anterior S/ 1100,00; precio actual S/ 1140,89 | Muestra +S/ 40,89 (+3,7 %) en verde | Aprobada (automatizada en CI) | test_price_queries.py::test_live_price_includes_change_against_previous_close |
| PA-03-3 | Llega una cotización nueva con la pantalla abierta | El precio cambia sin recargar en menos de 1 minuto | Aprobada en CI · falta revisión del Cliente | integration::test_stream_sends_live_price_as_server_sent_event, stream.test.ts; 30 flujos abiertos: primer evento ≤ 0,45 s |
| PA-03-4 | Abrir la pantalla en un celular | Se ven precio, hora de la cotización, fuentes y estado de la bolsa | Pendiente · la ejecuta el Cliente | Pantalla «Precio» (ver manual de usuario); probada con datos DEMO |
| PA-07-1 | Enviar REQUEST get_live_price al supervisor | Lo atiende el Analista y vuelve un INFORM con precio, hora y fuentes | Aprobada (automatizada en CI) | test_supervisor.py::test_routes_each_request_to_the_right_agent |
| PA-07-2 | Enviar una acción dirigida a cada agente | Cada solicitud llega al agente correcto | Aprobada (automatizada en CI) | test_supervisor.py::test_routes_each_request_to_the_right_agent (5 agentes) |
| PA-07-3 | Forzar una excepción dentro de un agente | Se devuelve FAILURE; la API responde un mensaje claro (sin error 500) | Aprobada (automatizada en CI) | test_supervisor.py::test_agent_exception_becomes_failure |
| PA-07-4 | Revisar la tabla de trazas tras las pruebas | Cada interacción tiene agente, acción, duración y resultado | Aprobada (automatizada en CI) | test_supervisor.py::test_every_interaction_is_traced |

## Registro de la iteración (llenar al cerrar)

| Dato | Valor |
|---|---|
| Puntos planificados | 13 |
| Puntos terminados (velocidad real) | |
| Horas reales — Chavez C., J. X. | |
| Horas reales — Reyes G., L. B. | |
| Fecha de la revisión con el Cliente | |
| Historias aceptadas por el Cliente | |

## Retrospectiva (llenar en la reunión)

- **¿Qué funcionó bien?**
- **¿Qué no funcionó?**
- **Una mejora concreta para la siguiente iteración:**

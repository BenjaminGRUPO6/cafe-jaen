# Tareas de ingeniería (T01–T42)

Cada tarea tiene un commit propio en el historial de Git (`git log --oneline`).

| Tarea | Iteración | HU | Tarea | Pts | Resp. | Entregable |
|---|---|---|---|---|---|---|
| T01 | It0 | — | Spike: probar 3–4 webs del precio de la bolsa de Nueva York (KC=F), medir su retraso real y límites de uso; API del BCRP y proveedor LLM | 1 | Chavez C., J. X. | scripts/spike_sources.py · docs/xp/iteracion-0/spike.md |
| T02 | It0 | — | Diseño: arquitectura hexagonal, metáfora del sistema, tarjetas CRC y modelo de datos | 2 | Pareja | docs/arquitectura.md · metafora.md · tarjetas-crc.md · decisiones/0001-0003, 0006 · .importlinter |
| T03 | It0 | — | Repositorio, CI (lint, tipos, pruebas), estándar de código, esqueletos backend/frontend y componentes UI base | 1 | Reyes G., L. B. | .github/ · Makefile · pyproject.toml · estándar de código · esqueletos backend y frontend |
| T04 | It1 | HU01 | Entidades User e InvitationCode y puerto UserRepository (TDD) | 1 | Reyes G., L. B. | identity/domain/ |
| T05 | It1 | HU01 | Casos de uso RegisterUser y AuthenticateUser + adaptador SQLAlchemy | 1 | Reyes G., L. B. | identity/application/ · identity/infrastructure/ |
| T06 | It1 | HU01 | Pantallas de registro, consentimiento e inicio de sesión | 1 | Reyes G., L. B. | frontend/src/features/auth/ · shared/auth/ |
| T07 | It1 | HU02 | Puerto QuotationSource + adaptadores de las webs del precio de Nueva York (Yahoo Finance, Stooq) | 1 | Chavez C., J. X. | market/domain/ports/sources.py · infrastructure/sources/ (Yahoo, Stooq, BCRP, DEMO) |
| T08 | It1 | HU02 | Consolidación multifuente (mediana y descarte de la fuente discrepante) y validación (TDD) | 1 | Chavez C., J. X. | market/domain/consensus.py · price_validator.py · market_hours.py |
| T09 | It1 | HU02 | Tipo de cambio BCRP y repositorio de cotizaciones intradía | 1 | Chavez C., J. X. | market/infrastructure/persistence/ (live_quotes, cierres) · migración 0001 |
| T10 | It1 | HU02 | Agente Recolector y job cada minuto en horario de bolsa | 1 | Chavez C., J. X. | market/application/collect_prices.py · agents/collector_agent.py · scheduler (cada minuto) |
| T11 | It1 | HU03 | PriceConverter (TDD) y Agente Analista: caso de uso GetLivePrice | 1 | Chavez C., J. X. | market/domain/quintal_price.py · live_price.py · application/get_live_price.py · agents/analyst_agent.py |
| T12 | It1 | HU03 | Endpoint GET /prices/live y flujo en vivo GET /prices/stream (Server-Sent Events) | 1 | Chavez C., J. X. | market/infrastructure/api/market_router.py (/prices/live, /prices/stream) |
| T13 | It1 | HU03 | Pantalla «Precio en vivo» tipo bolsa | 1 | Chavez C., J. X. | features/live/LivePricePage.tsx · shared/api/stream.ts · hooks/useLivePrice.ts |
| T14 | It1 | HU07 | Kernel compartido: AgentMessage y puerto Agent | 1 | Pareja | shared/domain/ (AgentMessage, contrato, puertos) |
| T15 | It1 | HU07 | Grafo del supervisor en LangGraph y caso de uso DispatchRequest | 1 | Reyes G., L. B. | orchestration/application/ · infrastructure/langgraph/ · scheduler/ |
| T16 | It1 | HU07 | Registro de trazas de los agentes | 1 | Reyes G., L. B. | orchestration/domain/trace.py · infrastructure/persistence/ |
| T17 | It2 | HU04 | Caso de uso GetPriceHistory (intradía y diario) + endpoint GET /prices/history | 1 | Reyes G., L. B. | market/application/get_price_history.py (hoy, 30, 90) |
| T18 | It2 | HU04 | Componente de gráfico tipo bolsa | 1 | Reyes G., L. B. | features/live/ChartPage.tsx |
| T19 | It2 | HU06 | Dataset histórico y evaluación de modelos (ELM vs. modelo base) | 1 | Chavez C., J. X. | scripts/evaluate_forecast_models.py · docs/xp/iteracion-2/evaluacion-modelos.md · decisiones/0005 |
| T20 | It2 | HU06 | Modelos ELM y base + Agente Predictor con job diario | 1 | Chavez C., J. X. | forecasting/ (modelos, GenerateForecast, ForecasterAgent) · migración 0002 |
| T21 | It2 | HU06 | Endpoint GET /forecast y vista del pronóstico | 1 | Chavez C., J. X. | forecasting/infrastructure/api/ · features/forecast/ForecastPage.tsx |
| T22 | It2 | HU08 | Puerto LanguageModel + adaptador del proveedor LLM y modelo por palabras clave | 1 | Reyes G., L. B. | advisor/domain/ports/language_model.py · infrastructure/llm/ |
| T23 | It2 | HU08 | Agente Asesor con herramientas y salvaguarda de números | 2 | Reyes G., L. B. | advisor/domain/ · advisor/application/ · decisiones/0004 |
| T24 | It2 | HU08 | Batería de 20 pruebas de aceptación y pantalla de chat | 1 | Reyes G., L. B. | tests/acceptance/test_advisor_battery.py · features/advisor/AdvisorPage.tsx |
| T25 | It2 | HU09 | Ajustes de accesibilidad (tamaños, contraste, navegación) | 1 | Reyes G., L. B. | shared/styles.css · docs/xp/iteracion-2/accesibilidad.md |
| T26 | It2 | HU09 | Service worker y caché del último precio | 1 | Reyes G., L. B. | features/live/lastPriceCache.ts · vite.config.ts (PWA) |
| T27 | It3 | HU05 | Regla de dominio SellingDecision (TDD) | 1 | Chavez C., J. X. | decision/domain/selling_decision.py |
| T28 | It3 | HU05 | Agente Estratega de venta: pide precio y pronóstico vía supervisor; herramienta del asesor | 1 | Chavez C., J. X. | decision/application/ · agents/strategist_agent.py · herramienta del asesor |
| T29 | It3 | HU05 | Endpoint GET /decision/today y tarjeta «¿Vendo ahora o espero?» | 1 | Chavez C., J. X. | decision/infrastructure/api/ · features/decision/DecisionPage.tsx |
| T30 | It3 | HU05 | Prueba retrospectiva de la regla con 5 años de datos (porcentaje de acierto) | 1 | Chavez C., J. X. | decision/domain/backtest.py · scripts/backtest_selling_rule.py · docs/xp/iteracion-3/prueba-retrospectiva.md · decisiones/0007 |
| T31 | It3 | HU10 | Despliegue de API, base de datos y front-end | 1 | Reyes G., L. B. | backend/Dockerfile · docker-compose.yml · docs/operacion.md |
| T32 | It3 | HU10 | Prueba de carga y reporte de pruebas | 1 | Chavez C., J. X. | tests/load/locustfile.py · docs/xp/iteracion-3/Reporte_de_pruebas_Cafe_Jaen.docx |
| T33 | It3 | HU11 | Manual de usuario | 0.5 | Reyes G., L. B. | docs/manual/Manual_de_usuario_Cafe_Jaen.docx |
| T34 | It3 | HU11 | Sesión de inducción con el GE | 0.5 | Pareja | docs/manual/Guia_de_induccion_Cafe_Jaen.docx (la sesión la realiza el equipo) |
| T35 | It3 | HU12 | Modelo LocalPriceObservation y estimador por mediana de porcentajes (TDD) | 1 | Chavez C., J. X. | market/domain/local_price.py · tests/unit/market/test_local_price.py |
| T36 | It3 | HU12 | Rol administrador, caso de uso RecordLocalPrice y endpoints /admin/local-prices | 1 | Reyes G., L. B. | identity (rol admin, scripts/create_admin.py) · market/application/record_local_price.py · /admin/local-prices · migración 0003 |
| T37 | It3 | HU12 | Pantalla «Equipo» para anotar precios y tarjeta «Precio estimado en Jaén» con filtro por tipo | 1 | Reyes G., L. B. | features/admin/AdminPage.tsx · features/live/LocalEstimateCard.tsx · features/auth/RequireAdmin.tsx |
| T38 | It2 | HU06 | Pronóstico estimado en Jaén por tipo de café en la pantalla «7 días» (alineado con la TPP) | 1 | Chavez C., J. X. | features/forecast/localForecast.ts · ForecastPage.tsx · decisiones/0009 |
| T39 | It3 | HU15 | Sistema de diseño v2: paleta «Cosecha», tipografías, bloques (bento) y barra inferior flotante | 1 | Reyes G., L. B. | shared/styles.css · docs/paleta.md · shared/components/Brand.tsx |
| T40 | It3 | HU15 | Animaciones con Framer Motion: precio que rueda, línea del día, pastillas, veredicto, rangos, chat y carga | 1 | Chavez C., J. X. | shared/motion/ (Ticker, Sparkline, Reveal, Segmented, PageTransition) · pantallas |
| T41 | It3 | HU16 | dev.py multiplataforma (setup, demo, start, test, check, admin, reset), SQLite por defecto y demo con cooperativas | 1 | Reyes G., L. B. | dev.py · settings.py (SQLite) · scripts/seed_demo_data.py · decisiones/0008 |
| T42 | It3 | HU16 | Dependabot, versiones fijadas (.python-version, .nvmrc) y README con arquitectura y paso a paso | 0.5 | Chavez C., J. X. | .github/dependabot.yml · .python-version · frontend/.nvmrc · README.md |

**Total:** 42.5 puntos ≈ 170 horas.

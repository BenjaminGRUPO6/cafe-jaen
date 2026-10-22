# Tarjetas CRC (Clase · Responsabilidades · Colaboradores)

| Clase | Responsabilidades | Colaboradores |
|---|---|---|
| `DispatchRequest` | Crear la solicitud, enrutarla, medir su duración y registrar la traza | `AgentRouter`, `TraceRepository`, `Clock` |
| `LangGraphAgentRouter` | Entregar cada mensaje al nodo del agente receptor; convertir errores en `FAILURE` | `Agent` (todos), LangGraph |
| `CollectLivePrices` | Pedir la recolección en vivo cada minuto | `AgentGateway` |
| `RunDailyCycle` | Tras el cierre: encadenar cierre → histórico → pronóstico | `AgentGateway` |
| `CollectorAgent` | Atender `collect_prices` | `CollectPrices` |
| `CollectPrices` | Consultar cada web, consolidar, validar y guardar; tipo de cambio una vez al día | `QuotationSource`, `ExchangeRateProvider`, `Consensus`, `PriceValidator`, `MarketHours`, `PriceRepository` |
| `Consensus` | Publicar la mediana y descartar la web que se aleja más de 1 % | `LiveQuote` |
| `MarketHours` | Saber si la bolsa de Nueva York está abierta y a qué día de negociación pertenece una hora | `Clock` |
| `PriceValidator` | Rechazar cotizaciones repetidas o saltos mayores a ±10 % | `LiveQuote` |
| `AnalystAgent` | Atender `get_live_price` y `get_price_history` (hoy, 30, 90) | `GetLivePrice`, `GetPriceHistory` |
| `GetLivePrice` | Precio en vivo, variación frente al cierre anterior, estado de la bolsa y antigüedad | `PriceRepository`, `PriceConverter`, `MarketHours` |
| `LocalPriceEstimator` | Estimar el precio en Jaén por tipo de café: bolsa × mediana de porcentajes de 30 días | `LocalPriceObservation` |
| `RecordLocalPrice` | Guardar el precio de una cooperativa junto a la bolsa del momento | `PriceRepository`, `GetLivePrice`, `Clock` |
| `PriceConverter` | Convertir ¢USD/lb a S/ por quintal | `QuintalPrice` |
| `ForecasterAgent` | Atender `generate_forecast` y `get_forecast` | `GenerateForecast`, `GetForecast` |
| `GenerateForecast` | Validar cada modelo (MAPE), elegir el mejor y pronosticar | `ForecastModel`, `ForecastRepository`, `Clock` |
| `StrategistAgent` | Atender `get_selling_advice` | `GetSellingAdvice` |
| `GetSellingAdvice` | Pedir precio y pronóstico vía supervisor y aplicar la regla | `AgentGateway`, `SellingDecision` |
| `SellingDecision` | Decidir vender ahora, esperar, sin señal clara o sin datos, con su motivo | `MarketSnapshot`, `ForecastDay` |
| `AdvisorAgent` | Atender `answer_question` | `AnswerQuestion` |
| `AnswerQuestion` | Elegir herramienta, pedir datos vía supervisor, redactar y verificar números | `LanguageModel`, `AgentGateway`, `is_grounded`, `template_answer` |
| `RegisterUser` | Validar código, consentimiento, celular y contraseña; crear el usuario | `UserRepository`, `InvitationCodeRepository`, `PasswordHasher`, `Clock` |

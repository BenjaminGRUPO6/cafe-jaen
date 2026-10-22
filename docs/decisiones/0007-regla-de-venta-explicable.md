# 0007 — «¿Vendo ahora o espero?» con una regla explicable y su prueba retrospectiva

**Estado:** aceptada (v3.0, 21/10/2026)

**Contexto.** El caficultor decide por el boca a boca. La app debe darle «la mejor opción del
mercado» sin convertirse en una caja negra ni en una orden de venta.

**Decisión.**
- Un agente nuevo, el **Estratega de venta** (módulo `decision`), combina el precio en vivo y el
  pronóstico (pedidos al Analista y al Predictor vía supervisor) con una **regla simple**:
  esperar, vender ahora o «sin señal clara», con umbral configurable (3 %).
- Siempre explica el motivo con números y muestra «la decisión de vender siempre es tuya».
- Si los datos están desactualizados, no recomienda.
- Su acierto se mide con `scripts/backtest_selling_rule.py`: para cada día pasado se pronostica
  solo con los datos de ese momento y se compara con el precio 7 días hábiles después; se
  compara con la referencia «vender siempre de inmediato».

**Consecuencias.** Es auditable por el jurado y el caficultor. Con modelos de pronóstico
conservadores, la regla puede responder «sin señal clara» la mayoría de días: es preferible a
recomendar sin fundamento. El umbral final se decide con los datos reales y el asesor de tesis.

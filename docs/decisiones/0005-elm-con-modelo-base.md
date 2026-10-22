# 0005 — ELM comparado con un modelo base

**Estado:** aceptada (Iteración 2)

**Decisión:** el Predictor valida cada modelo con los últimos 30 precios (MAPE) y usa el de menor
error: una ELM (Deina et al., 2022) o un modelo ingenuo con deriva. El rango del pronóstico es
± el MAPE de validación.

**Consecuencias:** el pronóstico nunca es peor que el método más simple y la elección queda
justificada con datos para el capítulo de resultados.

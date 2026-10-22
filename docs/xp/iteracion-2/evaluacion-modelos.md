# Evaluación de modelos de pronóstico (T19, PA-06-1)

**Iteración:** 2 · **Responsable:** Chavez Canaquiri, J. X.

## Método

1. Serie diaria de precios en S/ por quintal (días hábiles).
2. Para cada horizonte de validación (7, 15 y 30 días): se entrena con todo menos los últimos
   N días, se pronostican esos N días y se mide el MAPE contra lo que realmente ocurrió.
3. Modelos: ELM (ventana 10, 40 neuronas ocultas, regularización 0,001, semilla 42; según
   Deina et al., 2022) y modelo ingenuo con deriva (referencia).
4. En producción, el Agente Predictor repite la validación de 30 días cada vez que pronostica y
   usa el modelo con menor MAPE.

Reproducir: `PYTHONPATH=src python scripts/evaluate_forecast_models.py --days 1825`

## Resultados con datos SINTÉTICOS (solo para verificar el procedimiento)

Datos generados por `seed_demo_data.py` (caminata aleatoria, 523 días hábiles).
**No usar en la tesis.**

| Modelo | MAPE 7 días | MAPE 15 días | MAPE 30 días |
|---|---|---|---|
| ELM | 1,39 % | 1,35 % | 1,69 % |
| Ingenuo con deriva | 1,19 % | 1,45 % | 1,60 % |

En una caminata aleatoria no hay patrón que aprender, así que es esperable que la ELM no supere
claramente al modelo ingenuo. Con datos reales el resultado puede ser distinto.

## Resultados con datos REALES (completar)

> Ejecutar después de `load_price_history.py --years 5` y pegar la tabla aquí.
> Esta tabla es la que va al capítulo de resultados de la tesis.

| Modelo | MAPE 7 días | MAPE 15 días | MAPE 30 días |
|---|---|---|---|
| ELM | | | |
| Ingenuo con deriva | | | |

**Modelo elegido:** ______ · **Justificación:** ______

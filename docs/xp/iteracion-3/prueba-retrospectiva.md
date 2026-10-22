# Prueba retrospectiva de «¿Vendo ahora o espero?» (T30, HU05)

**Responsable:** Chavez Canaquiri, J. X. · **Decisión relacionada:** [0007](../../decisiones/0007-regla-de-venta-explicable.md)

## Qué se mide

Para cada día hábil del periodo evaluado:

1. Se pronostica **solo con los datos que había hasta ese día** (mismo criterio de elección de
   modelo que el Agente Predictor: ELM o modelo base, el de menor MAPE).
2. Se aplica la regla de venta con el umbral a probar.
3. Se compara con lo que pasó: si el precio **7 días hábiles después** fue mayor, «Esperar» acertó;
   si no, «Vender ahora» acertó. «Sin señal clara» no se califica.
4. Referencia: «vender siempre de inmediato».

```bash
make backtest      # 250 días hábiles, umbrales 1 %, 2 % y 3 %
```

## Resultado con datos SINTÉTICOS (solo para comprobar que el script funciona)

Base de datos de demostración (`make demo`, caminata aleatoria), 120 días hábiles:

| Umbral | Vender ahora | Esperar | Sin señal clara | Acierto de la regla | «Vender siempre» |
|---|---|---|---|---|---|
| 1 % | 9 | 1 | 110 | 60,0 % | 49,2 % |
| 3 % | 0 | 0 | 120 | — | 49,2 % |

Con una caminata aleatoria no hay nada que pronosticar: la regla casi siempre se abstiene
(«sin señal clara»), que es el comportamiento esperado. **Estos números no sirven para la tesis.**

## Resultado con datos reales (completar)

Cargar 5 años reales (`load_price_history.py --years 5`) y ejecutar `make backtest`.

| Umbral | Vender ahora | Esperar | Sin señal clara | Acierto de la regla | «Vender siempre» |
|---|---|---|---|---|---|
| 1 % | | | | | |
| 2 % | | | | | |
| 3 % | | | | | |

**Umbral elegido:** ____ (acordar con el asesor). Configurar `SELLING_THRESHOLD` y
`SELLING_HIT_RATE_PCT` (la app muestra ese acierto bajo la recomendación).

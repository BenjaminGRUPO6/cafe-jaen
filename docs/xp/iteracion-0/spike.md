# Spike de fuentes del precio mundial y LLM (T01)

**Iteración:** 0 · **Responsable:** Chavez Canaquiri, J. X. · **Tiempo máximo:** 4 h

## Preguntas

1. ¿Qué webs gratuitas publican la cotización del café arábica de la bolsa de Nueva York
   (ICE, contrato C) y con cuánto **retraso real**?
2. ¿Coinciden entre sí? ¿Cuánto se alejan unas de otras?
3. ¿Aguantan una consulta por minuto sin bloquearnos?
4. ¿Responden el BCRP (tipo de cambio) y el LLM?

## Candidatas

| Web | Cómo se lee | Estado en el código |
|---|---|---|
| Yahoo Finance (`KC=F`) | Librería `yfinance`, velas de 1 minuto | Adaptador `YahooQuotationSource` |
| Stooq (`KC.F`) | CSV público `https://stooq.com/q/l/?s=kc.f&f=sd2t2c&h&e=csv` | Adaptador `StooqQuotationSource` (formato y zona horaria por confirmar) |
| Barchart, Investing, MarketWatch u otras | Revisar si ofrecen acceso permitido (API o CSV) | Sin adaptador: agregar uno si el spike lo justifica |
| Datos de ICE en tiempo real | Requieren licencia pagada | Fuera del alcance (mejora futura) |

Tipo de cambio: API del BCRP, serie `PD04640PD`. LLM: API de Anthropic (opcional) con el modelo
por palabras clave como respaldo.

## Cómo se verifica

Con la bolsa abierta (de 03:15 a 12:30 de Lima en horario de verano de Nueva York; de 04:15 a
13:30 en invierno):

```bash
make spike          # consulta cada web cada minuto durante 60 min
```

El script imprime, por minuto y por web: precio, hora de la cotización, retraso frente a la hora
actual y diferencia con la mediana.

## Resultados

> El entorno donde se generó el código no tenía acceso a internet: este resultado debe
> completarse antes del planning game de la Iteración 1.

| Web | ¿Respondió los 60 min? | Retraso típico | Diferencia máx. con la mediana | Observaciones |
|---|---|---|---|---|
| Yahoo Finance | | | | |
| Stooq | | | | |

```
(pegar la salida de spike_sources.py)
```

## Decisión

- Se usan en `QUOTATION_SOURCES` las webs que respondieron siempre y se mantuvieron dentro de
  ±1 % de la mediana.
- Si solo una web es utilizable, el Cliente decide si se acepta una sola fuente (el consenso
  funciona igual, pero sin respaldo) o se agrega otra.
- Si la hora de Stooq no coincide con la de Yahoo, ajustar `STOOQ_TIMEZONE`.
- El retraso medido se informa en la app y en el manual («cotización de las hh:mm»).

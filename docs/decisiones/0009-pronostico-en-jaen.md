# 0009 — Pronóstico estimado en Jaén, alineado con el indicador TPP

**Estado:** aceptada (v1.1, 04/11/2026)

**Contexto.** La ficha de la TPP pide al caficultor predecir el precio del **café pergamino en
S/ por quintal** en una fecha objetivo, y lo compara con el precio real de la cooperativa. La
pantalla de pronóstico solo mostraba el precio de la **bolsa** (≈ S/ 1500), que no es el número
que el caficultor predice (≈ S/ 1100 en Jaén): la app no lo ayudaba con ese indicador.

**Decisión.** La pantalla «7 días» muestra, para cada día, el pronóstico de la bolsa y el
**estimado en Jaén** = pronóstico de la bolsa × porcentaje que pagan hoy las cooperativas por el
tipo de café elegido (el mismo porcentaje de HU12). El cálculo es una multiplicación de
presentación y se hace en el front-end (`features/forecast/localForecast.ts`, con pruebas) a
partir de dos respuestas existentes (`/forecast` y `/prices/live`): los módulos `forecasting` y
`market` siguen sin conocerse, como exige el contrato de independencia.

**Consecuencias.** El grupo experimental ve el pronóstico en la misma unidad que predice en la
ficha de la TPP. Para la tesis se fijan: fecha objetivo = 7 días, Pr = precio que paga la
cooperativa de la zona ese día, en S/ por quintal de pergamino. Si más adelante el estimado
necesitara reglas propias (por ejemplo, porcentajes que cambian en el tiempo), se moverá al
backend como un caso de uso del módulo `orchestration`.

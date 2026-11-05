# 0010 — Solo datos reales

**Estado:** aceptada (v1.6, noviembre de 2026). Reemplaza el modo demostración de la
[decisión 0008](0008-herramientas-simples.md).

**Contexto:** para mostrar la app a cualquier hora usábamos una fuente sintética (una caminata
aleatoria) y un histórico generado. Eso mezclaba datos inventados con la intervención del
experimento, y los indicadores de la tesis (TAI, NCP y TPP) deben medirse sobre precios reales.

**Decisión:**
- El Recolector consulta solo webs reales: Yahoo Finance (`KC=F`) y Stooq (`KC.F`); el tipo de
  cambio es el del BCRP. Se eliminaron la fuente sintética y el script de datos de demostración.
- El histórico de 5 años se carga desde Yahoo Finance y, si no responde, desde Stooq
  (`LoadPriceHistory`), al arrancar en Render y con `python dev.py datos` en local.
- La migración 0007 borra de las bases existentes lo que generó la demostración y los
  pronósticos calculados sobre ese histórico; conserva usuarios, cooperativas reales y precios
  anotados por el equipo.
- Los precios de cooperativas son los que el equipo anota tras preguntar a cada una. Para
  **demostraciones**, el equipo puede cargar desde «Equipo → Cooperativas» precios sintéticos de
  6 cooperativas llamadas «Cooperativa JAENPERU sintético A…F», calculados sobre el precio
  **real** de la bolsa de cada día. La app avisa en el estimado cuántos precios son sintéticos y
  se borran con un toque antes de trabajar con el grupo experimental.

**Consecuencias:** el precio solo se mueve con la bolsa de Nueva York abierta (lunes a viernes,
04:15–13:30 hora de Nueva York); el estimado en Jaén aparece cuando el equipo anota precios de
cooperativas; la app depende de que al menos una web responda (con ninguna, muestra el último
precio y avisa que está desactualizado). La evaluación de modelos y la prueba retrospectiva de la
regla de venta deben recalcularse con el histórico real.

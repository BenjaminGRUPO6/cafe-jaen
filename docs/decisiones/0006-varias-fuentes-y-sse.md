# 0006 — Varias webs del mismo precio, consolidadas por mediana, y flujo en vivo con SSE

**Estado:** aceptada (v3.0, 21/10/2026)

**Contexto.** El caficultor debe ver «como en la bolsa» a cuánto se vende el café en el mundo.
Ninguna web gratuita es totalmente confiable (caídas, cambios de formato, datos raros) y los
datos de ICE al segundo requieren licencia.

**Decisión.**
- Consultar el precio de la bolsa de Nueva York (café arábica, contrato C) en **varias webs**
  (un adaptador `QuotationSource` por web) **cada minuto** con la bolsa abierta.
- Publicar la **mediana** y descartar la web que se aleje más de 1 %; si las webs no coinciden,
  no publicar y conservar el último valor válido.
- Enviar cada precio nuevo al celular con **Server-Sent Events** (`GET /api/prices/stream`):
  el flujo es solo del servidor al cliente, funciona sobre HTTP normal y es más simple que
  WebSockets. El cliente usa `fetch` para poder enviar el token de sesión.
- Mostrar siempre la **hora de la cotización** y marcar el precio como desactualizado si pasa
  de 20 min con la bolsa abierta.

**Consecuencias.** El precio es más confiable y la pantalla se actualiza sola. El «tiempo real»
tiene el retraso de las webs gratuitas (se mide en el spike) y se informa con honestidad.
Agregar una web es agregar un adaptador.

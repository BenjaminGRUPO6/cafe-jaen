# 0002 — Agentes coordinados por un supervisor

**Estado:** aceptada (Iteración 0)

**Decisión:** los agentes no se llaman entre sí. Todo pedido es un `AgentMessage` que pasa por el
supervisor (`DispatchRequest` + `LangGraphAgentRouter`). Los agentes viven en la capa de
aplicación; LangGraph es solo el adaptador que enruta.

**Consecuencias:** módulos desacoplados, trazas de todas las interacciones (evidencia de
habilidad social para la tesis) y un único lugar donde manejar fallos.

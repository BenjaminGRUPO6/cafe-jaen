# Metáfora del sistema (práctica XP)

> **«La pizarra de la bolsa en el bolsillo».**

Un **supervisor**, como el presidente de una cooperativa, recibe los encargos y los reparte entre
cinco especialistas:

| Especialista | En el código | Qué hace |
|---|---|---|
| El que mira varias pizarras a la vez | `CollectorAgent` | Cada minuto anota el precio de la bolsa de Nueva York en el que coinciden varias webs |
| El que saca las cuentas | `AnalystAgent` | Traduce la cotización a soles por quintal y arma el gráfico |
| El que mira el cielo | `ForecasterAgent` | Anticipa hacia dónde irá el precio en la semana |
| El consejero | `StrategistAgent` | Con el precio y el pronóstico, aconseja si vender hoy o esperar, y explica por qué |
| El que conversa | `AdvisorAgent` | Responde las dudas del caficultor con palabras sencillas |

Ningún especialista habla directamente con otro: todo pasa por el presidente (`DispatchRequest`),
que anota cada encargo en el cuaderno de actas (`agent_traces`).

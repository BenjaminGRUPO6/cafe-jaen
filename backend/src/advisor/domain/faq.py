"""Preguntas frecuentes del caficultor con respuestas preparadas por el equipo.

Orden de búsqueda (ver AnswerQuestion):
1. Frases de varias palabras («como se calcula»): ganan a las herramientas de datos, así
   «¿cómo se calcula el precio?» explica la fórmula en lugar de dar el precio.
2. Herramientas de datos (precio, histórico, pronóstico, venta, cooperativas).
3. Palabras sueltas («pergamino», «hola»): solo si ninguna herramienta respondió, así
   «¿cuánto pagan por café especial?» da el dato y no la definición de «especial».

Para agregar una pregunta basta con sumar una entrada: `triggers` van en minúsculas y sin
tildes. Las respuestas no llevan precios: los números del día siempre salen de los agentes.
"""

from dataclasses import dataclass

from advisor.domain.text import normalize

TEAM_SOURCE = "Equipo Café Jaén"

# Cooperativas cafetaleras con sede en Jaén (fuentes públicas: JNC, Agraria.pe, OCIA).
# Es el mismo catálogo inicial de la migración 0005; el equipo puede ampliarlo en «Equipo».
JAEN_COOPERATIVES = (
    "CENFROCAFE (Central Fronteriza del Norte de Cafetaleros)",
    "Cooperativa de Servicios Múltiples Sol & Café",
    "Cooperativa de Servicios Múltiples Jesús Solidario",
    "Cooperativa Agraria Cafetalera Perú Andino",
    "Cooperativa Agraria Café del Norte",
)


@dataclass(frozen=True)
class FaqEntry:
    topic: str
    triggers: tuple[str, ...]
    answer: str


FAQ: tuple[FaqEntry, ...] = (
    FaqEntry(
        "como_se_calcula",
        (
            "como se calcula",
            "de donde sale el precio",
            "la formula",
            "como sacan",
            "como convierten",
            "como calculan",
        ),
        "El precio de la bolsa llega en centavos de dólar por libra (¢/lb). Lo pasamos a soles "
        "por quintal así: ¢/lb ÷ 100 × 101,41 libras (los 46 kg del quintal) × tipo de cambio del "
        "BCRP. El «precio estimado en Jaén» es ese precio × el porcentaje que pagan las "
        "cooperativas (la mediana de los precios anotados en los últimos 30 días). En la pantalla "
        "«Precio» el botón «¿Cómo se calcula?» muestra la cuenta con los números de hoy.",
    ),
    FaqEntry(
        "por_que_jaen_es_distinto",
        (
            "por que es distinto",
            "por que es diferente",
            "por que pagan menos",
            "pagan menos",
            "por que en jaen",
            "diferencia",
            "por que no pagan",
        ),
        "La bolsa de Nueva York cotiza café verde (oro) listo para exportar. En Jaén se vende "
        "pergamino, que todavía hay que pilar, seleccionar, transportar y exportar; además cuenta "
        "la calidad de cada lote. Por eso las cooperativas pagan un porcentaje del precio de la "
        "bolsa, y ese porcentaje es el que usamos para el estimado en Jaén.",
    ),
    FaqEntry(
        "fuentes",
        ("de donde sacan", "fuente", "de donde viene", "confiable el precio", "es real el precio"),
        "El precio de la bolsa lo consultamos cada minuto en Yahoo Finance y Stooq (contrato café "
        "C de la bolsa ICE de Nueva York) y publicamos el valor en que coinciden. "
        "El tipo de cambio es el oficial del Banco Central de Reserva (BCRP). Lo que paga "
        "cada cooperativa lo anota el equipo preguntando directamente. En «Precio» están los "
        "botones para abrir cada fuente.",
    ),
    FaqEntry(
        "retraso",
        ("tiempo real", "atrasado", "retraso", "demora", "minutos tarde"),
        "Las webs gratuitas publican la bolsa con algunos minutos de retraso; los datos al segundo "
        "cuestan una licencia. Por eso la app siempre muestra la hora exacta de la cotización.",
    ),
    FaqEntry(
        "horario",
        (
            "cuando abre",
            "a que hora abre",
            "a que hora cierra",
            "cuando cierra",
            "horario de la bolsa",
            "que dias abre",
        ),
        "El café de la bolsa de Nueva York se negocia de lunes a viernes de 4:15 a 13:30, hora "
        "de Nueva York. En Lima es la misma hora de noviembre a marzo y una hora antes el resto "
        "del año (de 3:15 a 12:30). Fuera de ese horario, la app muestra el último precio y "
        "avisa «Bolsa cerrada».",
    ),
    FaqEntry(
        "quintal",
        ("que es un quintal", "cuantos kilos", "cuanto pesa un quintal", "que es quintal"),
        "Un quintal son 46 kilos (unas 101 libras). En la app todos los precios están en soles por "
        "quintal para compararlos fácil con lo que paga la cooperativa.",
    ),
    FaqEntry(
        "pergamino",
        ("pergamino", "cafe oro", "cafe verde", "que es oro"),
        "El café pergamino es el grano seco que todavía conserva su cascarilla: es lo que el "
        "productor vende en Jaén. Al pilarlo (quitar la cascarilla) se obtiene el café oro "
        "o verde, que es el que se exporta y el que cotiza la bolsa.",
    ),
    FaqEntry(
        "bolsa",
        (
            "que es la bolsa",
            "bolsa de nueva york",
            "que es ice",
            "contrato c",
            "que es la bolsa de",
        ),
        "La bolsa ICE de Nueva York es donde se fija el precio internacional del café arábica "
        "(contrato «café C»). Las cooperativas y exportadores de Jaén toman ese precio como "
        "referencia para pagar al productor.",
    ),
    FaqEntry(
        "tipo_de_cambio",
        ("tipo de cambio", "dolar", "bcrp"),
        "Usamos el tipo de cambio interbancario de venta que publica el Banco Central de Reserva "
        "del Perú (BCRP) cada día hábil. Si el dólar sube, el precio en soles también sube aunque "
        "la bolsa no se mueva.",
    ),
    FaqEntry(
        "tipos_de_cafe",
        ("tipos de cafe", "organico", "especial", "convencional", "certificad"),
        "En la app hay tres tipos: convencional (sin certificación), orgánico (certificado, suele "
        "pagarse más) y especial (lotes de alta calidad en taza). El estimado en Jaén se calcula "
        "por separado para cada tipo porque las cooperativas pagan distinto por cada uno.",
    ),
    FaqEntry(
        "como_pronostica",
        (
            "como pronostica",
            "como sabe el pronostico",
            "es seguro el pronostico",
            "confiable el pronostico",
            "como predice",
        ),
        "El Agente Predictor prueba dos modelos con el histórico de la bolsa (una red ELM y un "
        "modelo base) y usa el que tuvo menos error. Muestra el valor esperado y un rango para "
        "cada día: es una referencia, no una garantía.",
    ),
    FaqEntry(
        "como_decide",
        ("como decide", "por que recomienda", "como sabe si vender", "en que se basa"),
        "El Agente Estratega compara el precio de hoy con el pronóstico de la próxima semana. Si "
        "se espera que suba más de 3 %, recomienda esperar; si se espera que baje más de 3 %, "
        "vender ahora; si no, «sin señal clara». Siempre muestra el motivo con números.",
    ),
    FaqEntry(
        "cooperativas",
        ("que cooperativas", "cuales cooperativas", "cooperativas de jaen", "cooperativas hay"),
        "Algunas cooperativas cafetaleras con sede en Jaén son: "
        + "; ".join(JAEN_COOPERATIVES)
        + ". En «Precio» → «Por cooperativa» ves lo que pagó cada una según lo anotado por el "
        "equipo.",
    ),
    FaqEntry(
        "humedad",
        ("humedad", "secado", "secar"),
        "Las cooperativas suelen pedir pergamino bien seco, alrededor de 11 a 12 % de humedad; "
        "con más humedad pueden descontar del precio. Confirma la exigencia con tu cooperativa.",
    ),
    FaqEntry(
        "sin_senal",
        ("sin senal", "sin internet", "sin datos", "offline"),
        "Si te quedas sin señal, la app te muestra el último precio que vio, con su fecha y hora. "
        "Cuando vuelva la señal se actualiza sola.",
    ),
    FaqEntry(
        "instalar",
        ("instalar", "descargar la app", "icono", "pantalla de inicio"),
        "En el celular abre la app en Chrome, toca los tres puntos y elige «Instalar app» o "
        "«Agregar a pantalla de inicio». Queda como un ícono y abre más rápido.",
    ),
    FaqEntry(
        "privacidad",
        ("mis datos", "privacidad", "comparten", "contrasena"),
        "Solo guardamos tu celular, tu contraseña cifrada y la fecha de tu consentimiento. Nadie "
        "del equipo puede ver tu contraseña y tus datos se usan solo para la investigación.",
    ),
    FaqEntry(
        "ayuda",
        ("que puedes hacer", "ayuda", "como funciona", "que sabes", "para que sirve"),
        "Puedo decirte: el precio del café hoy («¿a cuánto está?»), cómo se movió («últimos 30 "
        "días»), el pronóstico («¿subirá la próxima semana?»), si conviene vender («¿vendo o "
        "espero?») y lo que pagan las cooperativas («¿cuánto paga CENFROCAFE?»). También explico "
        "cómo se calcula cada número, qué es un quintal, el pergamino o la bolsa.",
    ),
    FaqEntry(
        "saludo",
        ("hola", "buenos dias", "buenas tardes", "buenas noches", "buenas"),
        "¡Hola! Soy el asesor de Café Jaén. Pregúntame por el precio de hoy, el pronóstico, si "
        "conviene vender o lo que pagan las cooperativas. Escribe «ayuda» para ver más ejemplos.",
    ),
    FaqEntry(
        "gracias",
        ("gracias", "muy amable", "chevere", "excelente"),
        "¡Con gusto! Pregúntame de nuevo más tarde: el precio se actualiza cada minuto.",
    ),
    FaqEntry(
        "despedida",
        ("adios", "chau", "hasta luego", "nos vemos"),
        "¡Hasta pronto! Que te vaya bien con la cosecha.",
    ),
)


def find_faq(question: str, phrases_only: bool) -> FaqEntry | None:
    """Primera entrada que coincide, en el orden de FAQ.

    Con `phrases_only` solo cuentan las frases de varias palabras (paso 1 del orden).
    """
    text = normalize(question)
    words = set("".join(c if c.isalnum() else " " for c in text).split())
    for entry in FAQ:
        for trigger in entry.triggers:
            if " " in trigger:
                if trigger in text:
                    return entry
            elif not phrases_only and _word_matches(trigger, text, words):
                return entry
    return None


def _word_matches(trigger: str, text: str, words: set[str]) -> bool:
    # Palabra completa («hola», no «holanda»); las raíces largas también valen por prefijo
    # («certificad» → certificado, certificación)
    return trigger in words or (len(trigger) > 7 and trigger in text)

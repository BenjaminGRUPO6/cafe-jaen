import logging

from advisor.domain.answer import NO_INFORMATION, SERVICE_UNAVAILABLE, Answer
from advisor.domain.grounding import is_grounded
from advisor.domain.ports.language_model import LanguageModel
from advisor.domain.templates import template_answer
from shared.domain.contract import AgentName
from shared.domain.ports.agent_gateway import AgentGateway

logger = logging.getLogger(__name__)
MAX_QUESTION_LENGTH = 500


class AnswerQuestion:
    """HU08: responde preguntas en lenguaje natural usando datos de los otros agentes."""

    def __init__(self, language_model: LanguageModel, gateway: AgentGateway) -> None:
        self._language_model = language_model
        self._gateway = gateway

    def execute(self, question: str) -> Answer:
        question = question.strip()[:MAX_QUESTION_LENGTH]
        tool = self._language_model.choose_tool(question) if question else None
        if tool is None:
            return Answer(NO_INFORMATION)

        # El asesor nunca accede a la BD: pide los datos al agente dueño, vía supervisor
        reply = self._gateway.request(
            AgentName.ADVISOR, tool.spec.receiver, tool.spec.action, tool.arguments
        )
        if reply.is_failure:
            return Answer(SERVICE_UNAVAILABLE, used_tool=tool.spec.action)

        text = self._language_model.write_answer(question, tool.spec.action, reply.content)
        if not is_grounded(text, reply.content):
            logger.warning("Respuesta del LLM con números no respaldados; se usa la plantilla")
            text = template_answer(tool.spec.action, reply.content)
        sources = tuple(reply.content.get("sources", ["ICE", "BCRP"]))
        return Answer(text, sources, tool.spec.action)

from advisor.application.answer_question import AnswerQuestion
from shared.domain.agent_message import AgentMessage
from shared.domain.contract import Action, AgentName
from shared.domain.ports.clock import Clock


class AdvisorAgent:
    """Agente Asesor: conversa con el caficultor en lenguaje sencillo."""

    name = AgentName.ADVISOR

    def __init__(self, answer_question: AnswerQuestion, clock: Clock) -> None:
        self._answer_question = answer_question
        self._clock = clock

    def handle(self, message: AgentMessage) -> AgentMessage:
        if message.action != Action.ANSWER_QUESTION:
            return message.reply_failure(
                f"Acción no soportada: {message.action}", self._clock.now()
            )
        answer = self._answer_question.execute(str(message.content.get("question", "")))
        return message.reply_inform(
            {"answer": answer.text, "sources": list(answer.sources), "used_tool": answer.used_tool},
            self._clock.now(),
        )

from datetime import datetime

from shared.domain.agent_message import AgentMessage, Performative

NOW = datetime(2026, 11, 4, 9, 0)


def test_reply_inverts_sender_and_keeps_conversation() -> None:
    request = AgentMessage.request("api", "analyst", "get_live_price", {}, NOW)

    reply = request.reply_inform({"price_soles": 1140.89}, NOW)

    assert (reply.sender, reply.receiver) == ("analyst", "api")
    assert reply.performative is Performative.INFORM
    assert reply.conversation_id == request.conversation_id
    assert reply.id != request.id


def test_failure_reply_carries_the_reason() -> None:
    request = AgentMessage.request("api", "analyst", "get_live_price", {}, NOW)

    reply = request.reply_failure("sin datos", NOW)

    assert reply.is_failure
    assert reply.content == {"reason": "sin datos"}


import sys
from pathlib import Path
from types import SimpleNamespace

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SRC_DIRECTORY))

import agent


def make_response(content="", tool_calls=None):
    """Create a predictable mock Ollama response."""

    message = SimpleNamespace(
        content=content,
        tool_calls=tool_calls or [],
    )
    return SimpleNamespace(message=message)


def make_tool_call(name, arguments):
    """Create a mock tool-call request from the model."""

    function = SimpleNamespace(
        name=name,
        arguments=arguments,
    )
    return SimpleNamespace(function=function)


def test_agent_returns_normal_answer_without_tool(monkeypatch):
    def fake_chat(**kwargs):
        return make_response("Try restarting your laptop.")

    monkeypatch.setattr(agent.ollama, "chat", fake_chat)

    result = agent.run_agent("How do I fix my laptop?")

    assert result == "Try restarting your laptop."


def test_agent_executes_ticket_tool(monkeypatch):
    responses = [
        make_response(
            tool_calls=[
                make_tool_call(
                    "get_ticket_status",
                    {"ticket_id": "HD-1001"},
                )
            ]
        ),
        make_response("Ticket HD-1001 is In Progress."),
    ]
    recorded_calls = []

    def fake_chat(**kwargs):
        recorded_calls.append(kwargs)
        return responses.pop(0)

    monkeypatch.setattr(agent.ollama, "chat", fake_chat)

    result = agent.run_agent("Check ticket HD-1001.")

    assert result == "Ticket HD-1001 is In Progress."
    assert len(recorded_calls) == 2

    # The second model call should include the actual Python tool result.
    messages = recorded_calls[1]["messages"]
    tool_messages = [
        message for message in messages
        if isinstance(message, dict) and message.get("role") == "tool"
    ]

    assert len(tool_messages) == 1
    assert '"status": "In Progress"' in tool_messages[0]["content"]
    assert '"success": true' in tool_messages[0]["content"]


def test_agent_rejects_unavailable_tool(monkeypatch):
    responses = [
        make_response(
            tool_calls=[
                make_tool_call(
                    "delete_all_tickets",
                    {},
                )
            ]
        ),
        make_response("That tool is unavailable."),
    ]
    recorded_calls = []

    def fake_chat(**kwargs):
        recorded_calls.append(kwargs)
        return responses.pop(0)

    monkeypatch.setattr(agent.ollama, "chat", fake_chat)

    result = agent.run_agent("Delete all tickets.")

    assert result == "That tool is unavailable."

    messages = recorded_calls[1]["messages"]
    tool_messages = [
        message for message in messages
        if isinstance(message, dict) and message.get("role") == "tool"
    ]

    assert len(tool_messages) == 1
    assert "This tool is not available." in tool_messages[0]["content"]


def test_agent_stops_at_tool_round_limit(monkeypatch):
    monkeypatch.setattr(agent, "MAX_TOOL_ROUNDS", 2)

    def fake_chat(**kwargs):
        return make_response(
            tool_calls=[
                make_tool_call(
                    "get_ticket_status",
                    {"ticket_id": "HD-1001"},
                )
            ]
        )

    monkeypatch.setattr(agent.ollama, "chat", fake_chat)

    result = agent.run_agent("Check ticket HD-1001.")

    assert "allowed number of tool rounds" in result



def test_conversation_history_is_preserved_between_requests(monkeypatch):
    responses = [
        make_response("Ticket HD-1004 created."),
        make_response("Ticket HD-1004 is Open."),
    ]
    chat_calls = []

    def fake_chat(**kwargs):
        chat_calls.append(kwargs)
        return responses.pop(0)

    monkeypatch.setattr(agent.ollama, "chat", fake_chat)

    conversation_history = []

    first_answer = agent.run_agent(
        "Create a ticket for my email issue.",
        conversation_history,
    )

    second_answer = agent.run_agent(
        "What is the status of the ticket you just created?",
        conversation_history,
    )

    assert first_answer == "Ticket HD-1004 created."
    assert second_answer == "Ticket HD-1004 is Open."

    # The second request should include the first request.
    second_messages = chat_calls[1]["messages"]

    assert any(
        isinstance(message, dict)
        and message.get("content") == "Create a ticket for my email issue."
        for message in second_messages
    )

    # The previous assistant response should also be available.
    assert any(
        getattr(message, "content", None) == "Ticket HD-1004 created."
        for message in second_messages
    )


def test_agent_calls_list_tickets(monkeypatch):
    tool_call = make_tool_call("list_tickets", {})
    responses = [
        make_response("", [tool_call]),
        make_response("There are 3 tickets."),
    ]
    chat_calls = []

    def fake_chat(**kwargs):
        chat_calls.append(kwargs)
        return responses.pop(0)

    monkeypatch.setattr(agent.ollama, "chat", fake_chat)

    result = agent.run_agent("Show me all helpdesk tickets.")

    assert result == "There are 3 tickets."
    assert len(chat_calls) == 2

    # Confirm the tool result was passed back to the model.
    tool_messages = [
        message
        for message in chat_calls[1]["messages"]
        if isinstance(message, dict)
        and message.get("role") == "tool"
        and message.get("name") == "list_tickets"
    ]

    assert len(tool_messages) == 1
    assert '"success": true' in tool_messages[0]["content"]


def test_agent_handles_unknown_tool(monkeypatch):
    tool_call = make_tool_call("unknown_tool", {})
    responses = [
        make_response("", [tool_call]),
        make_response("I couldn't use that tool."),
    ]

    def fake_chat(**kwargs):
        return responses.pop(0)

    monkeypatch.setattr(agent.ollama, "chat", fake_chat)

    result = agent.run_agent("Use an unknown tool.")

    assert result == "I couldn't use that tool."


def test_agent_handles_invalid_tool_arguments(monkeypatch):
    # The model provides an unexpected argument.
    tool_call = make_tool_call(
        "create_ticket",
        {"unexpected_argument": "value"},
    )
    responses = [
        make_response("", [tool_call]),
        make_response("I couldn't create the ticket because the arguments were invalid."),
    ]

    def fake_chat(**kwargs):
        return responses.pop(0)

    monkeypatch.setattr(agent.ollama, "chat", fake_chat)

    result = agent.run_agent("Create a ticket.")

    assert "couldn't create the ticket" in result.lower()


def test_agent_reports_ticket_creation_failure(monkeypatch):
    # Force the actual tool to reject an empty title.
    tool_call = make_tool_call("create_ticket", {"title": "   "})
    responses = [
        make_response("", [tool_call]),
        make_response("The ticket could not be created because the title was empty."),
    ]

    def fake_chat(**kwargs):
        return responses.pop(0)

    monkeypatch.setattr(agent.ollama, "chat", fake_chat)

    result = agent.run_agent("Create a ticket with an empty title.")

    assert "couldn't create the ticket" in result.lower()


def test_agent_does_not_claim_ticket_created_after_tool_failure(monkeypatch):
    tool_call = make_tool_call(
        "create_ticket",
        {"title": "   "},
    )

    def fake_chat(**kwargs):
        return make_response("", [tool_call])

    monkeypatch.setattr(agent.ollama, "chat", fake_chat)

    result = agent.run_agent("Create a ticket.")

    assert "couldn't create the ticket" in result.lower()
    assert "successfully created" not in result.lower()


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

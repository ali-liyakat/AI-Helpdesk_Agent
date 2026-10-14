
import json
import ollama

from llm_client import SYSTEM_PROMPT
from ticket_tools import (
    create_ticket,
    get_ticket_status,
    list_tickets,
    update_ticket,
)

MODEL = "qwen3:4b"
MAX_TOOL_ROUNDS = 5

# Give the model a description of the tool it is allowed to request.
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_ticket_status",
            "description": (
                "Look up a fictional helpdesk ticket by its ID. "
                "Use this when the user asks about a ticket's status "
                "or details. Do not guess ticket information."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "Ticket ID, such as HD-1001",
                    }
                },
                "required": ["ticket_id"],
            },
        },
    },
        {
        "type": "function",
        "function": {
            "name": "create_ticket",
            "description": (
                "Create a new fictional helpdesk ticket when the user "
                "asks to report an IT problem or create a ticket. "
                "Use the user's issue as the ticket title. "
                "Use the requested priority if provided; otherwise "
                "use Medium. Never claim a ticket was created unless "
                "the tool confirms success."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "A short description of the IT issue",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["Low", "Medium", "High"],
                        "description": "Ticket priority; defaults to Medium",
                    },
                },
                "required": ["title"],
            },
        },
    },
    
    {
        "type": "function",
        "function": {
            "name": "list_tickets",
            "description": (
                "List fictional helpdesk tickets. Use this when the "
                "user asks to see, list, or find multiple tickets. "
                "If the user asks for tickets with a particular status, "
                "pass that status. Otherwise, list all tickets."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["Open", "In Progress", "Resolved"],
                        "description": (
                            "Optional status filter. Omit it to list "
                            "all tickets."
                        ),
                    }
                },
                "required": [],
            },
        },
    },
    
    {
        "type": "function",
        "function": {
            "name": "update_ticket",
            "description": (
                "Update the status or priority of an existing helpdesk "
                "ticket when the user explicitly requests a change. "
                "Use the ticket ID provided by the user or established "
                "in the conversation. Only report changes confirmed "
                "by the tool result."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "Ticket ID, such as HD-1001",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["Open", "In Progress", "Resolved"],
                        "description": "New ticket status, if requested",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["Low", "Medium", "High"],
                        "description": "New ticket priority, if requested",
                    },
                },
                "required": ["ticket_id"],
            },
        },
    },


]


# Only functions explicitly registered here can be executed.
AVAILABLE_FUNCTIONS = {
    "get_ticket_status": get_ticket_status,
    "create_ticket": create_ticket,
    "list_tickets": list_tickets,
    "update_ticket": update_ticket,
}


def run_agent(
    user_message: str,
    conversation_history: list | None = None,
) -> str:
    """Run the agent while preserving conversation history."""

    if conversation_history is None:
        conversation_history = []

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *conversation_history,
        {"role": "user", "content": user_message},
    ]

    for _ in range(MAX_TOOL_ROUNDS):
        response = ollama.chat(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
        )

        # Keep the assistant response, including any tool-call request.
        messages.append(response.message)

        tool_calls = response.message.tool_calls

        # If the model doesn't request a tool, its response is final.
        if not tool_calls:
            conversation_history[:] = messages[1:]
            return response.message.content.strip()

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            arguments = tool_call.function.arguments

            function_to_call = AVAILABLE_FUNCTIONS.get(function_name)

            if function_to_call is None:
                result = {
                    "success": False,
                    "error": "This tool is not available.",
                }
            else:
                try:
                    result = function_to_call(**arguments)
                except (TypeError, ValueError):
                    result = {
                        "success": False,
                        "error": "The tool received invalid arguments.",
                    }

            
            print(f"[Tool called: {function_name}]")

            # Preserve the actual result for the model.
            messages.append({
                "role": "tool",
                "name": function_name,
                "content": json.dumps(result),
            })

            # Do not let the model claim an action succeeded
            # when the tool explicitly reports failure.
            if (
                isinstance(result, dict)
                and result.get("success") is False
            ):
                error_message = result.get(
                    "error",
                    "The requested operation failed.",
                )

                if function_name == "create_ticket":
                    return f"I couldn't create the ticket: {error_message}"

                if function_name == "get_ticket_status":
                    return f"I couldn't retrieve the ticket: {error_message}"

                if function_name == "list_tickets":
                    return f"I couldn't list the tickets: {error_message}"


    return (
        "I couldn't complete the request within the allowed "
        "number of tool rounds. Please try again."
    )


if __name__ == "__main__":
    print("AI Helpdesk Agent")
    print("-" * 40)

    conversation_history = []

    while True:
        question = input("\nYou: ").strip()

        if question.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not question:
            continue

        try:
            answer = run_agent(question, conversation_history)
            print(f"\nAssistant: {answer}")
        except Exception as error:
            print(
                "\nSorry, I couldn't process that request. "
                "Check that Ollama is running and try again."
            )
            print(f"Technical details: {error}")

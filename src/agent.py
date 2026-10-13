
import json
import ollama

from llm_client import SYSTEM_PROMPT
from ticket_tools import get_ticket_status


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
    }
]


# Only functions explicitly registered here can be executed.
AVAILABLE_FUNCTIONS = {
    "get_ticket_status": get_ticket_status,
}


def run_agent(user_message: str) -> str:
    """Run the helpdesk agent and handle any requested tool calls."""

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": user_message,
        },
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

            # Send the real Python result back to the model.
            messages.append(
                {
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(result),
                }
            )

    return (
        "I couldn't complete the request within the allowed "
        "number of tool rounds. Please try again."
    )


if __name__ == "__main__":
    print("AI Helpdesk Agent")
    print("-" * 40)

    while True:
        question = input("\nYou: ").strip()

        if question.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not question:
            continue

        try:
            answer = run_agent(question)
            print(f"\nAssistant: {answer}")
        except Exception as error:
            print(
                "\nSorry, I couldn't process that request. "
                "Check that Ollama is running and try again."
            )
            print(f"Technical details: {error}")

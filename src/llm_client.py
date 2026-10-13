
import ollama


SYSTEM_PROMPT = """
You are a helpful AI IT helpdesk assistant.

Your responsibilities:
- Help users troubleshoot common IT problems.
- Explain solutions in clear, beginner-friendly language.
- Give numbered steps when explaining a procedure.
- Ask a follow-up question when you need more information.
- If you do not know the answer, say so honestly.
- Never claim that you accessed a system, checked a ticket,
  or performed an action unless a tool actually confirmed it.
- Do not ask users to share passwords or secret credentials.

Only provide IT helpdesk-related assistance.
"""


def ask_llm(prompt: str) -> str:
    """Send a user question to the local LLM."""

    response = ollama.chat(
        model="qwen3:4b",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return response["message"]["content"].strip()


if __name__ == "__main__":
    questions = [
        "My laptop cannot connect to Wi-Fi. What should I do?",
        "Can you tell me the current status of ticket HD-1001?",
        "Explain how to make a chocolate cake.",
    ]

    for question in questions:
        print(f"\nUser: {question}")
        print("-" * 50)
        print(f"Assistant: {ask_llm(question)}")

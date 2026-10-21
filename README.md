# AI Helpdesk Agent

A lightweight AI-powered IT helpdesk assistant built with Python, Ollama, Qwen3 4B, Streamlit, and SQLite.

The project demonstrates how an LLM can use tools to retrieve ticket information, create tickets, list tickets, and update ticket details. It uses fictional ticket data and runs locally.

## Features

- **AI chat interface:** Interact with the helpdesk through a Streamlit web app.
- **Ticket lookup:** Retrieve ticket details using a ticket ID.
- **Ticket creation:** Create tickets with a title and priority.
- **Ticket listing:** View all tickets or filter by status.
- **Ticket updates:** Change ticket status or priority.
- **SQLite persistence:** Store ticket records locally so changes survive application restarts.
- **Tool calling:** Let the LLM select from a controlled set of Python functions.
- **Automated tests:** Validate core ticket operations and database persistence.
- **Error handling:** Show a friendly message when the AI service is unavailable.

## Technology Stack

- Python
- Ollama
- Qwen3 4B (`qwen3:4b`)
- Streamlit
- SQLite
- pytest

## Project Structure

```text
AI-Helpdesk_Agent/
├── app.py
├── src/
│   ├── agent.py
│   ├── llm_client.py
│   ├── ticket_tools.py
│   └── database.py
├── tests/
├── docs/
├── .gitignore
└── README.md
```

## Prerequisites

- Python installed
- Git
- Ollama installed and running
- The `qwen3:4b` model downloaded

Download the model if needed:

```bash
ollama pull qwen3:4b
```

## Setup and Run

Clone the repository:

```bash
git clone https://github.com/ali-liyakat/AI-Helpdesk_Agent.git
cd AI-Helpdesk_Agent
```

Create and activate a virtual environment.

Windows Command Prompt:

```cmd
python -m venv venv
venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Start the web application:

```bash
python -m streamlit run app.py
```

Open the local URL displayed in the terminal, usually `http://localhost:8501`.

Ensure Ollama is running and the `qwen3:4b` model is available before sending requests.

## Example Requests

Try these prompts in the chat interface:

- `Check ticket HD-1001`
- `Show me all open tickets`
- `Create a high-priority ticket for my laptop Wi-Fi issue`
- `Mark HD-1002 as resolved`
- `Check ticket HD-9999`

## Run Tests

From the project root, with the virtual environment activated:

```bash
python -m pytest -v
```

## Architecture

1. The user enters a request in the Streamlit interface.
2. The agent sends the conversation to the local Ollama model.
3. The model chooses an available tool when ticket operations are needed.
4. The agent executes the corresponding Python function.
5. The ticket function reads or updates SQLite.
6. The agent returns a response to the user.

## Data and Limitations

This project uses fictional helpdesk data for demonstration and learning purposes. Ticket records are stored in a local SQLite database.

The current version is a local MVP, not a production helpdesk system. Before using real organizational data, additional security, access control, data protection, operational safeguards, and integration work would be required.

## Future Improvements

Potential future extensions include a dedicated ticket table view, ticket assignment, richer input validation, and integration with an organization's actual ticketing system.

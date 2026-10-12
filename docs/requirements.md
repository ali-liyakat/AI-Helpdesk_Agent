# AI Helpdesk Agent — Project Requirements

## 1. Project Overview

The AI Helpdesk Agent is a small AI-powered application that helps users with common IT support questions. It uses a locally running Large Language Model (LLM) through Ollama and Python-based tools to answer questions and perform simple helpdesk tasks.

This project uses fictional sample data for learning and development.

## 2. Project Goals

- Understand how an AI agent works in a practical application.
- Connect a Python application to a locally running LLM.
- Give the agent access to tools that perform specific tasks.
- Allow the agent to answer questions using a small knowledge base.
- Maintain relevant conversation context.
- Test the agent's behavior and document its limitations.

## 3. Initial Features

### Feature 1: General Helpdesk Questions

The agent should respond to common IT questions, such as how to reset a password or connect to a company VPN.

### Feature 2: Ticket Management

The agent should be able to:
- Create a support ticket.
- Check the status of an existing ticket.
- Look up fictional ticket details.

### Feature 3: Knowledge Base

The agent should answer questions using approved helpdesk documentation instead of relying only on the LLM's general knowledge.

### Feature 4: Conversation Context

The agent should use relevant earlier messages in the current conversation to understand follow-up questions.

### Feature 5: Testing and Evaluation

The project should include tests for tool behavior, ticket handling, and response quality.

## 4. Technology Stack

- **Language:** Python
- **LLM runtime:** Ollama
- **Model:** Qwen3 4B
- **Version control:** Git and GitHub
- **Development environment:** VS Code
- **Testing:** pytest (planned)
- **User interface:** To be decided later

## 5. Development Principles

- Build the application incrementally.
- Keep the code organized and reusable.
- Use fictional data only.
- Never commit secrets or local environment files.
- Test each feature before moving to the next.
- Record meaningful changes in Git commits.

## 6. Initial Scope Limitations

- No real company systems or customer data.
- No real password changes or privileged IT operations.
- Ticket management will initially use local sample data.
- The agent must not claim that an action succeeded unless the corresponding tool confirms it.

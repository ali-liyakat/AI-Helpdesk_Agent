
import sys
from pathlib import Path

import streamlit as st

# Allow app.py to import modules from the src folder.
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SRC_DIRECTORY))

from agent import run_agent


st.set_page_config(
    page_title="AI Helpdesk Agent",
    page_icon="🎫",
    layout="centered",
)

st.title("🎫 AI Helpdesk Agent")
st.caption(
    "A demo IT helpdesk assistant powered by Qwen3 and SQLite."
)

with st.sidebar:
    st.header("About")
    st.write(
        "Ask about tickets, create new tickets, "
        "list tickets, or update ticket status and priority."
    )
    st.divider()
    st.write("**Example requests**")
    st.write("- Check ticket HD-1001")
    st.write("- Show all open tickets")
    st.write("- Create a high-priority ticket for Wi-Fi issues")
    st.write("- Mark HD-1002 as resolved")

    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.rerun()


# Keep chat messages and agent history for this browser session.
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []


# Display previous messages.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Accept a new user message.
if prompt := st.chat_input("How can I help you today?"):
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Working on your request..."):
            try:
                answer = run_agent(
                    prompt,
                    st.session_state.conversation_history,
                )
            except Exception:
                answer = (
                    "I couldn't connect to the AI service. "
                    "Please check that Ollama is running and "
                    "the qwen3:4b model is available."
                )

            st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )

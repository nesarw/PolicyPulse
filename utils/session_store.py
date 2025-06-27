import streamlit as st


def init_session():
    """Initialize the session state for conversation and context_page if not already present."""
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
    if 'context_page' not in st.session_state:
        st.session_state.context_page = None


def append_message(role, content, rationale=None):
    """Append a message to the conversation in session state. Optionally include rationale for assistant replies."""
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
    entry = {'role': role, 'content': content}
    if role == 'assistant' and rationale:
        entry['rationale'] = rationale
    st.session_state.conversation.append(entry)


def get_conversation():
    """Return the conversation from session state."""
    return st.session_state.get('conversation', [])

import streamlit as st


def init_session():
    """Initialize the session state for conversation and context_page if not already present."""
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
    if 'context_page' not in st.session_state:
        st.session_state.context_page = None


def append_message(role, content):
    """Append a message to the conversation in session state."""
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
    st.session_state.conversation.append({'role': role, 'content': content})


def get_conversation():
    """Return the conversation from session state."""
    return st.session_state.get('conversation', [])

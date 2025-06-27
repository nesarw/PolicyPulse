import streamlit as st

# Sidebar for page selection
page = st.sidebar.selectbox('Current Page', ['My Policies', 'Claims', 'Billing'])

# Initialize conversation in session state if not present
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

st.title('PolicyPulse Chat')

# Chat area
st.subheader('Chat')
chat_container = st.container()

with chat_container:
    for msg in st.session_state.conversation:
        if msg['role'] == 'user':
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**Bot:** {msg['content']}")

# User input area
user_input = st.text_input('Type your message:', key='user_input')
send = st.button('Send')

if send and user_input.strip():
    st.session_state.conversation.append({'role': 'user', 'content': user_input.strip()})
    st.session_state.user_input = ''  # Clear input field
    st.experimental_rerun()

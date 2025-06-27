from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from utils.llm_client import LLMClient
from prompts.few_shot_templates import get_few_shot_prompt
from utils.session_store import init_session, append_message, get_conversation
import os
import re

# Initialize session state
init_session()

# Sidebar for page selection
page = st.sidebar.selectbox('Current Page', ['My Policies', 'Claims', 'Billing'])

st.title('PolicyPulse Chat')

# Instantiate LLMClient with Hugging Face API key
llm = LLMClient(api_key=os.getenv('HF_API_KEY'))

# Chat area
st.subheader('Chat')
chat_container = st.container()

conversation = get_conversation()

with chat_container:
    for idx, msg in enumerate(conversation):
        if msg['role'] == 'user':
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**Bot:** {msg['content']}")
            # Parse suggestions from assistant message
            suggestions = []
            if 'You might also ask:' in msg['content']:
                after = msg['content'].split('You might also ask:', 1)[-1]
                # Find up to 3 lines that look like suggestions
                suggestions = [line.strip('- ').strip() for line in after.strip().split('\n') if line.strip()][:3]
            for suggestion in suggestions:
                st.button(suggestion, key=f'suggestion_{idx}_{suggestion}')

# User input area
if 'user_input' not in st.session_state:
    st.session_state.user_input = ''

def on_send():
    user_input = st.session_state.user_input
    if user_input.strip():
        append_message('user', user_input.strip())
        prompt = get_few_shot_prompt(st.session_state.context_page, user_input.strip())
        reply = llm.chat(prompt)
        append_message('assistant', reply)
        st.session_state.user_input = ''  # This is now safe
        st.rerun()

st.text_input('Type your message:', key='user_input', on_change=on_send)

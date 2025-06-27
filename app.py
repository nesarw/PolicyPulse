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

# User input area
if 'user_input' not in st.session_state:
    st.session_state.user_input = ''

def on_send():
    user_input = st.session_state.user_input
    if user_input.strip():
        append_message('user', user_input.strip())
        prompt = get_few_shot_prompt(st.session_state.context_page, user_input.strip())
        reply, rationale = llm.chat(prompt)
        append_message('assistant', reply, rationale=rationale)
        st.session_state.user_input = ''  # This is now safe in the callback

with chat_container:
    for idx, msg in enumerate(conversation):
        if msg['role'] == 'user':
            st.markdown(f"**You:** {msg['content']}")
        else:
            reply = msg['content']  # Always a string
            # Only use up to the next "User:" or "Assistant:" if present
            for tag in ["User:", "Assistant:"]:
                if tag in reply:
                    reply = reply.split(tag, 1)[0].strip()
            # Split out the main answer and suggestions
            main_reply = reply
            suggestions = []
            if 'You might also ask:' in reply:
                main_reply, after = reply.split('You might also ask:', 1)
                suggestions = [line.strip('- ').strip() for line in after.strip().split('\n') if line.strip()][:3]
            else:
                # Fallback: scan for lines that look like questions or start with '-'
                lines = reply.split('\n')
                for line in lines:
                    line_strip = line.strip()
                    if (line_strip.startswith('-') or (line_strip.endswith('?') and len(line_strip) > 8)) and len(suggestions) < 3:
                        suggestions.append(line_strip.strip('- ').strip())

            st.markdown(f"**Bot:** {main_reply.strip()}")

            if suggestions:
                st.markdown("**You might also ask:**")
                for suggestion in suggestions:
                    if st.button(suggestion, key=f'suggestion_{idx}_{suggestion}'):
                        st.session_state.user_input = suggestion
                        on_send()
                        st.rerun()
            if 'rationale' in msg and msg['rationale']:
                st.markdown(f"*🔍 Rationale:* {msg['rationale']}", unsafe_allow_html=True)

st.text_input('Type your message:', key='user_input', on_change=on_send)

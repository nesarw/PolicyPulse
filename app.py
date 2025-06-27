from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from utils.llm_client import LLMClient
from prompts.few_shot_templates import get_few_shot_prompt
from utils.session_store import init_session, append_message, get_conversation
import os
import re
from utils.vector_store import build_index, query_index

# Comprehensive KB – covers health, home, claims, and general policy info
KB_DOCS = [
    # Health insurance facts
    "Health insurance covers medical expenses incurred due to illness, injury, or disease.",
    "We offer individual, family, and group health insurance plans.",
    "Health insurance provides financial protection against unexpected medical emergencies.",
    "You can renew your health insurance policy online through our website or mobile app.",
    "Pre-existing conditions may be covered after a waiting period in health insurance policies.",
    "Cashless hospitalization is available at our network hospitals for health insurance policyholders.",
    "You can add dependents to your health insurance policy during renewal or special enrollment periods.",
    # Home insurance facts
    "Your home insurance deductible is set at ₹10,000.",
    "Home insurance covers damages caused by natural disasters such as earthquakes, floods, and hurricanes.",
    "Your policy covers your home, personal belongings, and liability.",
    "Your policy includes coverage for earthquakes and floods.",
    # Claims and general info
    "You can file a claim via our mobile app under the Claims tab.",
    "To file a claim, provide your policy number, a detailed description, and supporting documents.",
    "Your policy number is 1234567890.",
    "Your policy is valid for one year from the date of issue.",
    "You can pay your premium online through our website or mobile app using various payment methods.",
    "The grace period for premium payment is usually 30 days from the due date.",
    "To cancel your policy, contact our customer service team and provide your policy number and reason for cancellation.",
    "Adding a new driver to your auto policy may affect your premium.",
    "You can add or remove beneficiaries from your life insurance policy at any time.",
    # More general insurance facts
    "Insurance policies help manage financial risks by providing coverage for unexpected events.",
    "Policyholders receive a renewal notice before their policy expires.",
    "You can check your claim status online or by contacting customer service.",
]
faiss_index = build_index(KB_DOCS)

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
        passages = query_index(faiss_index, KB_DOCS, user_input, k=3)
        prompt = get_few_shot_prompt(st.session_state.context_page, user_input.strip(), kb_passages=passages)
        reply, rationale = llm.chat(prompt, kb_passages=passages)
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
            else:
                st.markdown("**You might also ask:**\n_No suggestions available._")
            if 'rationale' in msg and msg['rationale']:
                st.markdown(f"*🔍 Rationale:* {msg['rationale']}", unsafe_allow_html=True)

st.text_input('Type your message:', key='user_input', on_change=on_send)

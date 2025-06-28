from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from utils.llm_client import LLMClient
from utils.memory_manager import MemoryManager
from prompts.few_shot_templates import get_few_shot_prompt
from utils.session_store import init_session, append_message, get_conversation
from utils.pdf_processor import process_uploaded_pdf
from utils.vector_store import build_index, query_index, search_document_chunks
from utils.bfsi_filter import is_bfsi_query
import os
import re

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
    "Home insurance covers damages caused by natural disasters such as earthquakes, floods, and hurricanes.",
    "Your policy covers your home, personal belongings, and liability.",
    "Your policy includes coverage for earthquakes and floods.",
    # Claims and general info
    "You can file a claim via our mobile app under the Claims tab.",
    "To file a claim, provide your policy number, a detailed description, and supporting documents.",
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

# Build the default KB index
faiss_index = build_index(KB_DOCS)

# Initialize session state
init_session()

# Sidebar for page selection
page = st.sidebar.selectbox('Current Page', ['My Policies', 'Claims', 'Billing'])

# Streaming toggle in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Settings")
stream_response = st.sidebar.checkbox("Enable Streaming", value=st.session_state.get('stream_response', False))
st.session_state['stream_response'] = stream_response
if stream_response:
    st.sidebar.info("🔄 Streaming mode enabled - responses will appear token by token")
else:
    st.sidebar.info("📝 Regular mode - responses appear all at once")

st.title('PolicyPulse Chat')

# File upload section
st.subheader('📁 Upload Policy Document')
uploaded_file = st.file_uploader(
    "Upload a PDF policy document to ask questions based on its contents",
    type=['pdf'],
    help="Upload a PDF file to enable document-specific Q&A"
)

# Process uploaded PDF
if uploaded_file is not None:
    if 'doc_chunks' not in st.session_state or 'doc_index' not in st.session_state:
        with st.spinner("Processing uploaded document..."):
            # Process the PDF
            doc_chunks = process_uploaded_pdf(uploaded_file)
            
            if doc_chunks:
                # Build FAISS index for document chunks
                doc_index = build_index(doc_chunks)
                
                # Store in session state
                st.session_state['doc_chunks'] = doc_chunks
                st.session_state['doc_index'] = doc_index
                st.session_state['uploaded_filename'] = uploaded_file.name
                
                st.success(f"✅ Document uploaded successfully! You can now ask questions based on '{uploaded_file.name}'.")
                st.info("📄 Using uploaded document for answer context.")
            else:
                st.error("❌ Failed to process the uploaded document. Please try a different PDF file.")
    
    # Display current document info
    if 'uploaded_filename' in st.session_state:
        st.info(f"📄 Currently using: {st.session_state['uploaded_filename']}")
        if st.button("🗑️ Clear Document"):
            # Clear document-related session state
            for key in ['doc_chunks', 'doc_index', 'uploaded_filename']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

# Instantiate LLMClient with Hugging Face API key
llm = LLMClient(api_key=os.getenv('HF_API_KEY'))

# Initialize memory manager
memory_manager = MemoryManager(llm)

# Chat area
st.subheader('💬 Chat')
chat_container = st.container()

conversation = get_conversation()

# User input area
if 'user_input' not in st.session_state:
    st.session_state.user_input = ''

def on_send():
    user_input = st.session_state.user_input
    if user_input.strip():
        append_message('user', user_input.strip())
        if not is_bfsi_query(user_input):
            refusal_message = (
                "I'm sorry, I can only answer questions related to banking, financial services, and insurance (BFSI). "
                "Please ask a question relevant to these topics."
            )
            append_message('assistant', refusal_message)
            st.session_state.user_input = ''
            return
        doc_chunks = None
        kb_passages = None
        using_document = False
        if ('doc_chunks' in st.session_state and 
            'doc_index' in st.session_state and 
            st.session_state['doc_chunks'] and 
            st.session_state['doc_index']):
            # Heuristic for 'customer name'
            if not doc_chunks and 'customer name' in user_input.lower():
                customer_name_lines = []
                for i, line in enumerate(st.session_state['doc_chunks']):
                    if 'customer name' in line.lower():
                        for j in range(max(0, i-1), min(len(st.session_state['doc_chunks']), i+2)):
                            customer_name_lines.append(st.session_state['doc_chunks'][j])
                customer_name_lines = list(dict.fromkeys(customer_name_lines))[:5]
                if customer_name_lines:
                    doc_chunks = customer_name_lines
                    using_document = True
                    st.info("🔍 Using uploaded document for answer context (customer name match).")
            # Heuristic for 'insured name'
            if not doc_chunks and 'insured name' in user_input.lower():
                insured_name_lines = []
                for i, line in enumerate(st.session_state['doc_chunks']):
                    if 'insured name' in line.lower():
                        for j in range(max(0, i-1), min(len(st.session_state['doc_chunks']), i+2)):
                            insured_name_lines.append(st.session_state['doc_chunks'][j])
                insured_name_lines = list(dict.fromkeys(insured_name_lines))[:5]
                if insured_name_lines:
                    doc_chunks = insured_name_lines
                    using_document = True
                    st.info("🔍 Using uploaded document for answer context (insured name match).")
            # Heuristic for 'policyholder'
            if not doc_chunks and 'policyholder' in user_input.lower():
                policyholder_lines = []
                for i, line in enumerate(st.session_state['doc_chunks']):
                    if 'policyholder' in line.lower():
                        for j in range(max(0, i-1), min(len(st.session_state['doc_chunks']), i+2)):
                            policyholder_lines.append(st.session_state['doc_chunks'][j])
                policyholder_lines = list(dict.fromkeys(policyholder_lines))[:5]
                if policyholder_lines:
                    doc_chunks = policyholder_lines
                    using_document = True
                    st.info("🔍 Using uploaded document for answer context (policyholder match).")
            # Heuristic for 'nominee'
            if not doc_chunks and 'nominee' in user_input.lower():
                nominee_lines = []
                for i, line in enumerate(st.session_state['doc_chunks']):
                    if 'nominee details' in line.lower():
                        # Add the header and up to 5 lines below (table rows)
                        nominee_lines.append(line)
                        for k in range(1, 6):
                            if i + k < len(st.session_state['doc_chunks']):
                                next_line = st.session_state['doc_chunks'][i + k]
                                # Stop if we hit a blank line or a new section
                                if not next_line.strip() or any(x in next_line.lower() for x in ["details", "policy", "coverage", "important", "note:"]):
                                    break
                                nominee_lines.append(next_line)
                    elif 'nominee' in line.lower():
                        for j in range(max(0, i-1), min(len(st.session_state['doc_chunks']), i+2)):
                            nominee_lines.append(st.session_state['doc_chunks'][j])
                nominee_lines = list(dict.fromkeys(nominee_lines))[:7]
                if nominee_lines:
                    doc_chunks = nominee_lines
                    using_document = True
                    st.info("🔍 Using uploaded document for answer context (nominee match).")
            # Heuristic for 'address'
            if not doc_chunks and 'address' in user_input.lower():
                address_lines = []
                for i, line in enumerate(st.session_state['doc_chunks']):
                    if 'address' in line.lower():
                        for j in range(max(0, i-1), min(len(st.session_state['doc_chunks']), i+2)):
                            address_lines.append(st.session_state['doc_chunks'][j])
                address_lines = list(dict.fromkeys(address_lines))[:5]
                if address_lines:
                    doc_chunks = address_lines
                    using_document = True
                    st.info("🔍 Using uploaded document for answer context (address match).")
            # Heuristic for 'mobile' or 'phone'
            if not doc_chunks and any(word in user_input.lower() for word in ['mobile', 'phone']):
                phone_lines = []
                for i, line in enumerate(st.session_state['doc_chunks']):
                    if 'mobile' in line.lower() or 'phone' in line.lower():
                        for j in range(max(0, i-1), min(len(st.session_state['doc_chunks']), i+2)):
                            phone_lines.append(st.session_state['doc_chunks'][j])
                phone_lines = list(dict.fromkeys(phone_lines))[:5]
                if phone_lines:
                    doc_chunks = phone_lines
                    using_document = True
                    st.info("🔍 Using uploaded document for answer context (phone/mobile match).")
            # Heuristic for 'email'
            if not doc_chunks and 'email' in user_input.lower():
                email_lines = []
                for i, line in enumerate(st.session_state['doc_chunks']):
                    if 'email' in line.lower():
                        for j in range(max(0, i-1), min(len(st.session_state['doc_chunks']), i+2)):
                            email_lines.append(st.session_state['doc_chunks'][j])
                email_lines = list(dict.fromkeys(email_lines))[:5]
                if email_lines:
                    doc_chunks = email_lines
                    using_document = True
                    st.info("🔍 Using uploaded document for answer context (email match).")
            # Heuristic for 'gstin'
            if not doc_chunks and 'gstin' in user_input.lower():
                gstin_lines = []
                for i, line in enumerate(st.session_state['doc_chunks']):
                    if 'gstin' in line.lower():
                        for j in range(max(0, i-1), min(len(st.session_state['doc_chunks']), i+2)):
                            gstin_lines.append(st.session_state['doc_chunks'][j])
                gstin_lines = list(dict.fromkeys(gstin_lines))[:5]
                if gstin_lines:
                    doc_chunks = gstin_lines
                    using_document = True
                    st.info("🔍 Using uploaded document for answer context (GSTIN match).")
            # Heuristic for 'plan' or 'product'
            if not doc_chunks and any(word in user_input.lower() for word in ['plan', 'product']):
                plan_lines = []
                for i, line in enumerate(st.session_state['doc_chunks']):
                    if 'plan' in line.lower() or 'product' in line.lower():
                        for j in range(max(0, i-1), min(len(st.session_state['doc_chunks']), i+2)):
                            plan_lines.append(st.session_state['doc_chunks'][j])
                plan_lines = list(dict.fromkeys(plan_lines))[:5]
                if plan_lines:
                    doc_chunks = plan_lines
                    using_document = True
                    st.info("🔍 Using uploaded document for answer context (plan/product match).")
            # Heuristic for 'premium'
            if not doc_chunks and 'premium' in user_input.lower():
                premium_lines = []
                for i, line in enumerate(st.session_state['doc_chunks']):
                    if 'premium' in line.lower():
                        for j in range(max(0, i-1), min(len(st.session_state['doc_chunks']), i+2)):
                            premium_lines.append(st.session_state['doc_chunks'][j])
                premium_lines = list(dict.fromkeys(premium_lines))[:5]
                if premium_lines:
                    doc_chunks = premium_lines
                    using_document = True
                    st.info("🔍 Using uploaded document for answer context (premium match).")
            # Heuristic for 'date of inception'
            if not doc_chunks and 'date of inception' in user_input.lower():
                inception_lines = []
                for i, line in enumerate(st.session_state['doc_chunks']):
                    if 'date of inception' in line.lower():
                        for j in range(max(0, i-1), min(len(st.session_state['doc_chunks']), i+2)):
                            inception_lines.append(st.session_state['doc_chunks'][j])
                inception_lines = list(dict.fromkeys(inception_lines))[:5]
                if inception_lines:
                    doc_chunks = inception_lines
                    using_document = True
                    st.info("🔍 Using uploaded document for answer context (date of inception match).")
            # Heuristic for 'collection number'
            if not doc_chunks and 'collection number' in user_input.lower():
                collection_lines = []
                for i, line in enumerate(st.session_state['doc_chunks']):
                    if 'collection no' in line.lower() or 'collection number' in line.lower():
                        for j in range(max(0, i-1), min(len(st.session_state['doc_chunks']), i+2)):
                            collection_lines.append(st.session_state['doc_chunks'][j])
                collection_lines = list(dict.fromkeys(collection_lines))[:5]
                if collection_lines:
                    doc_chunks = collection_lines
                    using_document = True
                    st.info("🔍 Using uploaded document for answer context (collection number match).")
            # Heuristic for 'collection date'
            if not doc_chunks and 'collection date' in user_input.lower():
                collection_date_lines = []
                for i, line in enumerate(st.session_state['doc_chunks']):
                    if 'collection date' in line.lower():
                        for j in range(max(0, i-1), min(len(st.session_state['doc_chunks']), i+2)):
                            collection_date_lines.append(st.session_state['doc_chunks'][j])
                collection_date_lines = list(dict.fromkeys(collection_date_lines))[:5]
                if collection_date_lines:
                    doc_chunks = collection_date_lines
                    using_document = True
                    st.info("🔍 Using uploaded document for answer context (collection date match).")
            # Heuristic for 'policy category'
            if not doc_chunks and 'policy category' in user_input.lower():
                policy_category_lines = []
                for i, line in enumerate(st.session_state['doc_chunks']):
                    if 'policy category' in line.lower():
                        for j in range(max(0, i-1), min(len(st.session_state['doc_chunks']), i+2)):
                            policy_category_lines.append(st.session_state['doc_chunks'][j])
                policy_category_lines = list(dict.fromkeys(policy_category_lines))[:5]
                if policy_category_lines:
                    doc_chunks = policy_category_lines
                    using_document = True
                    st.info("🔍 Using uploaded document for answer context (policy category match).")
            # Heuristic for 'insured' questions
            if any(word in user_input.lower() for word in ["insured", "insured name", "who is insured", "who is the insured"]):
                insured_lines = []
                for i, line in enumerate(st.session_state['doc_chunks']):
                    if "insured" in line.lower() or "name" in line.lower():
                        for j in range(max(0, i-1), min(len(st.session_state['doc_chunks']), i+2)):
                            insured_lines.append(st.session_state['doc_chunks'][j])
                insured_lines = list(dict.fromkeys(insured_lines))[:5]
                if insured_lines:
                    doc_chunks = insured_lines
                    using_document = True
                    st.info("🔍 Using uploaded document for answer context (insured match).")
            # Heuristic for 'policy number'
            if not doc_chunks and 'policy number' in user_input.lower():
                policy_lines = []
                for i, line in enumerate(st.session_state['doc_chunks']):
                    if 'policy no' in line.lower():
                        for j in range(max(0, i-1), min(len(st.session_state['doc_chunks']), i+2)):
                            policy_lines.append(st.session_state['doc_chunks'][j])
                policy_lines = list(dict.fromkeys(policy_lines))[:5]
                if policy_lines:
                    doc_chunks = policy_lines
                    using_document = True
                    st.info("🔍 Using uploaded document for answer context (policy number match).")
            # Improved heuristic for 'sum insured'/'sum assured' (2 lines before and after)
            if not doc_chunks and any(word in user_input.lower() for word in ["sum insured", "sum assured"]):
                sum_lines = []
                for i, line in enumerate(st.session_state['doc_chunks']):
                    if re.search(r"sum[\s_-]*insured|sum[\s_-]*assured", line, re.IGNORECASE):
                        for j in range(max(0, i-2), min(len(st.session_state['doc_chunks']), i+3)):
                            sum_lines.append(st.session_state['doc_chunks'][j])
                sum_lines = list(dict.fromkeys(sum_lines))[:7]
                if sum_lines:
                    doc_chunks = sum_lines
                    using_document = True
                    st.info("🔍 Using uploaded document for answer context (sum insured match).")
            # Heuristic for 'customer code'
            if not doc_chunks and 'customer code' in user_input.lower():
                customer_lines = []
                for i, line in enumerate(st.session_state['doc_chunks']):
                    if 'customer code' in line.lower():
                        for j in range(max(0, i-1), min(len(st.session_state['doc_chunks']), i+2)):
                            customer_lines.append(st.session_state['doc_chunks'][j])
                customer_lines = list(dict.fromkeys(customer_lines))[:5]
                if customer_lines:
                    doc_chunks = customer_lines
                    using_document = True
                    st.info("🔍 Using uploaded document for answer context (customer code match).")
            # Heuristic for 'proposer'
            if not doc_chunks and 'proposer' in user_input.lower():
                proposer_lines = []
                for i, line in enumerate(st.session_state['doc_chunks']):
                    if 'proposer' in line.lower():
                        for j in range(max(0, i-1), min(len(st.session_state['doc_chunks']), i+2)):
                            proposer_lines.append(st.session_state['doc_chunks'][j])
                proposer_lines = list(dict.fromkeys(proposer_lines))[:5]
                if proposer_lines:
                    doc_chunks = proposer_lines
                    using_document = True
                    st.info("🔍 Using uploaded document for answer context (proposer match).")
            if not doc_chunks:
                try:
                    relevant_chunks, has_relevant_chunks = search_document_chunks(
                        st.session_state['doc_index'],
                        st.session_state['doc_chunks'],
                        user_input,
                        k=3,
                        similarity_threshold=0.1
                    )
                    if has_relevant_chunks:
                        doc_chunks = relevant_chunks
                        using_document = True
                        st.info("🔍 Using uploaded document for answer context.")
                    else:
                        st.warning("⚠️ No relevant information found in uploaded document. Using general knowledge base.")
                        passages = query_index(faiss_index, KB_DOCS, user_input, k=3)
                        kb_passages = passages
                except Exception as e:
                    st.error(f"Error searching document: {str(e)}")
                    passages = query_index(faiss_index, KB_DOCS, user_input, k=3)
                    kb_passages = passages
        else:
            passages = query_index(faiss_index, KB_DOCS, user_input, k=3)
            kb_passages = passages
        base_prompt = get_few_shot_prompt(
            st.session_state.context_page, 
            user_input.strip(), 
            kb_passages=kb_passages,
            doc_chunks=doc_chunks
        )
        
        # Add memory context to the prompt by modifying the system message
        memory_ctx = memory_manager.get_memory_context()
        if memory_ctx:
            # Insert memory context prominently at the beginning of the system message
            if "You are a helpful assistant" in base_prompt:
                # Split at the system message start and insert memory before it
                parts = base_prompt.split("You are a helpful assistant", 1)
                full_prompt = f"{parts[0]}### CONVERSATION MEMORY (Use this information for consistency):\n{memory_ctx}\n\nYou are a helpful assistant{parts[1]}"
            else:
                # Fallback: prepend memory context
                full_prompt = f"### CONVERSATION MEMORY (Use this information for consistency):\n{memory_ctx}\n\n{base_prompt}"
        else:
            full_prompt = base_prompt
        
        # Streaming support
        stream_response = False
        if 'stream_response' in st.session_state:
            stream_response = st.session_state['stream_response']
        elif 'stream_response' in globals():
            stream_response = globals()['stream_response']
        # You can also add config-based check here if you have a config dict

        if stream_response:
            # Only accumulate the streamed reply here, do not render
            reply_accum = ""
            for token in llm.stream_chat_response(full_prompt):
                reply_accum += token
            reply = reply_accum
            rationale = None
        else:
            reply, rationale = llm.chat(full_prompt, kb_passages=kb_passages)
        
        # Add this conversation turn to memory
        memory_manager.add_turn(user_input.strip(), reply)
        
        append_message('assistant', reply, rationale=rationale)
        st.session_state.user_input = ''

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

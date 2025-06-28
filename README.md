# PolicyPulse

[![Streamlit Cloud](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/) <!-- TODO: Replace with your app's Streamlit Cloud URL -->

## Overview

PolicyPulse is an interactive Streamlit application designed to help users analyze, discuss, and visualize policy documents and related data. With a conversational interface and context-aware features, PolicyPulse aims to make policy analysis more accessible and engaging for everyone.

## 🆕 New Features: Document-Constrained RAG

PolicyPulse now supports **document-constrained Retrieval-Augmented Generation (RAG)** that allows users to:

- 📁 **Upload PDF policy documents** and ask questions based on their specific contents
- 🧠 **Dynamic vector search** using FAISS and SentenceTransformers
- 💬 **Context-aware responses** that reference the uploaded document
- 🛡️ **Intelligent fallback** to general BFSI knowledge base when document content isn't relevant
- 📊 **Similarity threshold filtering** to ensure only relevant document chunks are used

### How It Works

1. **Upload a PDF**: Users can upload any PDF policy document using the file uploader
2. **Automatic Processing**: The system extracts text, chunks it into overlapping segments, and builds a FAISS vector index
3. **Smart Retrieval**: When users ask questions, the system searches the document chunks for relevant information
4. **Context Injection**: Relevant document chunks are injected into the LLM prompt as context
5. **Fallback Protection**: If no relevant document content is found, the system falls back to the general BFSI knowledge base

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nesarw/PolicyPulse.git
   cd PolicyPulse
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   ```

3. **Activate the virtual environment:**
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running Locally

You can use the provided script to set up and launch the app:

```bash
./run.sh
```

Or, run manually:

```bash
streamlit run app.py
```

## Streamlit Cloud

[![Open in Streamlit Cloud](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)  
*Replace this link with your deployed app's Streamlit Cloud URL.*

## BFSI Domain Restriction

PolicyPulse is strictly limited to answering questions related to the Banking, Financial Services, and Insurance (BFSI) sector. Any questions outside this domain (e.g., programming, sports, general trivia) will be politely refused by the assistant.

This is enforced by a BFSI domain filter utility (`utils/bfsi_filter.py`) that checks user queries for BFSI relevance before generating a response. You can customize the list of keywords in that file to broaden or narrow the domain as needed.

## Features

### Core Features
- 💬 **Conversational interface** for BFSI policy and insurance queries
- 🛡️ **Strict domain filtering** - refuses to answer out-of-domain questions
- 🧠 **Context-aware answers** with related suggestions
- 🔄 **Easy extensibility** for BFSI topics

### Document RAG Features
- 📁 **PDF Upload**: Accepts PDF policy documents for analysis
- 🔍 **Text Extraction**: Uses pdfplumber for reliable text extraction
- ✂️ **Smart Chunking**: Splits text into overlapping chunks (400 chars, 200 char overlap)
- 🧠 **Vector Search**: FAISS index with SentenceTransformer embeddings
- 🎯 **Similarity Filtering**: Only uses chunks above similarity threshold (0.3)
- 🔄 **Intelligent Fallback**: Falls back to general KB when document content isn't relevant
- 📊 **Real-time Processing**: Processes documents on upload, stores in session state

## Technical Architecture

### Document Processing Pipeline
1. **PDF Upload** → `st.file_uploader` with PDF validation
2. **Text Extraction** → `pdfplumber` for reliable text extraction
3. **Chunking** → Smart text splitting with sentence boundary preservation
4. **Embedding** → SentenceTransformer (`all-MiniLM-L6-v2`) for vectorization
5. **Indexing** → FAISS IndexFlatL2 for fast similarity search
6. **Retrieval** → Similarity search with threshold filtering
7. **Context Injection** → Document chunks injected into LLM prompt

### Key Components
- `utils/pdf_processor.py` - PDF text extraction and chunking
- `utils/vector_store.py` - FAISS indexing and similarity search
- `prompts/few_shot_templates.py` - Enhanced prompts with document context
- `app.py` - Main application with document upload and RAG pipeline

## Dependencies

The application requires the following key dependencies:
- `streamlit` - Web application framework
- `pdfplumber` - PDF text extraction
- `faiss-cpu` - Vector similarity search
- `sentence-transformers` - Text embeddings
- `openai` - LLM integration
- `python-dotenv` - Environment variable management

## Usage Examples

### Document-Based Q&A
1. Upload a PDF policy document
2. Ask questions like:
   - "What is the policy number?"
   - "What are the coverage limits?"
   - "How do I file a claim according to this policy?"
   - "What is the deductible amount?"

### General BFSI Q&A
- "How do I update my address on my policy?"
- "What documents are needed to file a claim?"
- "Can I pay my premium online?"
- "What is the grace period for premium payment?"
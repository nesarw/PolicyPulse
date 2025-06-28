# PolicyPulse

[![Streamlit Cloud](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)

## Overview

PolicyPulse is an advanced Streamlit GenAI app for **document-grounded Q&A** on insurance policy PDFs. It uses Retrieval-Augmented Generation (RAG) with robust heuristics and LLMs (Groq Llama-4, HuggingFace, or fallback) to answer user questions based strictly on the uploaded document.

## Key Features (2024)

- 📁 **PDF Upload**: Upload any insurance policy PDF and ask questions about its contents.
- 🧠 **Dynamic RAG**: In-memory FAISS vector search with SentenceTransformer embeddings.
- 🗂️ **Advanced Heuristics**: Extracts fields like policy number, sum insured, nominee, customer name, address, GSTIN, premium, plan, proposer, and more—even from tables.
- 💬 **LLM Integration**: Uses Groq's Meta-Llama-4-Scout-17B-16E-Instruct (via OpenAI v1+ API) as primary, with HuggingFace fallback.
- 🛡️ **BFSI Domain Restriction**: Only answers banking, financial services, and insurance questions.
- 🔄 **Fallback Logic**: If document search fails, falls back to a general BFSI knowledge base.
- 📝 **Prompt Engineering**: Prompts instruct the LLM to extract and present table fields in a structured way.
- 🧪 **Session State**: Uploaded document and index persist for the session.

## Advanced Field Extraction

- **Heuristics for all major fields**: policy number, sum insured, customer name, insured name, policyholder, nominee (with table extraction), address, mobile/phone, email, GSTIN, plan/product, premium, date of inception, collection number/date, policy category, proposer, and more.
- **Table Extraction**: For fields like nominee, the app extracts the header and table rows for structured answers.
- **Prompt Examples**: Few-shot prompt includes structured nominee extraction for LLM guidance.

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

```bash
streamlit run app.py
```

## Environment Variables

- `GROQ_API_KEY` — for Groq Llama-4 (recommended primary LLM)
- `HF_API_KEY` — for HuggingFace fallback

Add these to your `.env` file:
```
GROQ_API_KEY=your-groq-key
HF_API_KEY=your-huggingface-key
```

## Usage Examples

- "What is the policy number?"
- "Who is the nominee?"
- "What is the sum insured?"
- "What is the GSTIN?"
- "What is the premium?"
- "Who is the proposer?"
- "What is the collection date?"
- "What is the policy category?"
- "What is the address?"
- "What is the mobile number?"
- "What is the email address?"

## Technical Architecture

- **Document Upload**: `st.file_uploader` for PDF
- **Text Extraction**: `pdfplumber` (line-based chunking)
- **Vector Search**: FAISS + SentenceTransformer
- **Heuristic Extraction**: Regex and windowed line search for all major fields
- **LLM Prompting**: Context injected as numbered lines, with explicit instructions for table extraction
- **LLM Client**: Groq (OpenAI v1+ API) primary, HuggingFace fallback
- **Session State**: Document and index persist for the session

## Dependencies

- `streamlit`
- `openai>=1.0.0`
- `requests`
- `pdfplumber`
- `faiss-cpu`
- `sentence-transformers`
- `python-dotenv`

## Project Status

- **Latest LLM support**: Groq Llama-4-Scout-17B-16E-Instruct (OpenAI v1+), HuggingFace fallback
- **Robust document heuristics**: All major insurance fields, including table extraction
- **Modern prompt engineering**: Structured, context-rich, and few-shot guided
- **Ready for production BFSI document Q&A**
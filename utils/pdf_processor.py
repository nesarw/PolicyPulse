import pdfplumber
import re
from typing import List, Optional
import streamlit as st


def extract_text_from_pdf(pdf_file) -> Optional[str]:
    """
    Extract raw text from uploaded PDF file using pdfplumber.
    Returns None if extraction fails.
    """
    try:
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return None


def split_text_by_lines(text: str) -> List[str]:
    """
    Split text into non-empty lines for line-based chunking.
    """
    return [line.strip() for line in text.splitlines() if line.strip()]


def process_uploaded_pdf(pdf_file) -> Optional[List[str]]:
    """
    Process uploaded PDF file: extract text and split into chunks.
    Returns list of text chunks or None if processing fails.
    """
    # Extract text from PDF
    text = extract_text_from_pdf(pdf_file)
    if not text:
        return None
    
    # Use line-based chunking for better LLM extraction
    chunks = split_text_by_lines(text)
    
    if not chunks:
        st.error("No text content found in the uploaded PDF.")
        return None
    
    return chunks 
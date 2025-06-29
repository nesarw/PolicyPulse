from typing import List, Tuple
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np


def build_index(documents: List[str]) -> faiss.IndexFlatL2:
    """
    Embeds each document with SentenceTransformer('all-MiniLM-L6-v2'),
    creates a FAISS IndexFlatL2, and adds the embeddings.
    """
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(documents, convert_to_numpy=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index


def query_index(index: faiss.IndexFlatL2, docs: List[str], query: str, k: int = 3) -> List[str]:
    """
    Embeds the query, searches the index for the top-k nearest docs,
    and returns the matching document texts.
    """
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode([query], convert_to_numpy=True)
    D, I = index.search(query_embedding, k)
    return [docs[i] for i in I[0]]


def search_document_chunks(index: faiss.IndexFlatL2, doc_chunks: List[str], query: str, 
                          k: int = 3, similarity_threshold: float = 0.3) -> Tuple[List[str], bool]:
    """
    Search document chunks with similarity threshold checking.
    
    Args:
        index: FAISS index of document chunks
        doc_chunks: List of document chunks
        query: User query
        k: Number of top results to retrieve
        similarity_threshold: Minimum similarity score (lower distance = higher similarity)
    
    Returns:
        Tuple of (relevant_chunks, has_relevant_chunks)
    """
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode([query], convert_to_numpy=True)
    
    # Search for top k results
    distances, indices = index.search(query_embedding, k)
    
    # Filter results based on similarity threshold
    relevant_chunks = []
    for i, distance in enumerate(distances[0]):
        # Convert distance to similarity score (lower distance = higher similarity)
        # Using a simple conversion: similarity = 1 / (1 + distance)
        similarity = 1 / (1 + distance)
        
        if similarity >= similarity_threshold:
            chunk_idx = indices[0][i]
            if chunk_idx < len(doc_chunks):
                relevant_chunks.append(doc_chunks[chunk_idx])
    
    has_relevant_chunks = len(relevant_chunks) > 0
    return relevant_chunks, has_relevant_chunks

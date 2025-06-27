from typing import List
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

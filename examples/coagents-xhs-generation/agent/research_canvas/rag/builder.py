"""
RAG provider builder for creating appropriate retriever instances.
"""
import os
from typing import Optional
from .retriever import Retriever
from .ragflow_provider import RAGFlowProvider


def build_retriever() -> Optional[Retriever]:
    """Build and return a retriever instance based on environment configuration."""
    rag_provider = os.getenv("RAG_PROVIDER", "").lower()
    
    if rag_provider == "ragflow":
        try:
            return RAGFlowProvider()
        except ValueError as e:
            print(f"Failed to initialize RAGFlow provider: {e}")
            return None
    elif rag_provider:
        print(f"Unsupported RAG provider: {rag_provider}")
        return None
    else:
        print("No RAG provider configured")
        return None
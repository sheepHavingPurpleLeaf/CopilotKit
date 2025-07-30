"""
Abstract base classes for RAG retrieval functionality.
"""
import abc
from typing import List, Optional
from pydantic import BaseModel


class Chunk:
    """Represents a chunk of content with similarity score."""
    
    def __init__(self, content: str, similarity: float):
        self.content = content
        self.similarity = similarity


class Document:
    """Represents a document with multiple chunks."""
    
    def __init__(
        self,
        id: str,
        url: Optional[str] = None,
        title: Optional[str] = None,
        chunks: List[Chunk] = None,
    ):
        self.id = id
        self.url = url
        self.title = title
        self.chunks = chunks or []

    def to_dict(self) -> dict:
        """Convert document to dictionary format."""
        d = {
            "id": self.id,
            "content": "\n\n".join([chunk.content for chunk in self.chunks]),
        }
        if self.url:
            d["url"] = self.url
        if self.title:
            d["title"] = self.title
        return d


class Resource(BaseModel):
    """Represents a resource in the knowledge base."""
    
    uri: str
    title: str
    description: str


class Retriever(abc.ABC):
    """Abstract base class for document retrievers."""
    
    @abc.abstractmethod
    def query_relevant_documents(
        self, query: str, resources: List[Resource] = None
    ) -> List[Document]:
        """Query relevant documents from the knowledge base."""
        pass

    @abc.abstractmethod
    def list_resources(self, query: Optional[str] = None) -> List[Resource]:
        """List available resources in the knowledge base."""
        pass
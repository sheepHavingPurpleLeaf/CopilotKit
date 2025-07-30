"""
RAGFlow provider implementation for document retrieval.
"""
import os
import requests
from typing import List, Optional
from urllib.parse import urlparse
from .retriever import Chunk, Document, Resource, Retriever


class RAGFlowProvider(Retriever):
    """RAGFlow provider for document retrieval."""

    def __init__(self):
        """Initialize RAGFlow provider with API credentials."""
        api_url = os.getenv("RAGFLOW_API_URL")
        if not api_url:
            raise ValueError("RAGFLOW_API_URL environment variable is not set")
        self.api_url = api_url

        api_key = os.getenv("RAGFLOW_API_KEY")
        if not api_key:
            raise ValueError("RAGFLOW_API_KEY environment variable is not set")
        self.api_key = api_key

        # Page size for retrieval results
        page_size = os.getenv("RAGFLOW_PAGE_SIZE", "10")
        self.page_size = int(page_size)

    def query_relevant_documents(
        self, query: str, resources: List[Resource] = None
    ) -> List[Document]:
        """Query relevant documents from RAGFlow."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Extract dataset and document IDs from resources
        dataset_ids: List[str] = []
        document_ids: List[str] = []

        if resources:
            for resource in resources:
                dataset_id, document_id = self._parse_uri(resource.uri)
                if dataset_id:
                    dataset_ids.append(dataset_id)
                if document_id:
                    document_ids.append(document_id)

        payload = {
            "question": query,
            "dataset_ids": dataset_ids,
            "document_ids": document_ids,
            "page_size": self.page_size,
        }

        try:
            response = requests.post(
                f"{self.api_url}/api/v1/retrieval", 
                headers=headers, 
                json=payload,
                timeout=30
            )

            if response.status_code != 200:
                raise Exception(f"RAGFlow API error: {response.status_code} - {response.text}")

            result = response.json()
            data = result.get("data", {})
            
            # Process document aggregations
            doc_aggs = data.get("doc_aggs", [])
            docs = {
                doc.get("doc_id"): Document(
                    id=doc.get("doc_id"),
                    title=doc.get("doc_name"),
                    chunks=[],
                )
                for doc in doc_aggs
            }

            # Process chunks and associate with documents
            for chunk in data.get("chunks", []):
                doc_id = chunk.get("document_id")
                if doc_id in docs:
                    docs[doc_id].chunks.append(
                        Chunk(
                            content=chunk.get("content", ""),
                            similarity=chunk.get("similarity", 0.0),
                        )
                    )

            return list(docs.values())

        except requests.RequestException as e:
            raise Exception(f"Failed to connect to RAGFlow: {str(e)}")
        except Exception as e:
            raise Exception(f"RAGFlow query failed: {str(e)}")

    def list_resources(self, query: Optional[str] = None) -> List[Resource]:
        """List available datasets in RAGFlow."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        params = {}
        if query:
            params["name"] = query

        try:
            response = requests.get(
                f"{self.api_url}/api/v1/datasets", 
                headers=headers, 
                params=params,
                timeout=30
            )

            if response.status_code != 200:
                raise Exception(f"RAGFlow API error: {response.status_code} - {response.text}")

            result = response.json()
            resources = []

            for item in result.get("data", []):
                resource = Resource(
                    uri=f"rag://dataset/{item.get('id')}",
                    title=item.get("name", ""),
                    description=item.get("description", ""),
                )
                resources.append(resource)

            return resources

        except requests.RequestException as e:
            raise Exception(f"Failed to connect to RAGFlow: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to list RAGFlow resources: {str(e)}")

    def _parse_uri(self, uri: str) -> tuple[str, str]:
        """Parse RAG URI to extract dataset and document IDs."""
        try:
            parsed = urlparse(uri)
            if parsed.scheme != "rag":
                raise ValueError(f"Invalid RAG URI scheme: {uri}")
            
            # For rag://dataset/id format, dataset is in netloc and id is in path
            if parsed.netloc == "dataset":
                path_parts = parsed.path.split("/")
                if len(path_parts) < 2 or not path_parts[1]:
                    raise ValueError(f"Invalid RAG URI format: {uri}")
                dataset_id = path_parts[1]
                document_id = parsed.fragment if parsed.fragment else ""
                return dataset_id, document_id
            
            # Fallback: try parsing as rag:///dataset/id format
            path_parts = parsed.path.split("/")
            if len(path_parts) >= 3 and path_parts[1] == "dataset":
                dataset_id = path_parts[2]
                document_id = parsed.fragment if parsed.fragment else ""
                return dataset_id, document_id
            
            raise ValueError(f"Invalid RAG URI format: {uri}")
            
        except Exception as e:
            raise ValueError(f"Failed to parse URI {uri}: {str(e)}")
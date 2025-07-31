"""
Base RAG Server Interface.

This module defines the base interface for all RAG (Retrieval-Augmented Generation) servers
in the Business License Navigator system.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .search_result import SearchResult


@dataclass
class RAGConfig:
    """Configuration for RAG servers."""
    collection_name: str
    embedding_model: str = "all-MiniLM-L6-v2"
    vector_size: int = 384
    top_k: int = 5
    similarity_threshold: float = 0.7


class BaseRAGServer(ABC):
    """
    Base interface for RAG servers.
    
    All RAG servers must implement these methods to provide consistent
    retrieval-augmented generation capabilities.
    """
    
    def __init__(self, config: RAGConfig):
        """Initialize the RAG server with configuration."""
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.embedding_model = None
        self.qdrant_client = None
        
        self._setup_embedding_model()
        self._setup_qdrant()
        self._load_data()
    
    @abstractmethod
    def _setup_embedding_model(self) -> None:
        """Setup the embedding model for text vectorization."""
        pass
    
    @abstractmethod
    def _setup_qdrant(self) -> None:
        """Setup the Qdrant vector database connection."""
        pass
    
    @abstractmethod
    def _load_data(self) -> None:
        """Load and index the data into the vector database."""
        pass
    
    @abstractmethod
    async def search_licenses(self, query: str, top_k: int = None) -> SearchResult:
        """
        Search for licenses using RAG.
        
        Args:
            query: The search query
            top_k: Number of results to return
            
        Returns:
            SearchResult containing relevant license information
        """
        pass
    
    @abstractmethod
    async def get_business_steps(self) -> SearchResult:
        """
        Get business setup steps.
        
        Returns:
            SearchResult containing business setup steps
        """
        pass
    
    @abstractmethod
    async def get_license_categories(self) -> SearchResult:
        """
        Get available license categories.
        
        Returns:
            SearchResult containing license categories
        """
        pass
    
    @abstractmethod
    async def get_similar_licenses(self, license_type: str, top_k: int = None) -> SearchResult:
        """
        Find similar licenses to the given type.
        
        Args:
            license_type: The license type to find similar licenses for
            top_k: Number of results to return
            
        Returns:
            SearchResult containing similar licenses
        """
        pass
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information and status."""
        return {
            "server_type": self.__class__.__name__,
            "embedding_model": self.config.embedding_model,
            "collection_name": self.config.collection_name,
            "vector_size": self.config.vector_size,
            "qdrant_connected": self.qdrant_client is not None,
            "embedding_model_loaded": self.embedding_model is not None
        } 
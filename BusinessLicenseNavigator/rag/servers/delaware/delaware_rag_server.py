"""
Delaware RAG Server.

This module provides RAG capabilities for Delaware business license information.
"""

import asyncio
import logging
import os
import sys
from typing import List, Dict, Any, Optional

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from core.models.base_rag_server import BaseRAGServer, RAGConfig
from core.models.search_result import SearchResult

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    print("Warning: Qdrant client not available. Install with: pip install qdrant-client")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: Sentence transformers not available. Install with: pip install sentence-transformers")


class DelawareRAGServer(BaseRAGServer):
    """RAG server for Delaware business license information."""
    
    def __init__(self, config: RAGConfig, **kwargs):
        """Initialize the Delaware RAG server."""
        super().__init__(config)
        self.state_config = kwargs.get('state_config', {})
        self._load_delaware_data()
    
    def _setup_embedding_model(self) -> None:
        """Setup the embedding model for text vectorization."""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            self.logger.warning("Sentence transformers not available, using fallback")
            return
        
        try:
            self.logger.info("Loading embedding model...")
            self.embedding_model = SentenceTransformer(self.config.embedding_model)
            self.logger.info("Embedding model loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading embedding model: {e}")
            self.embedding_model = None
    
    def _setup_qdrant(self) -> None:
        """Setup the Qdrant vector database connection."""
        if not QDRANT_AVAILABLE:
            self.logger.warning("Qdrant client not available, using fallback")
            return
        
        try:
            self.logger.info("Initializing Qdrant vector database...")
            self.qdrant_client = QdrantClient("localhost", port=6333)
            self.logger.info("Connected to Qdrant server")
            
            # Create collection if it doesn't exist
            try:
                self.qdrant_client.get_collection(self.config.collection_name)
                self.logger.info(f"Collection {self.config.collection_name} already exists")
            except Exception:
                self.qdrant_client.create_collection(
                    collection_name=self.config.collection_name,
                    vectors_config=VectorParams(size=self.config.vector_size, distance=Distance.COSINE)
                )
                self.logger.info(f"Created collection {self.config.collection_name}")
                
        except Exception as e:
            self.logger.error(f"Error setting up Qdrant collection: {e}")
            self.qdrant_client = None
    
    def _load_delaware_data(self) -> None:
        """Load Delaware-specific business license data."""
        self.delaware_data = [
            {
                "text": "Delaware Business First Steps - 4-Step Process\n\nStep 1: Harness Your Great Idea\n   Develop and refine your business concept\n\nStep 2: Write Your Business Plan\n   Create a comprehensive business plan\n\nStep 3: Choose Your Business Structure\n   Select appropriate legal structure\n\nStep 4: Register Your Business\n   Complete state registration requirements",
                "metadata": {"type": "business_steps", "source": "https://firststeps.delaware.gov"}
            },
            {
                "text": "Delaware License Categories\n\nAvailable Categories:\n1. Concentrated Animal Feeding Operation (CAFO) Permit\n2. Deer Depredation Permits\n3. Meat, Poultry, and Egg Products\n4. Food Establishments\n5. Professional Counselors of Mental Health\n6. Home Health Agencies\n7. Health\n8. Environmental Protection\n9. Well Contractors (Drillers)\n10. Accident and Health Insurance",
                "metadata": {"type": "license_categories", "source": "https://firststeps.delaware.gov/topics/"}
            },
            {
                "text": "Food Establishments License\n\nRequired for: restaurants, food trucks, bakeries, diners, caterers, frozen dessert stands, butchers, food delivery services\n\nRequirements:\n- Food safety training certification\n- Health inspection approval\n- Kitchen facility compliance\n- Employee training records\n\nCost: $100-300 application fee\nDue Date: Apply 45 days before opening\nRenewal: Annual renewal required",
                "metadata": {"type": "license_details", "category": "food", "source": "https://firststeps.delaware.gov/topics/"}
            },
            {
                "text": "Construction Contractor License\n\nRequired for: general contractors, building contractors, specialty contractors\n\nRequirements:\n- Experience verification (2-5 years)\n- Background check\n- Financial responsibility proof\n- Insurance coverage\n\nCost: $200-500 application fee\nDue Date: Apply 60 days before starting work\nRenewal: Annual renewal required",
                "metadata": {"type": "license_details", "category": "construction", "source": "https://firststeps.delaware.gov/topics/"}
            },
            {
                "text": "Cannabis Business License\n\nRequired for: dispensaries, cultivation facilities, processing facilities\n\nRequirements:\n- Background check (all owners/employees)\n- Financial responsibility proof\n- Security plan approval\n- Location compliance\n\nCost: $5,000-25,000 application fee\nDue Date: Apply 120 days before planned opening\nRenewal: Annual renewal required",
                "metadata": {"type": "license_details", "category": "cannabis", "source": "https://firststeps.delaware.gov/topics/"}
            }
        ]
        
        if self.qdrant_client and self.embedding_model:
            self._index_delaware_data()
    
    def _index_delaware_data(self) -> None:
        """Index Delaware data into Qdrant."""
        try:
            points = []
            for i, item in enumerate(self.delaware_data):
                # Generate embedding
                embedding = self.embedding_model.encode(item["text"]).tolist()
                
                # Create point
                point = PointStruct(
                    id=i,
                    vector=embedding,
                    payload={
                        "text": item["text"],
                        "metadata": item["metadata"]
                    }
                )
                points.append(point)
            
            # Insert points into collection
            self.qdrant_client.upsert(
                collection_name=self.config.collection_name,
                points=points
            )
            self.logger.info(f"Indexed {len(points)} Delaware license items")
            
        except Exception as e:
            self.logger.error(f"Error indexing Delaware data: {e}")
    
    async def search_licenses(self, query: str, top_k: int = None) -> SearchResult:
        """Search for Delaware licenses using RAG."""
        top_k = top_k or self.config.top_k
        
        if not self.qdrant_client or not self.embedding_model:
            # Fallback to keyword search
            return self._fallback_search(query)
        
        try:
            self.logger.info(f"Performing RAG search with Qdrant for: {query}")
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in Qdrant
            search_result = self.qdrant_client.search(
                collection_name=self.config.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=self.config.similarity_threshold
            )
            
            if search_result:
                content = []
                for result in search_result:
                    content.append({
                        "text": result.payload.get("text", ""),
                        "score": result.score,
                        "metadata": result.payload.get("metadata", {})
                    })
                
                return SearchResult(
                    content=content,
                    metadata={"query": query, "top_k": top_k},
                    score=search_result[0].score if search_result else None,
                    source="Delaware RAG Server"
                )
            else:
                return self._fallback_search(query)
                
        except Exception as e:
            self.logger.error(f"Error in RAG search: {e}")
            return self._fallback_search(query)
    
    def _fallback_search(self, query: str) -> SearchResult:
        """Fallback search when Qdrant is not available."""
        query_lower = query.lower()
        matching_items = []
        
        for item in self.delaware_data:
            if query_lower in item["text"].lower():
                matching_items.append({
                    "text": item["text"],
                    "score": 1.0,
                    "metadata": item["metadata"]
                })
        
        return SearchResult(
            content=matching_items,
            metadata={"query": query, "method": "fallback"},
            source="Delaware RAG Server (Fallback)"
        )
    
    async def get_business_steps(self) -> SearchResult:
        """Get Delaware business setup steps."""
        business_steps = next(
            (item for item in self.delaware_data if item["metadata"]["type"] == "business_steps"),
            None
        )
        
        if business_steps:
            return SearchResult(
                content=[{"text": business_steps["text"]}],
                metadata={"type": "business_steps"},
                source="Delaware RAG Server"
            )
        else:
            return SearchResult(
                content=[{"text": "Delaware business steps not available"}],
                metadata={"type": "business_steps"},
                source="Delaware RAG Server"
            )
    
    async def get_license_categories(self) -> SearchResult:
        """Get Delaware license categories."""
        categories = next(
            (item for item in self.delaware_data if item["metadata"]["type"] == "license_categories"),
            None
        )
        
        if categories:
            return SearchResult(
                content=[{"text": categories["text"]}],
                metadata={"type": "license_categories"},
                source="Delaware RAG Server"
            )
        else:
            return SearchResult(
                content=[{"text": "Delaware license categories not available"}],
                metadata={"type": "license_categories"},
                source="Delaware RAG Server"
            )
    
    async def get_similar_licenses(self, license_type: str, top_k: int = None) -> SearchResult:
        """Find similar licenses to the given type."""
        top_k = top_k or self.config.top_k
        
        if not self.qdrant_client or not self.embedding_model:
            return self._fallback_similar_search(license_type)
        
        try:
            self.logger.info(f"Finding similar licenses with Qdrant for: {license_type}")
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(license_type).tolist()
            
            # Search in Qdrant
            search_result = self.qdrant_client.search(
                collection_name=self.config.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=self.config.similarity_threshold
            )
            
            if search_result:
                content = []
                for result in search_result:
                    content.append({
                        "text": result.payload.get("text", ""),
                        "score": result.score,
                        "metadata": result.payload.get("metadata", {})
                    })
                
                return SearchResult(
                    content=content,
                    metadata={"license_type": license_type, "top_k": top_k},
                    score=search_result[0].score if search_result else None,
                    source="Delaware RAG Server"
                )
            else:
                return self._fallback_similar_search(license_type)
                
        except Exception as e:
            self.logger.error(f"Error finding similar licenses: {e}")
            return self._fallback_similar_search(license_type)
    
    def _fallback_similar_search(self, license_type: str) -> SearchResult:
        """Fallback similar search when Qdrant is not available."""
        license_type_lower = license_type.lower()
        matching_items = []
        
        for item in self.delaware_data:
            if license_type_lower in item["text"].lower():
                matching_items.append({
                    "text": item["text"],
                    "score": 1.0,
                    "metadata": item["metadata"]
                })
        
        return SearchResult(
            content=matching_items,
            metadata={"license_type": license_type, "method": "fallback"},
            source="Delaware RAG Server (Fallback)"
        ) 
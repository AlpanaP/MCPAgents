"""
Data Manager for Delaware RAG Server.

This module handles data loading, indexing, and management
for the Delaware RAG server to improve maintainability.
"""

import logging
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from .config import QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME, VECTOR_SIZE, LICENSE_DATA_STRUCTURE
from .utils import chunk_text

logger = logging.getLogger(__name__)


class DelawareDataManager:
    """Manages data loading and indexing for Delaware RAG server."""
    
    def __init__(self):
        """Initialize the data manager."""
        self.embedding_model = None
        self.qdrant_client = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize embedding model and Qdrant client."""
        try:
            # Initialize embedding model
            logger.info("Loading embedding model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            self.embedding_model = None
        
        try:
            # Initialize Qdrant client
            logger.info("Initializing Qdrant client...")
            self.qdrant_client = QdrantClient(QDRANT_HOST, port=QDRANT_PORT)
            logger.info("Qdrant client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Qdrant client: {e}")
            self.qdrant_client = None
    
    def setup_collection(self):
        """Setup Qdrant collection for Delaware license data."""
        if not self.qdrant_client:
            logger.error("Qdrant client not available")
            return False
        
        try:
            # Check if collection exists
            collections = self.qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if COLLECTION_NAME not in collection_names:
                # Create collection
                self.qdrant_client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
                )
                logger.info(f"Created collection: {COLLECTION_NAME}")
            else:
                logger.info(f"Collection {COLLECTION_NAME} already exists")
            
            return True
        except Exception as e:
            logger.error(f"Error setting up collection: {e}")
            return False
    
    def load_delaware_data(self) -> List[Dict[str, Any]]:
        """Load Delaware-specific business license data."""
        delaware_data = [
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
                "text": "Cannabis Business License\n\nRequired for: cultivation, manufacturing, dispensing, testing, transportation\n\nRequirements:\n- Comprehensive business plan\n- Financial solvency proof\n- Security plan\n- Background checks for principals\n- Compliance with state regulations\n\nCost: $5,000-25,000 application fee\nDue Date: Apply 120 days before planned opening\nRenewal: Annual renewal required",
                "metadata": {"type": "license_details", "category": "cannabis", "source": "https://delawarecannabiscoalition.org/"}
            }
        ]
        
        # Add industry-specific data from configuration
        for industry, pattern in LICENSE_DATA_STRUCTURE.items():
            license_types = pattern.get("license_types", [])
            requirements = pattern.get("requirements", [])
            fees = pattern.get("fees", [])
            due_dates = pattern.get("due_dates", [])
            
            text_parts = [f"{industry.title()} Business Licenses\n\n"]
            
            for i, license_type in enumerate(license_types):
                text_parts.append(f"{license_type}\n")
                if i < len(fees):
                    text_parts.append(f"Cost: {fees[i]}\n")
                if i < len(due_dates):
                    text_parts.append(f"Due Date: {due_dates[i]}\n")
                text_parts.append("Renewal: Annual renewal required\n\n")
            
            if requirements:
                text_parts.append("Requirements:\n")
                for requirement in requirements:
                    text_parts.append(f"- {requirement}\n")
                text_parts.append("\n")
            
            delaware_data.append({
                "text": "".join(text_parts),
                "metadata": {"type": "license_details", "category": industry, "source": "https://firststeps.delaware.gov/topics/"}
            })
        
        return delaware_data
    
    def index_data(self, data: List[Dict[str, Any]]) -> bool:
        """Index data into Qdrant vector database."""
        if not self.qdrant_client or not self.embedding_model:
            logger.error("Qdrant client or embedding model not available")
            return False
        
        try:
            points = []
            point_id = 0
            
            for item in data:
                text = item.get("text", "")
                metadata = item.get("metadata", {})
                
                # Split text into chunks
                chunks = chunk_text(text)
                
                for chunk in chunks:
                    # Generate embedding
                    embedding = self.embedding_model.encode(chunk)
                    
                    # Create point
                    point = PointStruct(
                        id=point_id,
                        vector=embedding.tolist(),
                        payload={
                            "text": chunk,
                            "metadata": metadata
                        }
                    )
                    points.append(point)
                    point_id += 1
            
            # Upload points to Qdrant
            self.qdrant_client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
            
            logger.info(f"Indexed {len(points)} points into Qdrant")
            return True
            
        except Exception as e:
            logger.error(f"Error indexing data: {e}")
            return False
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar content in the vector database."""
        if not self.qdrant_client or not self.embedding_model:
            logger.error("Qdrant client or embedding model not available")
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query)
            
            # Search in Qdrant
            search_result = self.qdrant_client.search(
                collection_name=COLLECTION_NAME,
                query_vector=query_embedding.tolist(),
                limit=top_k
            )
            
            results = []
            for result in search_result:
                results.append({
                    "text": result.payload.get("text", ""),
                    "metadata": result.payload.get("metadata", {}),
                    "score": result.score
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the Qdrant collection."""
        if not self.qdrant_client:
            return {"error": "Qdrant client not available"}
        
        try:
            collection_info = self.qdrant_client.get_collection(COLLECTION_NAME)
            return {
                "name": collection_info.name,
                "vector_size": collection_info.config.params.vectors.size,
                "distance": collection_info.config.params.vectors.distance,
                "points_count": collection_info.points_count
            }
        except Exception as e:
            return {"error": f"Error getting collection info: {e}"} 
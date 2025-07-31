import asyncio
import json
import logging
import os
import sys
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import numpy as np

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    print("Warning: Qdrant client not available. Install with: pip install qdrant-client")

# Import semantic search
try:
    from core.semantic_search import semantic_search
    SEMANTIC_SEARCH_AVAILABLE = True
except ImportError:
    SEMANTIC_SEARCH_AVAILABLE = False
    print("Warning: Semantic search not available")

@dataclass
class SearchResult:
    content: List[Dict[str, str]]
    metadata: Dict[str, Any]

class GenericRAGServer:
    """Generic RAG server for business license information."""
    
    def __init__(self, state_config: Dict[str, Any] = None):
        """Initialize the generic RAG server."""
        self.logger = logging.getLogger(__name__)
        self.embedding_model = None
        self.qdrant_client = None
        self.collection_name = "generic_licenses"
        self.state_config = state_config or {}
        
        self._setup_embedding_model()
        self._setup_qdrant()
        self._load_generic_data()
    
    def _setup_embedding_model(self):
        """Set up the embedding model."""
        try:
            self.logger.info("Loading embedding model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.logger.info("Embedding model loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading embedding model: {e}")
            self.embedding_model = None
    
    def _setup_qdrant(self):
        """Set up Qdrant vector database."""
        if not QDRANT_AVAILABLE:
            self.logger.warning("Qdrant not available, using in-memory storage")
            return
        
        try:
            self.logger.info("Initializing Qdrant vector database...")
            self.qdrant_client = QdrantClient("localhost", port=6333)
            self.logger.info("Connected to Qdrant server")
            
            # Create collection if it doesn't exist
            try:
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
                self.logger.info(f"Created collection: {self.collection_name}")
            except Exception as e:
                self.logger.info(f"Collection {self.collection_name} already exists or error: {e}")
                
        except Exception as e:
            self.logger.error(f"Error setting up Qdrant collection: {e}")
            self.qdrant_client = None
    
    def _load_generic_data(self):
        """Load generic business license data based on state configuration."""
        self.generic_data = {
            "business_registration": [
                {
                    "title": "Business Entity Registration",
                    "content": "Register your business entity with the state Division of Corporations. Choose between LLC, Corporation, or Partnership based on your business needs.",
                    "url": self.state_config.get("url_patterns", {}).get("business_registration", "https://state.gov/business/"),
                    "category": "registration"
                },
                {
                    "title": "Tax Registration",
                    "content": "Register for state sales tax and other business taxes through the state Department of Revenue.",
                    "url": self.state_config.get("url_patterns", {}).get("revenue", "https://state.gov/tax/"),
                    "category": "tax"
                }
            ],
            "licensing_process": [
                {
                    "title": "License Application Process",
                    "content": "Apply for required business licenses through the state licensing portal. Complete background checks, examinations, and provide proof of financial responsibility as required.",
                    "url": self.state_config.get("url_patterns", {}).get("application_portal", "https://state.gov/apply/"),
                    "category": "licensing"
                },
                {
                    "title": "License Requirements",
                    "content": "Review specific requirements for your business type including education, experience, examinations, and background checks.",
                    "url": self.state_config.get("url_patterns", {}).get("requirements", "https://state.gov/requirements/"),
                    "category": "requirements"
                }
            ],
            "local_requirements": [
                {
                    "title": "Local Government Requirements",
                    "content": "Check with local city and county governments for additional permits, zoning requirements, and local business licenses.",
                    "url": "https://local.gov/",
                    "category": "local"
                }
            ]
        }
        
        # Add industry-specific data based on state configuration
        industry_patterns = self.state_config.get("industry_patterns", {})
        for industry, pattern in industry_patterns.items():
            self.generic_data[f"{industry}_licenses"] = [
                {
                    "title": f"{industry.title()} License Types",
                    "content": f"Available {industry} license types: {', '.join(pattern.get('license_types', []))}",
                    "url": self.state_config.get("url_patterns", {}).get("main_license_site", "https://state.gov/"),
                    "category": industry
                },
                {
                    "title": f"{industry.title()} Requirements",
                    "content": f"Requirements for {industry} licenses: {', '.join(pattern.get('requirements', []))}",
                    "url": self.state_config.get("url_patterns", {}).get("requirements", "https://state.gov/requirements/"),
                    "category": industry
                },
                {
                    "title": f"{industry.title()} Fees",
                    "content": f"Typical fees for {industry} licenses: {', '.join(pattern.get('fees', []))}",
                    "url": self.state_config.get("url_patterns", {}).get("fees", "https://state.gov/fees/"),
                    "category": industry
                }
            ]
        
        # Index the data in Qdrant
        self._index_generic_data()
    
    def _index_generic_data(self):
        """Index generic data in Qdrant."""
        if not self.qdrant_client or not self.embedding_model:
            return
        
        try:
            points = []
            point_id = 1
            
            for category, items in self.generic_data.items():
                for item in items:
                    # Create embedding
                    text = f"{item['title']} {item['content']}"
                    embedding = self.embedding_model.encode(text).tolist()
                    
                    # Create point
                    point = PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload={
                            "title": item["title"],
                            "content": item["content"],
                            "url": item["url"],
                            "category": item["category"],
                            "source": "generic_government"
                        }
                    )
                    points.append(point)
                    point_id += 1
            
            # Upload points to Qdrant
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            self.logger.info(f"Indexed {len(points)} generic license items")
            
        except Exception as e:
            self.logger.error(f"Error indexing generic data: {e}")
    
    async def _get_business_steps(self) -> SearchResult:
        """Get generic business registration steps."""
        steps = [
            {
                "text": "## Generic Business Registration Steps\n\n"
                        "### Step 1: Business Registration\n"
                        "- Register your business entity with state Division of Corporations\n"
                        "- Choose between LLC, Corporation, or Partnership\n"
                        "- File Articles of Organization/Incorporation\n"
                        "- Obtain EIN from IRS\n\n"
                        "### Step 2: Industry-Specific Licensing\n"
                        "- Determine required licenses for your business type\n"
                        "- Apply for licenses through state licensing portal\n"
                        "- Complete required education or training\n"
                        "- Pass required examinations\n"
                        "- Submit background checks if required\n\n"
                        "### Step 3: Tax Registration\n"
                        "- Register for state sales tax\n"
                        "- Register for federal taxes\n"
                        "- Set up accounting and record keeping\n\n"
                        "### Step 4: Local Requirements\n"
                        "- Check local city/county requirements\n"
                        "- Apply for local business licenses\n"
                        "- Check zoning requirements\n"
                        "- Obtain local permits if needed\n\n"
                        "### Step 5: Insurance and Compliance\n"
                        "- Obtain required insurance coverage\n"
                        "- Set up compliance monitoring\n"
                        "- Establish record keeping procedures\n\n"
                        "**Source**: State government licensing portal"
            }
        ]
        
        return SearchResult(content=steps, metadata={"source": "generic_government"})
    
    async def _get_license_categories(self) -> SearchResult:
        """Get generic license categories."""
        industry_patterns = self.state_config.get("industry_patterns", {})
        
        categories = ["## Generic Business License Categories\n\n"]
        
        for industry, pattern in industry_patterns.items():
            categories.append(f"### {industry.title()} Industry\n")
            for license_type in pattern.get("license_types", []):
                categories.append(f"- **{license_type}**: {industry} business operations\n")
            categories.append("\n")
        
        categories.append("**Source**: State government licensing portal")
        
        return SearchResult(content=[{"text": "".join(categories)}], metadata={"source": "generic_government"})
    
    async def _search_licenses_rag(self, query: str) -> SearchResult:
        """Search generic licenses using RAG."""
        if not self.qdrant_client or not self.embedding_model:
            return SearchResult(content=[{"text": "RAG search not available"}], metadata={})
        
        try:
            # Create query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in Qdrant
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=5
            )
            
            # Format results
            results = []
            for result in search_results:
                payload = result.payload
                results.append({
                    "text": f"**{payload['title']}**\n\n{payload['content']}\n\n"
                            f"**Source**: [{payload['title']}]({payload['url']})"
                })
            
            if not results:
                results = [{"text": "No specific license information found for your query."}]
            
            return SearchResult(content=results, metadata={"source": "generic_government"})
            
        except Exception as e:
            self.logger.error(f"Error in RAG search: {e}")
            return SearchResult(content=[{"text": f"Error searching licenses: {e}"}], metadata={})
    
    async def _get_similar_licenses(self, license_type: str) -> SearchResult:
        """Get similar license types."""
        industry_patterns = self.state_config.get("industry_patterns", {})
        
        # Find the industry that matches the license type
        matching_industry = None
        for industry, pattern in industry_patterns.items():
            if license_type.lower() in industry.lower():
                matching_industry = industry
                break
        
        if matching_industry:
            pattern = industry_patterns[matching_industry]
            licenses = pattern.get("license_types", [])
            
            result_text = f"## Similar Licenses for {license_type.title()}\n\n"
            for license_name in licenses:
                result_text += f"- **{license_name}**\n"
            
            result_text += f"\n**Source**: State government licensing portal"
        else:
            result_text = f"No similar licenses found for {license_type}"
        
        return SearchResult(content=[{"text": result_text}], metadata={"source": "generic_government"})

    # Add compatibility methods for the agent
    async def search_licenses(self, query: str):
        """Search for licenses using RAG or fallback."""
        try:
            result = await self._search_licenses_rag(query)
            return result
        except Exception as e:
            self.logger.error(f"Error in RAG search: {e}")
            # Fallback to semantic search
            if SEMANTIC_SEARCH_AVAILABLE:
                result_text = self._semantic_keyword_search(query)
                return SearchResult(content=[{"text": result_text}], metadata={"source": "semantic_search"})
            else:
                return SearchResult(content=[{"text": f"Error searching licenses: {e}"}], metadata={})

    def _semantic_keyword_search(self, query: str) -> str:
        """Enhanced semantic search using keyword matching and business type mapping."""
        if not SEMANTIC_SEARCH_AVAILABLE:
            return f"No semantic search available for query: {query}"
        
        # Get state code from config if available
        state_code = self.state_config.get("state_code", None)
        
        # Use the generic semantic search
        augmented_prompt_data = semantic_search.create_augmented_prompt(
            query, 
            state_code=state_code
        )
        
        semantic_results = augmented_prompt_data['semantic_results']
        business_types = semantic_results['detected_business_types']
        relevant_licenses = semantic_results['relevant_licenses']
        
        if business_types and relevant_licenses:
            result_text = f"Based on your business description '{query}', you likely need these licenses:\n\n"
            
            for i, license_name in enumerate(relevant_licenses, 1):
                result_text += f"{i}. **{license_name}**\n"
                result_text += f"   Contact the relevant state agency for specific requirements\n\n"
            
            result_text += "**Additional Requirements:**\n"
            result_text += "• Business Registration (required for all businesses)\n"
            result_text += "• Tax Registration (if collecting sales tax or have employees)\n"
            result_text += "• Federal EIN (Employer Identification Number)\n\n"
            
            result_text += "**Next Steps:**\n"
            result_text += "1. Register your business entity with the state Division of Corporations\n"
            result_text += "2. Apply for required licenses through the respective agencies\n"
            result_text += "3. Complete background checks and provide required documentation\n"
            result_text += "4. Pay application and license fees\n"
            result_text += "5. Maintain compliance and renew licenses annually\n"
            
        else:
            result_text = f"No specific licenses found for '{query}'.\n\n"
            result_text += "**General Business Requirements:**\n"
            result_text += "• Business Registration (required for all businesses)\n"
            result_text += "• Tax Registration (if applicable)\n"
            result_text += "• Federal EIN (Employer Identification Number)\n\n"
            result_text += "**Contact Information:**\n"
            result_text += "• Business Registration: Contact your state's Division of Corporations\n"
            result_text += "• Tax Registration: Contact your state's Department of Revenue\n"
            result_text += "• Licensing: Contact your state's licensing agency\n"
        
        return result_text

    async def get_business_steps(self):
        """Get business steps for generic state."""
        try:
            result = await self._get_business_steps()
            return result
        except Exception as e:
            self.logger.error(f"Error getting business steps: {e}")
            return SearchResult(content=[{"text": "Error getting business steps"}], metadata={})

    async def get_license_categories(self):
        """Get license categories for generic state."""
        try:
            result = await self._get_license_categories()
            return result
        except Exception as e:
            self.logger.error(f"Error getting license categories: {e}")
            return SearchResult(content=[{"text": "Error getting license categories"}], metadata={}) 
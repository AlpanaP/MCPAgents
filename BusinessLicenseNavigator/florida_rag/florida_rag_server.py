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

@dataclass
class SearchResult:
    content: List[Dict[str, str]]
    metadata: Dict[str, Any]

class FloridaRAGServer:
    """Florida RAG server for business license information."""
    
    def __init__(self):
        """Initialize the Florida RAG server."""
        self.logger = logging.getLogger(__name__)
        self.embedding_model = None
        self.qdrant_client = None
        self.collection_name = "florida_licenses"
        
        self._setup_embedding_model()
        self._setup_qdrant()
        self._load_florida_data()
    
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
    
    def _load_florida_data(self):
        """Load Florida business license data."""
        self.florida_data = {
            "construction_licenses": [
                {
                    "title": "Florida Construction Industry Licensing Board",
                    "content": "The Florida Construction Industry Licensing Board regulates construction contractors in Florida. All construction work requires a license from the DBPR.",
                    "url": "https://www.myfloridalicense.com/DBPR/construction-industry-licensing-board/",
                    "category": "construction"
                },
                {
                    "title": "Florida Contractor License Requirements",
                    "content": "To obtain a Florida contractor license, you must: 1) Be at least 18 years old, 2) Pass a background check, 3) Pass the Florida contractor exam, 4) Provide proof of financial responsibility, 5) Submit application with fees.",
                    "url": "https://www.myfloridalicense.com/DBPR/construction-industry-licensing-board/license-requirements/",
                    "category": "construction"
                },
                {
                    "title": "Florida Construction License Application",
                    "content": "Apply for a Florida contractor license through MyFloridaLicense.com. You'll need: Personal information, Business information, Financial responsibility proof, Background check results, Exam scores.",
                    "url": "https://www.myfloridalicense.com/DBPR/construction-industry-licensing-board/apply-for-license/",
                    "category": "construction"
                },
                {
                    "title": "Pinellas County Building Department",
                    "content": "Pinellas County Building Department handles building permits and inspections for construction projects in Pinellas County, including Palm Harbor.",
                    "url": "https://www.pinellascounty.org/building/",
                    "category": "construction"
                },
                {
                    "title": "Palm Harbor Building Permits",
                    "content": "Palm Harbor Development Services Department issues building permits for construction projects within Palm Harbor city limits.",
                    "url": "https://www.palmharbor.org/departments/development-services/",
                    "category": "construction"
                }
            ],
            "business_registration": [
                {
                    "title": "Florida Division of Corporations",
                    "content": "Register your business entity with the Florida Division of Corporations before applying for a contractor license. Choose between LLC, Corporation, or Partnership.",
                    "url": "https://dos.myflorida.com/sunbiz/",
                    "category": "registration"
                },
                {
                    "title": "Florida Business Tax Registration",
                    "content": "Register for Florida sales tax and other business taxes through the Florida Department of Revenue.",
                    "url": "https://floridarevenue.com/",
                    "category": "tax"
                }
            ],
            "local_requirements": [
                {
                    "title": "Pinellas County Contractor Requirements",
                    "content": "Pinellas County requires contractors to have a valid Florida contractor license and may require additional local permits for construction projects.",
                    "url": "https://www.pinellascounty.org/building/",
                    "category": "local"
                },
                {
                    "title": "Palm Harbor Development Services",
                    "content": "Palm Harbor Development Services Department handles building permits, zoning, and development approvals for construction projects in Palm Harbor.",
                    "url": "https://www.palmharbor.org/departments/development-services/",
                    "category": "local"
                }
            ]
        }
        
        # Index the data in Qdrant
        self._index_florida_data()
    
    def _index_florida_data(self):
        """Index Florida data in Qdrant."""
        if not self.qdrant_client or not self.embedding_model:
            return
        
        try:
            points = []
            point_id = 1
            
            for category, items in self.florida_data.items():
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
                            "source": "florida_government"
                        }
                    )
                    points.append(point)
                    point_id += 1
            
            # Upload points to Qdrant
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            self.logger.info(f"Indexed {len(points)} Florida license items")
            
        except Exception as e:
            self.logger.error(f"Error indexing Florida data: {e}")
    
    async def _get_business_steps(self) -> SearchResult:
        """Get Florida business registration steps."""
        steps = [
            {
                "text": "## Florida Construction Company Setup Steps\n\n"
                        "### Step 1: Business Registration\n"
                        "- Register your business entity with Florida Division of Corporations\n"
                        "- Choose between LLC, Corporation, or Partnership\n"
                        "- File Articles of Organization/Incorporation\n"
                        "- Obtain EIN from IRS\n\n"
                        "### Step 2: Contractor License Application\n"
                        "- Apply for Florida contractor license through DBPR\n"
                        "- Complete background check\n"
                        "- Pass Florida contractor examination\n"
                        "- Provide proof of financial responsibility\n"
                        "- Submit application with required fees\n\n"
                        "### Step 3: Local Permits and Requirements\n"
                        "- Contact Pinellas County Building Department\n"
                        "- Apply for Palm Harbor building permits\n"
                        "- Check zoning requirements\n"
                        "- Obtain local business license\n\n"
                        "### Step 4: Insurance and Compliance\n"
                        "- Obtain general liability insurance\n"
                        "- Get workers compensation insurance\n"
                        "- Register for Florida sales tax\n"
                        "- Set up accounting and record keeping\n\n"
                        "**Source**: [MyFloridaLicense.com](https://www2.myfloridalicense.com/)"
            }
        ]
        
        return SearchResult(content=steps, metadata={"source": "florida_government"})
    
    async def _get_license_categories(self) -> SearchResult:
        """Get Florida license categories."""
        categories = [
            {
                "text": "## Florida Business License Categories\n\n"
                        "### Construction Industry\n"
                        "- **General Contractor**: Residential and commercial construction\n"
                        "- **Building Contractor**: Structural construction\n"
                        "- **Residential Contractor**: Single-family and multi-family homes\n"
                        "- **Roofing Contractor**: Roof installation and repair\n"
                        "- **Plumbing Contractor**: Plumbing systems\n"
                        "- **Electrical Contractor**: Electrical systems\n"
                        "- **HVAC Contractor**: Heating, ventilation, air conditioning\n"
                        "- **Specialty Contractor**: Specific trades\n\n"
                        "### Other Industries\n"
                        "- **Real Estate**: Brokers, sales associates\n"
                        "- **Food Service**: Restaurants, catering\n"
                        "- **Professional Services**: Various professional licenses\n\n"
                        "**Source**: [Florida Construction Industry Licensing Board](https://www.myfloridalicense.com/DBPR/construction-industry-licensing-board/)"
            }
        ]
        
        return SearchResult(content=categories, metadata={"source": "florida_government"})
    
    async def _search_licenses_rag(self, query: str) -> SearchResult:
        """Search Florida licenses using RAG."""
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
                results = [{"text": "No specific Florida license information found for your query."}]
            
            return SearchResult(content=results, metadata={"source": "florida_government"})
            
        except Exception as e:
            self.logger.error(f"Error in RAG search: {e}")
            return SearchResult(content=[{"text": f"Error searching Florida licenses: {e}"}], metadata={})
    
    async def _get_similar_licenses(self, license_type: str) -> SearchResult:
        """Get similar license types in Florida."""
        similar_licenses = {
            "construction": [
                "General Contractor",
                "Building Contractor", 
                "Residential Contractor",
                "Roofing Contractor",
                "Plumbing Contractor",
                "Electrical Contractor",
                "HVAC Contractor"
            ],
            "real_estate": [
                "Real Estate Broker",
                "Real Estate Sales Associate",
                "Property Manager"
            ],
            "food": [
                "Restaurant License",
                "Catering License",
                "Food Service License"
            ]
        }
        
        licenses = similar_licenses.get(license_type.lower(), [])
        
        result_text = f"## Similar Florida Licenses for {license_type.title()}\n\n"
        for license_name in licenses:
            result_text += f"- **{license_name}**\n"
        
        result_text += f"\n**Source**: [MyFloridaLicense.com](https://www2.myfloridalicense.com/)"
        
        return SearchResult(content=[{"text": result_text}], metadata={"source": "florida_government"}) 
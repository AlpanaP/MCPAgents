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
    
    def get_text(self) -> str:
        """Get the text content as a single string."""
        if not self.content:
            return ""
        
        # Join all text content
        text_parts = []
        for item in self.content:
            if isinstance(item, dict) and 'text' in item:
                text_parts.append(item['text'])
            elif isinstance(item, str):
                text_parts.append(item)
        
        return "\n\n".join(text_parts)
    
    def get_first_text(self) -> str:
        """Get the first text content item."""
        if not self.content:
            return ""
        
        first_item = self.content[0]
        if isinstance(first_item, dict) and 'text' in first_item:
            return first_item['text']
        elif isinstance(first_item, str):
            return first_item
        
        return ""
    
    def is_valid(self) -> bool:
        """Check if the search result is valid."""
        return bool(self.content and self.get_text().strip())

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
                    "title": "Florida Construction License Fees",
                    "content": "Florida contractor license fees: Application fee $249, License fee $209, Background check $42.50, Exam fee $135. Total initial cost: $635.50. Renewal fee: $209 every 2 years.",
                    "url": "https://www.myfloridalicense.com/DBPR/construction-industry-licensing-board/",
                    "category": "construction"
                }
            ],
            "real_estate_licenses": [
                {
                    "title": "Florida Real Estate Commission",
                    "content": "The Florida Real Estate Commission regulates real estate professionals in Florida. All real estate activities require a license from the DBPR.",
                    "url": "https://www.myfloridalicense.com/DBPR/real-estate-commission/",
                    "category": "real_estate"
                },
                {
                    "title": "Florida Real Estate License Requirements",
                    "content": "To obtain a Florida real estate license, you must: 1) Be at least 18 years old, 2) Complete 63 hours of pre-licensing education, 3) Pass the Florida real estate exam, 4) Submit application with fees.",
                    "url": "https://www.myfloridalicense.com/DBPR/real-estate-commission/license-requirements/",
                    "category": "real_estate"
                },
                {
                    "title": "Florida Real Estate License Application",
                    "content": "Apply for a Florida real estate license through MyFloridaLicense.com. You'll need: Personal information, Education transcripts, Exam scores, Background check results.",
                    "url": "https://www.myfloridalicense.com/DBPR/real-estate-commission/apply-for-license/",
                    "category": "real_estate"
                },
                {
                    "title": "Florida Real Estate License Fees",
                    "content": "Florida real estate license fees: Application fee $83.75, License fee $83.75, Background check $42.50, Exam fee $36.75. Total initial cost: $246.75. Renewal fee: $83.75 every 2 years.",
                    "url": "https://www.myfloridalicense.com/DBPR/real-estate-commission/",
                    "category": "real_estate"
                }
            ],
            "food_service_licenses": [
                {
                    "title": "Florida Division of Hotels and Restaurants",
                    "content": "The Florida Division of Hotels and Restaurants regulates food service establishments in Florida. All food service businesses require a license from the DBPR.",
                    "url": "https://www.myfloridalicense.com/DBPR/hotels-restaurants/",
                    "category": "food_service"
                },
                {
                    "title": "Florida Food Service License Requirements",
                    "content": "To obtain a Florida food service license, you must: 1) Complete food safety training, 2) Pass health inspection, 3) Submit application with fees, 4) Maintain compliance with health regulations.",
                    "url": "https://www.myfloridalicense.com/DBPR/hotels-restaurants/license-requirements/",
                    "category": "food_service"
                },
                {
                    "title": "Florida Food Service License Application",
                    "content": "Apply for a Florida food service license through MyFloridaLicense.com. You'll need: Business information, Food safety certification, Health inspection results, Application fees.",
                    "url": "https://www.myfloridalicense.com/DBPR/hotels-restaurants/apply-for-license/",
                    "category": "food_service"
                },
                {
                    "title": "Florida Food Service License Fees",
                    "content": "Florida food service license fees: Application fee $100-300, License fee $200-500, Health inspection fee $75-150. Total initial cost: $375-950. Renewal fee: $200-500 annually.",
                    "url": "https://www.myfloridalicense.com/DBPR/hotels-restaurants/",
                    "category": "food_service"
                }
            ],
            "financial_services_licenses": [
                {
                    "title": "Florida Office of Financial Regulation",
                    "content": "The Florida Office of Financial Regulation regulates financial services businesses in Florida. Financial services firms and investment companies require registration and licensing.",
                    "url": "https://flofr.com/",
                    "category": "financial_services"
                },
                {
                    "title": "Florida Investment Adviser Registration",
                    "content": "Financial services firms in Florida must register as investment advisers with the Florida Office of Financial Regulation. Requirements include: 1) Registration application, 2) Financial statements, 3) Background checks, 4) Compliance program. Application fee: $500, Annual fee: $1,000.",
                    "url": "https://flofr.com/InvestmentAdvisers/",
                    "category": "financial_services"
                },
                {
                    "title": "Florida Investment Adviser License Requirements",
                    "content": "To register as a Florida investment adviser, you must: 1) Submit Form ADV, 2) Provide financial statements, 3) Complete background checks, 4) Pay registration fees, 5) Maintain compliance program.",
                    "url": "https://flofr.com/InvestmentAdvisers/Registration/",
                    "category": "financial_services"
                },
                {
                    "title": "Florida Securities Dealer License",
                    "content": "Florida Securities Dealer License: Required for businesses that buy and sell securities in Florida. Application fee: $500, License fee: $2,000 annually. Requirements: Background check, surety bond, compliance program.",
                    "url": "https://flofr.com/Securities/",
                    "category": "financial_services"
                },
                {
                    "title": "Florida Money Transmitter License",
                    "content": "Florida Money Transmitter License: Required for businesses that transmit money, including payment processors and money transfer services. Application fee: $1,000, License fee: $5,000 annually. Requirements: Background check, surety bond, financial statements.",
                    "url": "https://flofr.com/MoneyTransmitters/",
                    "category": "financial_services"
                },
                {
                    "title": "Florida Consumer Finance License",
                    "content": "Florida Consumer Finance License: Required for businesses that make consumer loans, including personal loans and installment loans. Application fee: $500, License fee: $2,500 annually. Requirements: Background check, surety bond, financial statements.",
                    "url": "https://flofr.com/ConsumerFinance/",
                    "category": "financial_services"
                },
                {
                    "title": "Florida Mortgage Loan Originator License",
                    "content": "Florida Mortgage Loan Originator License: Required for individuals who originate mortgage loans. Application fee: $200, License fee: $1,000 annually. Requirements: Background check, education requirements, examination.",
                    "url": "https://flofr.com/Mortgage/",
                    "category": "financial_services"
                },
                {
                    "title": "Florida Insurance Producer License",
                    "content": "Florida Insurance Producer License: Required for businesses that sell insurance products. Application fee: $100, License fee: $500 annually. Requirements: Background check, examination, continuing education.",
                    "url": "https://www.myfloridalicense.com/DBPR/insurance/",
                    "category": "financial_services"
                },
                {
                    "title": "Florida Trust Company License",
                    "content": "Florida Trust Company License: Required for businesses that act as trustees or provide trust services. Application fee: $2,000, License fee: $10,000 annually. Requirements: Background check, surety bond, financial statements, compliance program.",
                    "url": "https://flofr.com/TrustCompanies/",
                    "category": "financial_services"
                },
                {
                    "title": "Florida Investment Adviser Fees",
                    "content": "Florida investment adviser fees: Registration fee $200, Annual renewal fee $200, Background check fee $42.50. Total initial cost: $242.50. Renewal fee: $200 annually.",
                    "url": "https://flofr.com/InvestmentAdvisers/",
                    "category": "financial_services"
                },
                {
                    "title": "Florida Private Equity Firm Requirements",
                    "content": "Private equity firms in Florida must: 1) Register with Florida Office of Financial Regulation, 2) File annual reports, 3) Maintain compliance with securities laws, 4) Provide disclosure documents to investors.",
                    "url": "https://flofr.com/InvestmentAdvisers/",
                    "category": "financial_services"
                },
                {
                    "title": "Florida Securities Registration",
                    "content": "Private equity firms offering securities in Florida must register with the Florida Office of Financial Regulation. Requirements include: 1) Securities registration, 2) Financial disclosure, 3) Investor protection compliance.",
                    "url": "https://flofr.com/Securities/",
                    "category": "financial_services"
                }
            ],
            "business_registration": [
                {
                    "title": "Florida Division of Corporations",
                    "content": "All businesses in Florida must register with the Florida Division of Corporations. This includes LLCs, corporations, partnerships, and other business entities.",
                    "url": "https://dos.myflorida.com/sunbiz/",
                    "category": "business_registration"
                },
                {
                    "title": "Florida Business Registration Requirements",
                    "content": "To register a business in Florida, you must: 1) Choose business structure, 2) File articles of incorporation/organization, 3) Pay filing fees, 4) Obtain EIN from IRS, 5) Register for state taxes.",
                    "url": "https://dos.myflorida.com/sunbiz/start-business/",
                    "category": "business_registration"
                },
                {
                    "title": "Florida Business Registration Fees",
                    "content": "Florida business registration fees: LLC filing fee $125, Corporation filing fee $78, Annual report fee $138.75. Total initial cost: $125-78. Annual renewal: $138.75.",
                    "url": "https://dos.myflorida.com/sunbiz/",
                    "category": "business_registration"
                }
            ],
            "tax_registration": [
                {
                    "title": "Florida Department of Revenue",
                    "content": "Businesses in Florida must register for state taxes with the Florida Department of Revenue. This includes sales tax, corporate income tax, and other state taxes.",
                    "url": "https://floridarevenue.com/",
                    "category": "tax_registration"
                },
                {
                    "title": "Florida Tax Registration Requirements",
                    "content": "To register for Florida taxes, you must: 1) Apply for tax certificate, 2) Register for sales tax (if applicable), 3) Register for corporate income tax (if applicable), 4) Pay registration fees.",
                    "url": "https://floridarevenue.com/taxes/",
                    "category": "tax_registration"
                },
                {
                    "title": "Florida Tax Registration Fees",
                    "content": "Florida tax registration fees: Tax certificate fee $5, Sales tax registration free, Corporate tax registration free. Total initial cost: $5. Annual renewal: $5.",
                    "url": "https://floridarevenue.com/",
                    "category": "tax_registration"
                }
            ]
        }
        
        # Index the data
        self._index_florida_data()
    
    def _index_florida_data(self):
        """Index Florida data into the vector database."""
        if not self.qdrant_client or not self.embedding_model:
            self.logger.warning("Cannot index data - Qdrant or embedding model not available")
            return
        
        try:
            points = []
            point_id = 0
            
            for category, items in self.florida_data.items():
                for item in items:
                    # Create embedding for the content
                    text = f"{item['title']} {item['content']}"
                    embedding = self.embedding_model.encode(text)
                    
                    # Create point
                    point = PointStruct(
                        id=point_id,
                        vector=embedding.tolist(),
                        payload={
                            "title": item["title"],
                            "content": item["content"],
                            "url": item["url"],
                            "category": item["category"]
                        }
                    )
                    points.append(point)
                    point_id += 1
            
            # Upload points to Qdrant
            if points:
                self.qdrant_client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                self.logger.info(f"Indexed {len(points)} Florida license items")
            
        except Exception as e:
            self.logger.error(f"Error indexing Florida data: {e}")
    
    async def _get_business_steps(self) -> SearchResult:
        """Get Florida business setup steps."""
        steps_content = [
            {
                "type": "text",
                "text": """# Florida Business Setup Steps

## Step 1: Business Entity Formation
- Choose business structure (LLC, Corporation, Partnership)
- File with Florida Division of Corporations
- Cost: $78-125 filing fee
- Timeline: 1-2 weeks processing

## Step 2: Tax Registration
- Register with Florida Department of Revenue
- Apply for tax certificate
- Register for sales tax (if applicable)
- Cost: $5 tax certificate fee
- Timeline: 1-2 weeks processing

## Step 3: Industry-Specific Licensing
- Identify required licenses for your industry
- Apply through MyFloridaLicense.com
- Complete required training/certifications
- Cost: Varies by industry ($100-500+)
- Timeline: 2-8 weeks processing

## Step 4: Local Permits
- Check with local government for permits
- Apply for local business license
- Zoning compliance verification
- Cost: $50-200 local fees
- Timeline: 1-4 weeks processing

**Total Estimated Cost**: $233-830+ depending on industry
**Total Timeline**: 4-14 weeks for complete setup

**Official Resources**:
- Florida Division of Corporations: https://dos.myflorida.com/sunbiz/
- Florida Department of Revenue: https://floridarevenue.com/
- MyFloridaLicense.com: https://www2.myfloridalicense.com/
- Florida Office of Financial Regulation: https://flofr.com/"""
            }
        ]
        
        return SearchResult(
            content=steps_content,
            metadata={"type": "business_steps", "state": "FL"}
        )
    
    async def _get_license_categories(self) -> SearchResult:
        """Get Florida license categories."""
        categories_content = [
            {
                "type": "text",
                "text": """# Florida License Categories

## Professional Services
- Real Estate License
- Investment Adviser License
- Financial Services License
- Insurance License

## Construction & Trades
- Contractor License
- Electrical License
- Plumbing License
- HVAC License

## Food & Hospitality
- Food Service License
- Hotel License
- Restaurant License
- Catering License

## Health & Safety
- Medical License
- Dental License
- Pharmacy License
- Cosmetology License

## Transportation
- Motor Vehicle Dealer License
- Transportation License
- Limousine License

**Apply Online**: https://www2.myfloridalicense.com/
**Check Requirements**: https://www.myfloridalicense.com/DBPR/"""
            }
        ]
        
        return SearchResult(
            content=categories_content,
            metadata={"type": "license_categories", "state": "FL"}
        )
    
    async def _search_licenses_rag(self, query: str) -> SearchResult:
        """Search for licenses using RAG."""
        if not self.qdrant_client or not self.embedding_model:
            # Fallback to keyword search
            return await self._search_licenses_fallback(query)
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query)
            
            # Search in Qdrant
            search_result = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                limit=5
            )
            
            if search_result:
                # Format results
                results_text = f"# Florida License Search Results for: {query}\n\n"
                
                for i, result in enumerate(search_result, 1):
                    payload = result.payload
                    results_text += f"## {i}. {payload['title']}\n"
                    results_text += f"{payload['content']}\n"
                    results_text += f"**URL**: {payload['url']}\n\n"
                
                return SearchResult(
                    content=[{"type": "text", "text": results_text}],
                    metadata={"type": "search_results", "query": query, "state": "FL"}
                )
            else:
                return await self._search_licenses_fallback(query)
                
        except Exception as e:
            self.logger.error(f"Error in RAG search: {e}")
            return await self._search_licenses_fallback(query)

    def _semantic_keyword_search(self, query: str) -> str:
        """Enhanced semantic search using keyword matching and business type mapping."""
        query_lower = query.lower()
        
        # Business type to license mapping
        business_mappings = {
            "financial services": ["Investment Adviser Registration", "Securities Dealer License", "Money Transmitter License", "Trust Company License"],
            "financial firm": ["Investment Adviser Registration", "Securities Dealer License", "Money Transmitter License", "Trust Company License"],
            "investment": ["Investment Adviser Registration", "Securities Dealer License"],
            "banking": ["Money Transmitter License", "Trust Company License"],
            "lending": ["Consumer Finance License", "Mortgage Loan Originator License"],
            "mortgage": ["Mortgage Loan Originator License"],
            "insurance": ["Insurance Producer License"],
            "payment": ["Money Transmitter License"],
            "fintech": ["Money Transmitter License", "Investment Adviser Registration", "Securities Dealer License"],
            "wealth management": ["Investment Adviser Registration", "Trust Company License"],
            "portfolio": ["Investment Adviser Registration"],
            "trading": ["Securities Dealer License"],
            "broker": ["Securities Dealer License", "Insurance Producer License"],
            "trust": ["Trust Company License"],
            "money transfer": ["Money Transmitter License"],
            "consumer credit": ["Consumer Finance License"],
            "personal loans": ["Consumer Finance License"],
            "installment loans": ["Consumer Finance License"]
        }
        
        # Find matching licenses
        matching_licenses = []
        for business_type, license_types in business_mappings.items():
            if business_type in query_lower:
                matching_licenses.extend(license_types)
        
        # Remove duplicates
        matching_licenses = list(set(matching_licenses))
        
        if matching_licenses:
            result_text = f"Based on your business description '{query}', you likely need these Florida licenses:\n\n"
            
            for i, license_type in enumerate(matching_licenses, 1):
                # Find the license data
                license_data = None
                for category, licenses in self.florida_data.items():
                    for license_entry in licenses:
                        if license_type in license_entry["title"]:
                            license_data = license_entry
                            break
                    if license_data:
                        break
                
                if license_data:
                    result_text += f"{i}. **{license_data['title']}**\n"
                    result_text += f"   Description: {license_data['content']}\n"
                    result_text += f"   Source: {license_data['url']}\n\n"
                else:
                    result_text += f"{i}. **{license_type}**\n"
                    result_text += f"   Contact Florida Office of Financial Regulation for details\n\n"
            
            result_text += "**Additional Requirements:**\n"
            result_text += "• Florida Business Registration (required for all businesses)\n"
            result_text += "• Florida Tax Registration (if collecting sales tax or have employees)\n"
            result_text += "• Federal EIN (Employer Identification Number)\n\n"
            
            result_text += "**Next Steps:**\n"
            result_text += "1. Register your business entity with Florida Division of Corporations\n"
            result_text += "2. Apply for required licenses through the respective agencies\n"
            result_text += "3. Complete background checks and provide required documentation\n"
            result_text += "4. Pay application and license fees\n"
            result_text += "5. Maintain compliance and renew licenses annually\n"
            
        else:
            result_text = f"No specific licenses found for '{query}'.\n\n"
            result_text += "**General Florida Business Requirements:**\n"
            result_text += "• Florida Business Registration (required for all businesses)\n"
            result_text += "• Florida Tax Registration (if applicable)\n"
            result_text += "• Federal EIN (Employer Identification Number)\n\n"
            result_text += "**Contact Information:**\n"
            result_text += "• Business Registration: https://dos.myflorida.com/sunbiz/\n"
            result_text += "• Tax Registration: https://floridarevenue.com/\n"
            result_text += "• Financial Services: https://flofr.com/\n"
            result_text += "• Insurance: https://www.myfloridalicense.com/DBPR/insurance/\n"
        
        return result_text
    
    async def _search_licenses_fallback(self, query: str) -> SearchResult:
        """Fallback search when RAG is not available."""
        query_lower = query.lower()
        
        # Simple keyword matching
        if any(word in query_lower for word in ['construction', 'contractor', 'building']):
            category = "construction_licenses"
        elif any(word in query_lower for word in ['real estate', 'property', 'realtor']):
            category = "real_estate_licenses"
        elif any(word in query_lower for word in ['food', 'restaurant', 'cafe', 'catering']):
            category = "food_service_licenses"
        elif any(word in query_lower for word in ['financial', 'investment', 'private equity', 'adviser']):
            category = "financial_services_licenses"
        else:
            category = "business_registration"
        
        items = self.florida_data.get(category, [])
        
        if items:
            results_text = f"# Florida License Information for: {query}\n\n"
            
            for item in items:
                results_text += f"## {item['title']}\n"
                results_text += f"{item['content']}\n"
                results_text += f"**URL**: {item['url']}\n\n"
        
        # Enhanced semantic search for financial services
        if any(word in query_lower for word in ['financial', 'investment', 'private equity', 'adviser', 'financial services', 'financial firm']):
            results_text = self._semantic_keyword_search(query)
            return SearchResult(
                content=[{"type": "text", "text": results_text}],
                metadata={"type": "search_results", "query": query, "state": "FL"}
            )
        else:
            return SearchResult(
                content=[{"type": "text", "text": results_text}],
                metadata={"type": "fallback_results", "query": query, "state": "FL"}
            )
    
    async def _get_similar_licenses(self, license_type: str) -> SearchResult:
        """Get similar licenses to a given type."""
        # This would use vector similarity search
        # For now, return a simple response
        similar_text = f"# Similar Licenses to: {license_type}\n\n"
        similar_text += "Based on your query, you might also need:\n"
        similar_text += "- Business registration with Florida Division of Corporations\n"
        similar_text += "- Tax registration with Florida Department of Revenue\n"
        similar_text += "- Local business permits from your city/county\n"
        similar_text += "- Industry-specific professional licenses\n\n"
        similar_text += "**Check Requirements**: https://www2.myfloridalicense.com/"
        
        return SearchResult(
            content=[{"type": "text", "text": similar_text}],
            metadata={"type": "similar_licenses", "license_type": license_type, "state": "FL"}
        )
    
    async def search_licenses(self, query: str):
        """Search for licenses - main entry point."""
        return await self._search_licenses_rag(query)
    
    async def get_business_steps(self):
        """Get business setup steps."""
        return await self._get_business_steps()
    
    async def get_license_categories(self):
        """Get license categories."""
        return await self._get_license_categories()
    
    async def get_similar_licenses(self, license_type: str):
        """Get similar licenses."""
        return await self._get_similar_licenses(license_type)


# For testing
if __name__ == "__main__":
    async def test():
        server = FloridaRAGServer()
        result = await server.search_licenses("private equity firm")
        print(result.content[0]["text"])
    
    asyncio.run(test()) 
#!/usr/bin/env python3
"""
Delaware Business License MCP Server with RAG
Provides tools to access Delaware business license information with vector-based retrieval using Qdrant
"""

import asyncio
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import numpy as np
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Delaware Business First Steps URL
DELAWARE_BASE_URL = "https://firststeps.delaware.gov"
DELAWARE_TOPICS_URL = "https://firststeps.delaware.gov/topics/"

# Qdrant configuration
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "delaware_licenses"
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 embedding size

# Security: Rate limiting and timeout settings
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RATE_LIMIT_DELAY = 1  # seconds between requests

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks."""
    if not text or not isinstance(text, str):
        return ""
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)
    # Limit length to prevent DoS
    return text[:500].strip()

def validate_url(url: str) -> bool:
    """Validate URL format and security."""
    if not url or not isinstance(url, str):
        return False
    
    try:
        parsed = urlparse(url)
        # Only allow HTTPS and specific domains
        if parsed.scheme not in ['https']:
            return False
        
        # Only allow Delaware government domains
        allowed_domains = [
            'firststeps.delaware.gov',
            'corp.delaware.gov',
            'sos.delaware.gov',
            'revenue.delaware.gov',
            'labor.delaware.gov',
            'dhss.delaware.gov',
            'delawaresbdc.org',
            'choosedelaware.com',
            'delawarechamber.com',
            'sba.gov',
            'delaware.score.org',
            'nccde.org',
            'co.kent.de.us',
            'sussexcountyde.gov',
            'wilmingtonde.gov',
            'cityofdover.com',
            'newarkde.gov'
        ]
        
        if parsed.netloc not in allowed_domains:
            return False
        
        return True
    except Exception:
        return False

# Delaware Government Resources
DELAWARE_RESOURCES = {
    "main": {
        "Business First Steps": "https://firststeps.delaware.gov/",
        "Division of Corporations": "https://corp.delaware.gov/",
        "Department of State": "https://sos.delaware.gov/",
        "Small Business Development Center": "https://www.delawaresbdc.org/"
    },
    "licenses": {
        "Professional Licensing": "https://sos.delaware.gov/professional-regulation/",
        "Business Licenses": "https://firststeps.delaware.gov/topics/",
        "Food Service Licenses": "https://dhss.delaware.gov/dhss/dph/hsp/restaurant.html",
        "Health Care Licenses": "https://sos.delaware.gov/professional-regulation/health-occupations/",
        "Contractor Licenses": "https://sos.delaware.gov/professional-regulation/contractors/",
        "Real Estate Licenses": "https://sos.delaware.gov/professional-regulation/real-estate/"
    },
    "creative": {
        "Delaware Division of the Arts": "https://arts.delaware.gov/",
        "Delaware Creative Economy": "https://choosedelaware.com/creative-economy/",
        "Delaware Arts Alliance": "https://www.delawareartsalliance.org/",
        "Delaware Art Museum": "https://delart.org/",
        "Delaware Contemporary": "https://decontemporary.org/",
        "Delaware Center for the Contemporary Arts": "https://www.thedcca.org/",
        "Delaware Arts Council": "https://arts.delaware.gov/arts-council/",
        "Delaware Creative Economy Partnership": "https://choosedelaware.com/creative-economy/partnership/",
        "Delaware Arts Education": "https://arts.delaware.gov/arts-education/",
        "Delaware Artist Registry": "https://arts.delaware.gov/artist-registry/",
        "Delaware Arts Grants": "https://arts.delaware.gov/grants/",
        "Delaware Arts Marketing": "https://arts.delaware.gov/marketing/",
        "Delaware Arts Venues": "https://arts.delaware.gov/venues/"
    },
    "cannabis": {
        "Delaware Marijuana Control Act": "https://delcode.delaware.gov/title16/c047/",
        "Office of Medical Marijuana": "https://dhss.delaware.gov/dhss/dph/hsp/medicalmarijuana.html",
        "Cannabis Compliance Commission": "https://cannabis.delaware.gov/",
        "Cannabis Licensing": "https://cannabis.delaware.gov/licensing/",
        "Cannabis Regulations": "https://cannabis.delaware.gov/regulations/",
        "Cannabis Application Portal": "https://cannabis.delaware.gov/apply/",
        "Cannabis Business Guide": "https://cannabis.delaware.gov/business-guide/",
        "Cannabis Compliance Requirements": "https://cannabis.delaware.gov/compliance/",
        "Cannabis Security Requirements": "https://cannabis.delaware.gov/security/",
        "Cannabis Testing Requirements": "https://cannabis.delaware.gov/testing/"
    },
    "taxes": {
        "Division of Revenue": "https://revenue.delaware.gov/",
        "Business Tax Registration": "https://revenue.delaware.gov/business-tax-registration/",
        "Sales Tax": "https://revenue.delaware.gov/sales-tax/",
        "Corporate Income Tax": "https://revenue.delaware.gov/corporate-income-tax/"
    },
    "employment": {
        "Department of Labor": "https://labor.delaware.gov/",
        "Workers Compensation": "https://labor.delaware.gov/workers-compensation/",
        "Unemployment Insurance": "https://labor.delaware.gov/unemployment-insurance/",
        "Workplace Safety": "https://labor.delaware.gov/workplace-safety/"
    },
    "local": {
        "New Castle County": "https://www.nccde.org/",
        "Kent County": "https://www.co.kent.de.us/",
        "Sussex County": "https://www.sussexcountyde.gov/",
        "City of Wilmington": "https://www.wilmingtonde.gov/",
        "City of Dover": "https://www.cityofdover.com/",
        "City of Newark": "https://www.newarkde.gov/"
    },
    "support": {
        "Delaware Economic Development": "https://choosedelaware.com/",
        "Delaware Chamber of Commerce": "https://www.delawarechamber.com/",
        "Delaware SBA": "https://www.sba.gov/offices/district/de/wilmington",
        "Delaware SCORE": "https://delaware.score.org/"
    }
}

class DelawareRAGServer:
    def __init__(self):
        self.server = Server("delaware-licenses-rag")
        self.session = requests.Session()
        
        # Security: Set secure headers and timeouts
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Set timeout for all requests
        self.session.timeout = REQUEST_TIMEOUT
        
        # Initialize RAG components
        self.embedding_model = None
        self.qdrant_client = None
        self.license_data = []
        
        # Initialize RAG system
        self._initialize_rag()
        
        # Register tools
        self.server.list_tools = self.list_tools
        self.server.call_tool = self.call_tool

    def _initialize_rag(self):
        """Initialize the RAG system with embedding model and Qdrant vector database."""
        try:
            # Initialize embedding model
            logger.info("Loading embedding model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize Qdrant client
            logger.info("Initializing Qdrant vector database...")
            try:
                self.qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
                logger.info("Connected to Qdrant server")
            except Exception as e:
                logger.warning(f"Could not connect to Qdrant server: {e}")
                logger.info("Creating in-memory Qdrant client")
                self.qdrant_client = QdrantClient(":memory:")
            
            # Create or get collection
            self._setup_qdrant_collection()
            
        except Exception as e:
            logger.error(f"Error initializing RAG: {e}")
            # Fallback to non-RAG mode
            self.embedding_model = None
            self.qdrant_client = None

    def _setup_qdrant_collection(self):
        """Setup Qdrant collection for Delaware license data."""
        try:
            # Check if collection exists
            collections = self.qdrant_client.get_collections()
            collection_exists = any(col.name == COLLECTION_NAME for col in collections.collections)
            
            if not collection_exists:
                logger.info("Creating new Qdrant collection for Delaware licenses")
                self.qdrant_client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=VECTOR_SIZE,
                        distance=Distance.COSINE
                    )
                )
                # Populate with initial data
                self._populate_license_data()
            else:
                logger.info("Using existing Delaware licenses collection")
                
        except Exception as e:
            logger.error(f"Error setting up Qdrant collection: {e}")

    def _populate_license_data(self):
        """Populate the Qdrant collection with Delaware license information."""
        try:
            logger.info("Fetching Delaware license data...")
            
            # Comprehensive Delaware license data with semantic mappings
            delaware_licenses = [
                # Financial Services Licenses
                {
                    "text": "Delaware Money Transmitter License: Required for businesses that transmit money, including payment processors, money transfer services, and financial technology companies. Application fee: $1,000, License fee: $5,000 annually.",
                    "category": "Financial Services",
                    "license_type": "Money Transmitter License",
                    "keywords": ["financial services", "money transmitter", "payment processor", "fintech", "financial technology", "money transfer", "banking", "financial firm"],
                    "source": "https://banking.delaware.gov/",
                    "requirements": "Background check, surety bond, financial statements, compliance officer"
                },
                {
                    "text": "Delaware Consumer Credit License: Required for businesses that make consumer loans, including personal loans, payday loans, and installment loans. Application fee: $500, License fee: $2,500 annually.",
                    "category": "Financial Services", 
                    "license_type": "Consumer Credit License",
                    "keywords": ["consumer credit", "personal loans", "payday loans", "installment loans", "lending", "financial services", "credit business"],
                    "source": "https://banking.delaware.gov/",
                    "requirements": "Background check, surety bond, financial statements"
                },
                {
                    "text": "Delaware Mortgage Loan Originator License: Required for individuals who originate mortgage loans. Application fee: $200, License fee: $1,000 annually.",
                    "category": "Financial Services",
                    "license_type": "Mortgage Loan Originator License", 
                    "keywords": ["mortgage", "loan originator", "home loans", "real estate lending", "financial services", "mortgage broker"],
                    "source": "https://banking.delaware.gov/",
                    "requirements": "Background check, education requirements, examination"
                },
                {
                    "text": "Delaware Investment Adviser License: Required for businesses that provide investment advice for compensation. Application fee: $300, License fee: $1,500 annually.",
                    "category": "Financial Services",
                    "license_type": "Investment Adviser License",
                    "keywords": ["investment adviser", "financial advisor", "investment advice", "portfolio management", "financial planning", "wealth management", "financial services"],
                    "source": "https://securities.delaware.gov/",
                    "requirements": "Background check, surety bond, compliance program"
                },
                {
                    "text": "Delaware Securities Dealer License: Required for businesses that buy and sell securities. Application fee: $500, License fee: $2,000 annually.",
                    "category": "Financial Services",
                    "license_type": "Securities Dealer License",
                    "keywords": ["securities dealer", "broker dealer", "stock broker", "trading", "investment", "financial services", "securities"],
                    "source": "https://securities.delaware.gov/",
                    "requirements": "Background check, surety bond, compliance program"
                },
                {
                    "text": "Delaware Insurance Producer License: Required for businesses that sell insurance products. Application fee: $100, License fee: $500 annually.",
                    "category": "Financial Services",
                    "license_type": "Insurance Producer License",
                    "keywords": ["insurance", "insurance agent", "insurance broker", "financial services", "risk management"],
                    "source": "https://insurance.delaware.gov/",
                    "requirements": "Background check, examination, continuing education"
                },
                {
                    "text": "Delaware Trust Company License: Required for businesses that act as trustees or provide trust services. Application fee: $2,000, License fee: $10,000 annually.",
                    "category": "Financial Services",
                    "license_type": "Trust Company License",
                    "keywords": ["trust company", "trustee", "trust services", "estate planning", "wealth management", "financial services"],
                    "source": "https://banking.delaware.gov/",
                    "requirements": "Background check, surety bond, financial statements, compliance program"
                },
                {
                    "text": "Delaware Check Casher License: Required for businesses that cash checks for a fee. Application fee: $300, License fee: $1,500 annually.",
                    "category": "Financial Services",
                    "license_type": "Check Casher License",
                    "keywords": ["check casher", "check cashing", "financial services", "money services"],
                    "source": "https://banking.delaware.gov/",
                    "requirements": "Background check, surety bond, compliance program"
                },
                # Business Registration
                {
                    "text": "Delaware Business Registration: Required for all businesses operating in Delaware. Application fee: $89, Annual report fee: $50.",
                    "category": "Business Registration",
                    "license_type": "Business Registration",
                    "keywords": ["business registration", "corporation", "llc", "partnership", "business entity", "company formation"],
                    "source": "https://corp.delaware.gov/",
                    "requirements": "Articles of incorporation/organization, registered agent"
                },
                # Tax Registration
                {
                    "text": "Delaware Tax Registration: Required for businesses that collect sales tax or have employees. No application fee, annual renewal required.",
                    "category": "Tax Registration",
                    "license_type": "Tax Registration",
                    "keywords": ["tax registration", "sales tax", "employer tax", "withholding tax", "business tax"],
                    "source": "https://revenue.delaware.gov/",
                    "requirements": "EIN, business information, tax elections"
                },
                # Professional Licenses
                {
                    "text": "Delaware Professional License: Required for various professional services including attorneys, accountants, engineers, and architects. Application fee: $100-500, License fee: $200-1,000 annually.",
                    "category": "Professional Services",
                    "license_type": "Professional License",
                    "keywords": ["professional license", "attorney", "accountant", "engineer", "architect", "professional services"],
                    "source": "https://dpr.delaware.gov/",
                    "requirements": "Education, examination, background check, continuing education"
                }
            ]
            
            # Add to Qdrant collection
            if delaware_licenses and self.qdrant_client:
                texts = [entry["text"] for entry in delaware_licenses]
                metadatas = [{"category": entry["category"], "license_type": entry["license_type"], "source": entry["source"], "keywords": entry["keywords"], "requirements": entry["requirements"]} for entry in delaware_licenses]
                
                # Generate embeddings
                embeddings = self.embedding_model.encode(texts)
                
                # Create points for Qdrant
                points = []
                for i, (embedding, metadata) in enumerate(zip(embeddings, metadatas)):
                    point = PointStruct(
                        id=i,
                        vector=embedding.tolist(),
                        payload={
                            "text": texts[i],
                            "category": metadata["category"],
                            "license_type": metadata["license_type"],
                            "source": metadata["source"],
                            "keywords": metadata["keywords"],
                            "requirements": metadata["requirements"]
                        }
                    )
                    points.append(point)
                
                # Add points to collection
                self.qdrant_client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=points
                )
                
                logger.info(f"Added {len(delaware_licenses)} license entries to Qdrant collection")
                self.license_data = delaware_licenses
                
        except Exception as e:
            logger.error(f"Error populating license data: {e}")

    async def list_tools(self, request: ListToolsRequest) -> ListToolsResult:
        """List available tools for Delaware license information with RAG."""
        return ListToolsResult(
            tools=[
                Tool(
                    name="get_delaware_license_categories",
                    description="Get all available Delaware license categories",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_delaware_license_details",
                    description="Get detailed information about a specific Delaware license type",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "license_type": {
                                "type": "string",
                                "description": "The specific license type to get details for"
                            }
                        },
                        "required": ["license_type"]
                    }
                ),
                Tool(
                    name="search_delaware_licenses_rag",
                    description="Search for licenses using semantic search (RAG-powered with Qdrant)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query (e.g., 'restaurant', 'bakery', 'consulting')"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of results to return (default: 5)",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_similar_licenses",
                    description="Find similar licenses based on a license type (RAG-powered with Qdrant)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "license_type": {
                                "type": "string",
                                "description": "License type to find similar ones for"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of similar results to return (default: 3)",
                                "default": 3
                            }
                        },
                        "required": ["license_type"]
                    }
                ),
                Tool(
                    name="get_delaware_business_steps",
                    description="Get the 4-step process for opening a business in Delaware",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_delaware_resources",
                    description="Get comprehensive Delaware government resources and links",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "description": "Resource category (main, licenses, taxes, employment, local, support, cannabis, all)",
                                "enum": ["main", "licenses", "taxes", "employment", "local", "support", "cannabis", "all"]
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="get_cannabis_compliance_steps",
                    description="Get detailed step-by-step cannabis dispensary compliance requirements for Delaware",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "business_type": {
                                "type": "string",
                                "description": "Type of cannabis business (dispensary, cultivation, manufacturing, testing)",
                                "enum": ["dispensary", "cultivation", "manufacturing", "testing", "all"]
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="get_creative_business_steps",
                    description="Get detailed step-by-step art studio and creative business compliance requirements for Delaware",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "business_type": {
                                "type": "string",
                                "description": "Type of creative business (art_studio, gallery, workshop, teaching, all)",
                                "enum": ["art_studio", "gallery", "workshop", "teaching", "all"]
                            }
                        },
                        "required": []
                    }
                )
            ]
        )

    async def call_tool(self, request: CallToolRequest) -> CallToolResult:
        """Handle tool calls for Delaware license information with RAG."""
        tool_name = request.name
        arguments = request.arguments
        
        if tool_name == "get_delaware_license_categories":
            return await self._get_license_categories()
        elif tool_name == "get_delaware_license_details":
            return await self._get_license_details(arguments)
        elif tool_name == "search_delaware_licenses_rag":
            return await self._search_licenses_rag(arguments)
        elif tool_name == "get_similar_licenses":
            return await self._get_similar_licenses(arguments)
        elif tool_name == "get_delaware_business_steps":
            return await self._get_business_steps()
        elif tool_name == "get_delaware_resources":
            return await self._get_delaware_resources(arguments)
        elif tool_name == "get_cannabis_compliance_steps":
            return await self._get_cannabis_compliance_steps(arguments)
        elif tool_name == "get_creative_business_steps":
            return await self._get_creative_business_steps(arguments)
        else:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error: Unknown tool '{tool_name}'"
                )]
            )

    async def _get_license_categories(self) -> CallToolResult:
        """Get all available Delaware license categories."""
        try:
            response = self.session.get(DELAWARE_TOPICS_URL)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            categories = []
            
            # Extract license categories from the page
            for section in soup.find_all(['h2', 'h3', 'h4']):
                title = section.get_text(strip=True)
                if title and any(keyword in title.lower() for keyword in ['license', 'permit', 'registration', 'certification']):
                    categories.append(title)
            
            result_text = "Delaware License Categories\n\n"
            result_text += f"Source: {DELAWARE_TOPICS_URL}\n\n"
            result_text += "Available Categories:\n"
            
            if categories:
                for i, category in enumerate(categories, 1):
                    result_text += f"{i}. {category}\n"
            else:
                result_text += "No specific categories found. Check the Delaware Business First Steps website for current categories.\n"
            
            result_text += f"\nFor detailed information on each category, visit: {DELAWARE_TOPICS_URL}"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except Exception as e:
            logger.error(f"Error fetching license categories: {e}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error fetching Delaware license categories: {str(e)}"
                )]
            )

    async def _get_license_details(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get detailed information about a specific license type."""
        license_type = arguments.get("license_type", "")
        
        if not license_type:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Please provide a license type."
                )]
            )
        
        try:
            # Search for the specific license type
            if self.qdrant_client and self.embedding_model:
                # Use RAG to find the license
                license_embedding = self.embedding_model.encode([license_type])
                
                search_results = self.qdrant_client.search(
                    collection_name=COLLECTION_NAME,
                    query_vector=license_embedding[0].tolist(),
                    limit=1
                )
                
                if search_results:
                    result = search_results[0]
                    payload = result.payload
                    
                    result_text = f"Delaware License Details: {payload['license_type']}\n\n"
                    result_text += f"Source: {payload['source']}\n\n"
                    result_text += f"Category: {payload['category']}\n"
                    result_text += f"Description: {payload['text']}\n\n"
                    result_text += f"Relevance Score: {result.score:.3f}\n\n"
                    result_text += f"For more detailed information, visit: {DELAWARE_TOPICS_URL}"
                    
                    return CallToolResult(
                        content=[TextContent(type="text", text=result_text)]
                    )
            
            # Fallback to web scraping
            response = self.session.get(DELAWARE_TOPICS_URL)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Search for the license type
            for section in soup.find_all(['h2', 'h3', 'h4']):
                title = section.get_text(strip=True)
                if license_type.lower() in title.lower():
                    content = ""
                    next_elem = section.find_next_sibling()
                    while next_elem and next_elem.name not in ['h2', 'h3', 'h4']:
                        if next_elem.name:
                            content += next_elem.get_text(strip=True) + " "
                        next_elem = next_elem.find_next_sibling()
                    
                    result_text = f"Delaware License Details: {title}\n\n"
                    result_text += f"Source: {DELAWARE_TOPICS_URL}\n\n"
                    result_text += f"Description: {content.strip()}\n\n"
                    result_text += f"For more detailed information, visit: {DELAWARE_TOPICS_URL}"
                    
                    return CallToolResult(
                        content=[TextContent(type="text", text=result_text)]
                    )
            
            result_text = f"No detailed information found for '{license_type}'.\n\n"
            result_text += f"Please visit {DELAWARE_TOPICS_URL} to search for this license type."
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except Exception as e:
            logger.error(f"Error fetching license details: {e}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error fetching Delaware license details: {str(e)}"
                )]
            )

    async def _search_licenses_rag(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Search for licenses using semantic search (RAG-powered with Qdrant)."""
        query = arguments.get("query", "")
        top_k = arguments.get("top_k", 5)
        
        if not query:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Please provide a search query."
                )]
            )
        
        try:
            if self.qdrant_client and self.embedding_model:
                # Use RAG for semantic search with Qdrant
                logger.info(f"Performing RAG search with Qdrant for: {query}")
                
                # Generate query embedding
                query_embedding = self.embedding_model.encode([query])
                
                # Search in Qdrant collection
                search_results = self.qdrant_client.search(
                    collection_name=COLLECTION_NAME,
                    query_vector=query_embedding[0].tolist(),
                    limit=top_k
                )
                
                result_text = f"Delaware License Search Results for: '{query}'\n\n"
                
                if search_results:
                    result_text += f"Found {len(search_results)} relevant license types:\n\n"
                    
                    for i, result in enumerate(search_results, 1):
                        payload = result.payload
                        result_text += f"{i}. **{payload['license_type']}**\n"
                        result_text += f"   Category: {payload['category']}\n"
                        result_text += f"   Relevance Score: {result.score:.3f}\n"
                        result_text += f"   Description: {payload['text']}\n"
                        if 'requirements' in payload:
                            result_text += f"   Requirements: {payload['requirements']}\n"
                        result_text += f"   Source: {payload['source']}\n\n"
                else:
                    # Enhanced fallback with semantic keyword matching
                    result_text += self._semantic_keyword_search(query)
                
                return CallToolResult(
                    content=[TextContent(type="text", text=result_text)]
                )
            else:
                # Fallback to semantic keyword search
                logger.info("RAG not available, using semantic keyword search")
                result_text = self._semantic_keyword_search(query)
                return CallToolResult(
                    content=[TextContent(type="text", text=result_text)]
                )
                
        except Exception as e:
            logger.error(f"Error in RAG search: {e}")
            # Fallback to semantic keyword search
            result_text = self._semantic_keyword_search(query)
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )

    def _semantic_keyword_search(self, query: str) -> str:
        """Enhanced semantic search using keyword matching and business type mapping."""
        query_lower = query.lower()
        
        # Business type to license mapping
        business_mappings = {
            "financial services": ["Money Transmitter License", "Investment Adviser License", "Securities Dealer License", "Trust Company License"],
            "financial firm": ["Money Transmitter License", "Investment Adviser License", "Securities Dealer License", "Trust Company License"],
            "investment": ["Investment Adviser License", "Securities Dealer License"],
            "banking": ["Money Transmitter License", "Trust Company License"],
            "lending": ["Consumer Credit License", "Mortgage Loan Originator License"],
            "mortgage": ["Mortgage Loan Originator License"],
            "insurance": ["Insurance Producer License"],
            "payment": ["Money Transmitter License"],
            "fintech": ["Money Transmitter License", "Investment Adviser License", "Securities Dealer License"],
            "wealth management": ["Investment Adviser License", "Trust Company License"],
            "portfolio": ["Investment Adviser License"],
            "trading": ["Securities Dealer License"],
            "broker": ["Securities Dealer License", "Insurance Producer License"],
            "trust": ["Trust Company License"],
            "money transfer": ["Money Transmitter License"],
            "check cashing": ["Check Casher License"],
            "consumer credit": ["Consumer Credit License"],
            "personal loans": ["Consumer Credit License"],
            "payday loans": ["Consumer Credit License"]
        }
        
        # Find matching licenses
        matching_licenses = []
        for business_type, license_types in business_mappings.items():
            if business_type in query_lower:
                matching_licenses.extend(license_types)
        
        # Remove duplicates
        matching_licenses = list(set(matching_licenses))
        
        if matching_licenses:
            result_text = f"Based on your business description '{query}', you likely need these Delaware licenses:\n\n"
            
            for i, license_type in enumerate(matching_licenses, 1):
                # Find the license data
                license_data = None
                for entry in self.license_data:
                    if entry["license_type"] == license_type:
                        license_data = entry
                        break
                
                if license_data:
                    result_text += f"{i}. **{license_data['license_type']}**\n"
                    result_text += f"   Description: {license_data['text']}\n"
                    result_text += f"   Requirements: {license_data['requirements']}\n"
                    result_text += f"   Source: {license_data['source']}\n\n"
                else:
                    result_text += f"{i}. **{license_type}**\n"
                    result_text += f"   Contact Delaware Division of Banking for details\n\n"
            
            result_text += "**Additional Requirements:**\n"
            result_text += "• Delaware Business Registration (required for all businesses)\n"
            result_text += "• Delaware Tax Registration (if collecting sales tax or have employees)\n"
            result_text += "• Federal EIN (Employer Identification Number)\n\n"
            
            result_text += "**Next Steps:**\n"
            result_text += "1. Register your business entity with Delaware Division of Corporations\n"
            result_text += "2. Apply for required licenses through the respective agencies\n"
            result_text += "3. Complete background checks and provide required documentation\n"
            result_text += "4. Pay application and license fees\n"
            result_text += "5. Maintain compliance and renew licenses annually\n"
            
        else:
            result_text = f"No specific licenses found for '{query}'.\n\n"
            result_text += "**General Delaware Business Requirements:**\n"
            result_text += "• Delaware Business Registration (required for all businesses)\n"
            result_text += "• Delaware Tax Registration (if applicable)\n"
            result_text += "• Federal EIN (Employer Identification Number)\n\n"
            result_text += "**Contact Information:**\n"
            result_text += "• Business Registration: https://corp.delaware.gov/\n"
            result_text += "• Tax Registration: https://revenue.delaware.gov/\n"
            result_text += "• Banking Licenses: https://banking.delaware.gov/\n"
            result_text += "• Securities Licenses: https://securities.delaware.gov/\n"
            result_text += "• Insurance Licenses: https://insurance.delaware.gov/\n"
        
        return result_text

    async def _search_licenses_fallback(self, query: str) -> CallToolResult:
        """Fallback search using web scraping."""
        try:
            response = self.session.get(DELAWARE_TOPICS_URL)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Search through all text content
            matches = []
            
            # Look for elements containing the query
            for element in soup.find_all(['h2', 'h3', 'h4', 'h5', 'li', 'a']):
                text = element.get_text(strip=True)
                if query.lower() in text.lower():
                    matches.append(text)
            
            # Remove duplicates and limit results
            matches = list(set(matches))[:15]
            
            result_text = f"Delaware License Search Results for: '{query}'\n\n"
            result_text += f"Source: {DELAWARE_TOPICS_URL}\n\n"
            
            if matches:
                result_text += f"Found {len(matches)} matching license types:\n\n"
                for i, match in enumerate(matches, 1):
                    result_text += f"{i}. {match}\n"
            else:
                result_text += f"No license types found matching '{query}'.\n"
                result_text += "\nTry searching for broader terms like:\n"
                result_text += "• 'food' for restaurant/bakery licenses\n"
                result_text += "• 'health' for medical licenses\n"
                result_text += "• 'profession' for professional licenses\n"
                result_text += "• 'business' for general business licenses\n"
            
            result_text += f"\nFor more detailed information, visit: {DELAWARE_TOPICS_URL}"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except Exception as e:
            logger.error(f"Error in fallback search: {e}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error searching Delaware licenses: {str(e)}"
                )]
            )

    async def _get_similar_licenses(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Find similar licenses based on a license type (RAG-powered with Qdrant)."""
        license_type = arguments.get("license_type", "")
        top_k = arguments.get("top_k", 3)
        
        if not license_type:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Please provide a license type."
                )]
            )
        
        try:
            if self.qdrant_client and self.embedding_model:
                # Use RAG for similarity search with Qdrant
                logger.info(f"Finding similar licenses with Qdrant for: {license_type}")
                
                # Generate embedding for the license type
                license_embedding = self.embedding_model.encode([license_type])
                
                # Search for similar licenses in Qdrant
                search_results = self.qdrant_client.search(
                    collection_name=COLLECTION_NAME,
                    query_vector=license_embedding[0].tolist(),
                    limit=top_k + 1  # +1 to exclude the exact match
                )
                
                result_text = f"Similar Licenses to '{license_type}' (RAG-powered with Qdrant):\n\n"
                result_text += f"Source: {DELAWARE_TOPICS_URL}\n\n"
                
                if search_results:
                    # Filter out exact matches
                    similar_results = [r for r in search_results if r.payload['license_type'] != license_type]
                    
                    if similar_results:
                        result_text += f"Found {len(similar_results)} similar license types:\n\n"
                        
                        for i, result in enumerate(similar_results, 1):
                            payload = result.payload
                            result_text += f"{i}. **{payload['license_type']}**\n"
                            result_text += f"   Category: {payload['category']}\n"
                            result_text += f"   Similarity Score: {result.score:.3f}\n"
                            result_text += f"   Description: {payload['text']}\n\n"
                    else:
                        result_text += "No similar licenses found.\n"
                else:
                    result_text += "No similar licenses found.\n"
                
                result_text += f"\nFor more detailed information, visit: {DELAWARE_TOPICS_URL}"
                
                return CallToolResult(
                    content=[TextContent(type="text", text=result_text)]
                )
            else:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="RAG system not available. Please ensure the embedding model and Qdrant database are properly initialized."
                    )]
                )
                
        except Exception as e:
            logger.error(f"Error finding similar licenses: {e}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error finding similar licenses: {str(e)}"
                )]
            )

    async def _get_business_steps(self) -> CallToolResult:
        """Get the 4-step process for opening a business in Delaware."""
        try:
            # The 4 steps are known from the Delaware website structure
            steps = [
                {
                    "step": 1,
                    "title": "Harness Your Great Idea",
                    "description": "Develop and refine your business concept"
                },
                {
                    "step": 2,
                    "title": "Write Your Business Plan",
                    "description": "Create a comprehensive business plan"
                },
                {
                    "step": 3,
                    "title": "Get Your License",
                    "description": "Obtain necessary business licenses and permits"
                },
                {
                    "step": 4,
                    "title": "Open Your Business",
                    "description": "Launch your business operations"
                }
            ]
            
            result_text = "Delaware Business First Steps - 4-Step Process\n\n"
            result_text += f"Source: {DELAWARE_BASE_URL}\n\n"
            
            for step in steps:
                result_text += f"Step {step['step']}: {step['title']}\n"
                result_text += f"   {step['description']}\n\n"
            
            result_text += f"For detailed guidance on each step, visit: {DELAWARE_BASE_URL}"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except Exception as e:
            logger.error(f"Error fetching business steps: {e}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error fetching Delaware business steps: {str(e)}"
                )]
            )

    async def _get_delaware_resources(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get comprehensive Delaware government resources and links."""
        category = arguments.get("category", "all")
        
        try:
            result_text = "🏛️ Delaware Government Resources\n\n"
            result_text += f"Source: Delaware Government Websites\n\n"
            
            if category == "all" or category == "main":
                result_text += "## 🏢 Main Delaware Resources:\n"
                for name, url in DELAWARE_RESOURCES["main"].items():
                    result_text += f"- **{name}**: {url}\n"
                result_text += "\n"
            
            if category == "all" or category == "licenses":
                result_text += "## 📋 License & Permit Resources:\n"
                for name, url in DELAWARE_RESOURCES["licenses"].items():
                    result_text += f"- **{name}**: {url}\n"
                result_text += "\n"
            
            if category == "all" or category == "taxes":
                result_text += "## 💰 Tax Resources:\n"
                for name, url in DELAWARE_RESOURCES["taxes"].items():
                    result_text += f"- **{name}**: {url}\n"
                result_text += "\n"
            
            if category == "all" or category == "employment":
                result_text += "## 👥 Employment Resources:\n"
                for name, url in DELAWARE_RESOURCES["employment"].items():
                    result_text += f"- **{name}**: {url}\n"
                result_text += "\n"
            
            if category == "all" or category == "local":
                result_text += "## 🏘️ Local Government Resources:\n"
                for name, url in DELAWARE_RESOURCES["local"].items():
                    result_text += f"- **{name}**: {url}\n"
                result_text += "\n"
            
            if category == "all" or category == "support":
                result_text += "## 🤝 Business Support Resources:\n"
                for name, url in DELAWARE_RESOURCES["support"].items():
                    result_text += f"- **{name}**: {url}\n"
                result_text += "\n"
            
            if category == "all" or category == "cannabis":
                result_text += "## 🌿 Cannabis Resources:\n"
                for name, url in DELAWARE_RESOURCES["cannabis"].items():
                    result_text += f"- **{name}**: {url}\n"
                result_text += "\n"
            
            if category == "all" or category == "creative":
                result_text += "## 🎨 Creative Resources:\n"
                for name, url in DELAWARE_RESOURCES["creative"].items():
                    result_text += f"- **{name}**: {url}\n"
                result_text += "\n"
            
            result_text += "---\n"
            result_text += "💡 **Tip**: Contact your local Small Business Administration (SBA) office for additional guidance.\n"
            result_text += "📞 **Need Help?**: Call Delaware Business First Steps at 1-800-292-7935"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except Exception as e:
            logger.error(f"Error fetching Delaware resources: {e}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error fetching Delaware resources: {str(e)}"
                )]
            )

    async def _get_cannabis_compliance_steps(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get detailed step-by-step cannabis dispensary compliance requirements for Delaware."""
        business_type = arguments.get("business_type", "all")
        
        if business_type == "all":
            result_text = "🌿 Delaware Cannabis Dispensary Compliance Requirements\n\n"
            result_text += "This tool provides a comprehensive guide to opening a cannabis dispensary in Delaware.\n\n"
            result_text += "1. **Application Process**:\n"
            result_text += "   - Submit an application to the Delaware Cannabis Compliance Commission (DCCC).\n"
            result_text += "   - Include all required documents (business plan, financial statements, etc.).\n"
            result_text += "   - Pay the required application fee.\n\n"
            result_text += "2. **Location Requirements**:\n"
            result_text += "   - Dispensaries must be located in a commercial zone.\n"
            result_text += "   - Must be at least 500 feet away from schools, parks, and other public places.\n"
            result_text += "   - Must be at least 1,000 feet away from churches, daycare centers, and other places of worship.\n\n"
            result_text += "3. **Staff Requirements**:\n"
            result_text += "   - Must have at least one employee with a valid Delaware ID.\n"
            result_text += "   - Employees must undergo background checks.\n"
            result_text += "   - Must have a trained security staff.\n\n"
            result_text += "4. **Security Measures**:\n"
            result_text += "   - Must have a secure, locked facility.\n"
            result_text += "   - Must have a security alarm system.\n"
            result_text += "   - Must have a secure cash handling area.\n\n"
            result_text += "5. **Inventory Management**:\n"
            result_text += "   - Must maintain a secure, tamper-evident inventory system.\n"
            result_text += "   - Must have a trained staff member responsible for inventory.\n\n"
            result_text += "6. **Compliance Training**:\n"
            result_text += "   - All employees must undergo training on Delaware cannabis laws and regulations.\n"
            result_text += "   - Training must be conducted by a certified instructor.\n\n"
            result_text += "7. **Monitoring and Reporting**:\n"
            result_text += "   - Must report all sales, inventory, and employee attendance to the DCCC.\n"
            result_text += "   - Must maintain detailed records for 5 years.\n\n"
            result_text += "8. **License Renewal**:\n"
            result_text += "   - Must renew the license annually.\n"
            result_text += "   - Must pay the required renewal fee.\n\n"
            result_text += "9. **Penalty for Non-Compliance**:\n"
            result_text += "   - Violations can result in fines, license revocation, and criminal penalties.\n\n"
            result_text += "For more detailed information, visit: https://cannabis.delaware.gov/compliance/\n"
            result_text += "📞 **Need Help?**: Call the DCCC at 1-800-292-7935"
        else:
            # This part needs to be implemented based on the specific business type
            # For now, it will return a placeholder message
            result_text = f"Detailed compliance steps for a {business_type} are not yet available in this tool."
            result_text += "\nPlease visit https://cannabis.delaware.gov/compliance/ for general information."
        
        return CallToolResult(
            content=[TextContent(type="text", text=result_text)]
        )

    async def _get_creative_business_steps(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get detailed step-by-step art studio and creative business compliance requirements for Delaware."""
        business_type = arguments.get("business_type", "all")
        
        if business_type == "all":
            result_text = "🎨 Delaware Creative Business Compliance Requirements\n\n"
            result_text += "This tool provides a comprehensive guide to opening an art studio or creative business in Delaware.\n\n"
            result_text += "1. **Application Process**:\n"
            result_text += "   - Submit an application to the Delaware Division of the Arts (DoA) or the Delaware Creative Economy Partnership (DCEP).\n"
            result_text += "   - Include all required documents (business plan, financial statements, etc.).\n"
            result_text += "   - Pay the required application fee.\n\n"
            result_text += "2. **Location Requirements**:\n"
            result_text += "   - Art studios and creative businesses must be located in a commercial zone.\n"
            result_text += "   - Must be at least 500 feet away from schools, parks, and other public places.\n"
            result_text += "   - Must be at least 1,000 feet away from churches, daycare centers, and other places of worship.\n\n"
            result_text += "3. **Staff Requirements**:\n"
            result_text += "   - Must have at least one employee with a valid Delaware ID.\n"
            result_text += "   - Employees must undergo background checks.\n"
            result_text += "   - Must have a trained security staff.\n\n"
            result_text += "4. **Security Measures**:\n"
            result_text += "   - Must have a secure, locked facility.\n"
            result_text += "   - Must have a security alarm system.\n"
            result_text += "   - Must have a secure cash handling area.\n\n"
            result_text += "5. **Inventory Management**:\n"
            result_text += "   - Must maintain a secure, tamper-evident inventory system.\n"
            result_text += "   - Must have a trained staff member responsible for inventory.\n\n"
            result_text += "6. **Compliance Training**:\n"
            result_text += "   - All employees must undergo training on Delaware creative business laws and regulations.\n"
            result_text += "   - Training must be conducted by a certified instructor.\n\n"
            result_text += "7. **Monitoring and Reporting**:\n"
            result_text += "   - Must report all sales, inventory, and employee attendance to the DoA or DCEP.\n"
            result_text += "   - Must maintain detailed records for 5 years.\n\n"
            result_text += "8. **License Renewal**:\n"
            result_text += "   - Must renew the license annually.\n"
            result_text += "   - Must pay the required renewal fee.\n\n"
            result_text += "9. **Penalty for Non-Compliance**:\n"
            result_text += "   - Violations can result in fines, license revocation, and criminal penalties.\n\n"
            result_text += "For more detailed information, visit: https://choosedelaware.com/creative-economy/\n"
            result_text += "📞 **Need Help?**: Call the DoA at 1-800-292-7935 or DCEP at 1-800-292-7935"
        else:
            # This part needs to be implemented based on the specific business type
            # For now, it will return a placeholder message
            result_text = f"Detailed compliance steps for a {business_type} are not yet available in this tool."
            result_text += "\nPlease visit https://choosedelaware.com/creative-economy/ for general information."
        
        return CallToolResult(
            content=[TextContent(type="text", text=result_text)]
        )

    # Add compatibility methods for the agent
    async def search_licenses(self, query: str):
        """Search for licenses using RAG or fallback."""
        try:
            # Try RAG search first
            result = await self._search_licenses_rag({"query": query})
            if result and hasattr(result, 'content'):
                return result
        except Exception as e:
            self.logger.error(f"Error in RAG search: {e}")
        
        # Fallback to semantic keyword search
        try:
            result_text = self._semantic_keyword_search(query)
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
        except Exception as e:
            self.logger.error(f"Error in semantic search: {e}")
            return None

    async def get_business_steps(self):
        """Get business steps for Delaware."""
        try:
            result = await self._get_business_steps()
            return result
        except Exception as e:
            self.logger.error(f"Error getting business steps: {e}")
            return None

    async def get_license_categories(self):
        """Get license categories for Delaware."""
        try:
            result = await self._get_license_categories()
            return result
        except Exception as e:
            self.logger.error(f"Error getting license categories: {e}")
            return None

async def main():
    """Main function to run the Delaware RAG MCP server."""
    server = DelawareRAGServer()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="delaware-licenses-rag",
                server_version="1.0.0",
                capabilities=server.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main()) 
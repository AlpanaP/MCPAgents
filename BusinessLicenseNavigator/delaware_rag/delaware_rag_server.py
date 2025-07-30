#!/usr/bin/env python3
"""
Delaware Business License MCP Server with RAG
Provides tools to access Delaware business license information with vector-based retrieval using Qdrant
"""

import asyncio
import json
import logging
import os
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
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
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
            response = self.session.get(DELAWARE_TOPICS_URL)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            license_entries = []
            
            # Extract license information from the page
            for section in soup.find_all(['h2', 'h3', 'h4', 'h5']):
                title = section.get_text(strip=True)
                if title and any(keyword in title.lower() for keyword in ['license', 'permit', 'registration', 'certification']):
                    # Get the content following this section
                    content = ""
                    next_elem = section.find_next_sibling()
                    while next_elem and next_elem.name not in ['h2', 'h3', 'h4', 'h5']:
                        if next_elem.name:
                            content += next_elem.get_text(strip=True) + " "
                        next_elem = next_elem.find_next_sibling()
                    
                    if content.strip():
                        entry = {
                            "text": f"{title}: {content.strip()}",
                            "category": "Business Licenses",
                            "license_type": title,
                            "source": DELAWARE_TOPICS_URL
                        }
                        license_entries.append(entry)
            
            # Add to Qdrant collection
            if license_entries and self.qdrant_client:
                texts = [entry["text"] for entry in license_entries]
                metadatas = [{"category": entry["category"], "license_type": entry["license_type"], "source": entry["source"]} for entry in license_entries]
                
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
                            "source": metadata["source"]
                        }
                    )
                    points.append(point)
                
                # Add points to collection
                self.qdrant_client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=points
                )
                
                logger.info(f"Added {len(license_entries)} license entries to Qdrant collection")
                self.license_data = license_entries
                
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
                                "description": "Resource category (main, licenses, taxes, employment, local, support, all)",
                                "enum": ["main", "licenses", "taxes", "employment", "local", "support", "all"]
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
        else:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Unknown tool: {tool_name}"
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
                
                result_text = f"Delaware License Search Results (RAG-powered with Qdrant) for: '{query}'\n\n"
                result_text += f"Source: {DELAWARE_TOPICS_URL}\n\n"
                
                if search_results:
                    result_text += f"Found {len(search_results)} relevant license types:\n\n"
                    
                    for i, result in enumerate(search_results, 1):
                        payload = result.payload
                        result_text += f"{i}. **{payload['license_type']}**\n"
                        result_text += f"   Category: {payload['category']}\n"
                        result_text += f"   Relevance Score: {result.score:.3f}\n"
                        result_text += f"   Description: {payload['text']}\n\n"
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
            else:
                # Fallback to web scraping
                logger.info("RAG not available, falling back to web scraping")
                return await self._search_licenses_fallback(query)
                
        except Exception as e:
            logger.error(f"Error in RAG search: {e}")
            # Fallback to web scraping
            return await self._search_licenses_fallback(query)

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
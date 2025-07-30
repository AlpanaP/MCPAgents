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
            
            # Extract license data
            license_entries = []
            
            # Find all category sections
            for element in soup.find_all(['h2', 'h3', 'h4']):
                category = element.get_text(strip=True)
                if len(category) > 2 and len(category) < 100:
                    # Get license types in this category
                    parent = element.find_parent()
                    if parent:
                        license_types = []
                        for item in parent.find_all(['li', 'a']):
                            license_text = item.get_text(strip=True)
                            if license_text and len(license_text) > 3:
                                license_types.append(license_text)
                        
                        # Create entries for each license type
                        for license_type in license_types:
                            entry = {
                                "category": category,
                                "license_type": license_type,
                                "text": f"Category: {category}. License Type: {license_type}",
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
        tools = [
            Tool(
                name="get_delaware_license_categories",
                description="Get all available license categories from Delaware Business First Steps",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="get_delaware_license_details",
                description="Get detailed information about a specific license type from Delaware",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "License category (e.g., 'Food', 'Health', 'Professions')"
                        },
                        "license_type": {
                            "type": "string",
                            "description": "Specific license type within the category"
                        }
                    },
                    "required": ["category"]
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
                            "description": "Number of top results to return (default: 5)"
                        }
                    },
                    "required": ["query"]
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
                            "description": "Number of similar results to return (default: 3)"
                        }
                    },
                    "required": ["license_type"]
                }
            )
        ]
        return ListToolsResult(tools=tools)

    async def call_tool(self, request: CallToolRequest) -> CallToolResult:
        """Handle tool calls for Delaware license information with RAG."""
        try:
            if request.name == "get_delaware_license_categories":
                return await self._get_license_categories()
            elif request.name == "get_delaware_license_details":
                return await self._get_license_details(request.arguments)
            elif request.name == "search_delaware_licenses_rag":
                return await self._search_licenses_rag(request.arguments)
            elif request.name == "get_delaware_business_steps":
                return await self._get_business_steps()
            elif request.name == "get_similar_licenses":
                return await self._get_similar_licenses(request.arguments)
            else:
                raise ValueError(f"Unknown tool: {request.name}")
        except Exception as e:
            logger.error(f"Error in tool call {request.name}: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")]
            )

    async def _get_license_categories(self) -> CallToolResult:
        """Get all available license categories from Delaware."""
        try:
            response = self.session.get(DELAWARE_TOPICS_URL)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the main content area
            content = soup.find('div', {'id': 'content'}) or soup
            
            # Extract categories from the page
            categories = []
            
            # Look for category headings
            category_elements = content.find_all(['h2', 'h3', 'h4'])
            
            for element in category_elements:
                text = element.get_text(strip=True)
                if text and len(text) > 2 and len(text) < 100:
                    categories.append(text)
            
            # Remove duplicates and clean up
            categories = list(set([cat.strip() for cat in categories if cat.strip()]))
            
            result_text = f"Delaware Business License Categories:\n\n"
            result_text += f"Source: {DELAWARE_TOPICS_URL}\n"
            result_text += f"Total Categories: {len(categories)}\n\n"
            result_text += f"Available Categories:\n"
            result_text += "\n".join([f"• {cat}" for cat in categories])
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error fetching Delaware license categories: {str(e)}"
                )]
            )

    async def _get_license_details(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get detailed information about a specific license type."""
        category = arguments.get("category", "").strip()
        license_type = arguments.get("license_type", "").strip()
        
        try:
            response = self.session.get(DELAWARE_TOPICS_URL)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the section for the specified category
            category_section = None
            for element in soup.find_all(['h2', 'h3', 'h4']):
                if element.get_text(strip=True).lower() == category.lower():
                    category_section = element.find_parent()
                    break
            
            if not category_section:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Category '{category}' not found. Available categories can be retrieved using get_delaware_license_categories."
                    )]
                )
            
            # Extract license types within the category
            license_types = []
            for item in category_section.find_all(['li', 'a']):
                text = item.get_text(strip=True)
                if text and len(text) > 3 and len(text) < 200:
                    license_types.append(text)
            
            result_text = f"Delaware License Details for Category: {category}\n\n"
            result_text += f"Source: {DELAWARE_TOPICS_URL}\n\n"
            
            if license_types:
                result_text += f"License Types in {category}:\n"
                for i, license_type in enumerate(license_types[:20], 1):  # Limit to first 20
                    result_text += f"{i}. {license_type}\n"
                
                if len(license_types) > 20:
                    result_text += f"\n... and {len(license_types) - 20} more license types.\n"
            else:
                result_text += "No specific license types found for this category.\n"
            
            result_text += f"\nFor more detailed information, visit: {DELAWARE_TOPICS_URL}"
            
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
        query = arguments.get("query", "").strip()
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
        license_type = arguments.get("license_type", "").strip()
        top_k = arguments.get("top_k", 3)
        
        if not license_type:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Please provide a license type to find similar ones for."
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
#!/usr/bin/env python3
"""
Delaware Business License MCP Server
Provides tools to access Delaware business license information from firststeps.delaware.gov
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

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

class DelawareLicenseServer:
    def __init__(self):
        self.server = Server("delaware-licenses")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Register tools
        self.server.list_tools = self.list_tools
        self.server.call_tool = self.call_tool

    async def list_tools(self, request: ListToolsRequest) -> ListToolsResult:
        """List available tools for Delaware license information."""
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
                name="search_delaware_licenses",
                description="Search for licenses by keyword or business type",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (e.g., 'restaurant', 'bakery', 'consulting')"
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
            )
        ]
        return ListToolsResult(tools=tools)

    async def call_tool(self, request: CallToolRequest) -> CallToolResult:
        """Handle tool calls for Delaware license information."""
        try:
            if request.name == "get_delaware_license_categories":
                return await self._get_license_categories()
            elif request.name == "get_delaware_license_details":
                return await self._get_license_details(request.arguments)
            elif request.name == "search_delaware_licenses":
                return await self._search_licenses(request.arguments)
            elif request.name == "get_delaware_business_steps":
                return await self._get_business_steps()
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
            
            result = {
                "categories": categories,
                "source": "Delaware Business First Steps",
                "url": DELAWARE_TOPICS_URL,
                "total_categories": len(categories)
            }
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Delaware Business License Categories:\n\n" +
                         f"Source: {DELAWARE_TOPICS_URL}\n" +
                         f"Total Categories: {len(categories)}\n\n" +
                         f"Available Categories:\n" +
                         "\n".join([f"• {cat}" for cat in categories])
                )]
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

    async def _search_licenses(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Search for licenses by keyword or business type."""
        query = arguments.get("query", "").strip().lower()
        
        if not query:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Please provide a search query."
                )]
            )
        
        try:
            response = self.session.get(DELAWARE_TOPICS_URL)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Search through all text content
            matches = []
            
            # Look for elements containing the query
            for element in soup.find_all(['h2', 'h3', 'h4', 'h5', 'li', 'a']):
                text = element.get_text(strip=True)
                if query in text.lower():
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
            logger.error(f"Error searching licenses: {e}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error searching Delaware licenses: {str(e)}"
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
    """Main function to run the Delaware MCP server."""
    server = DelawareLicenseServer()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="delaware-licenses",
                server_version="1.0.0",
                capabilities=server.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main()) 
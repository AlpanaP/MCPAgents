"""
Template RAG Server for New States/Provinces.

This template provides a base structure for creating RAG servers for new states.
Customize the configuration, data sources, and business logic for your specific state.
"""

import logging
from typing import Optional, List, Dict, Any
from core.models.base_rag_server import BaseRAGServer, RAGConfig, SearchResult
from core.models.text_content import TextContent


class TemplateRAGServer(BaseRAGServer):
    """
    Template RAG Server for {STATE_NAME}.
    
    This server provides business license information for {STATE_NAME}.
    Customize the configuration and data sources for your specific state.
    """
    
    def __init__(self, config: RAGConfig):
        """Initialize the template RAG server."""
        super().__init__(config)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Customize these for your state
        self.state_code = "TEMPLATE"  # Change to your state code
        self.state_name = "Template State"  # Change to your state name
        
        # Initialize state-specific configuration
        self._init_state_config()
    
    def _init_state_config(self):
        """Initialize state-specific configuration."""
        # Customize these settings for your state
        self.data_sources = [
            "https://template-state.gov/business/",
            "https://template-state.gov/licenses/"
        ]
        
        self.license_categories = [
            "General Business License",
            "Industry-Specific License",
            "Professional License",
            "Local Business License"
        ]
        
        self.business_types = {
            "construction": {
                "keywords": ["construction", "contractor", "building"],
                "license_types": ["General Contractor", "Building Contractor"],
                "requirements": ["Background check", "Experience verification"],
                "fees": ["Application fee: $200-500", "License fee: $300-800"]
            },
            "food_service": {
                "keywords": ["restaurant", "food", "cafe", "catering"],
                "license_types": ["Food Service License", "Restaurant License"],
                "requirements": ["Food safety training", "Health inspection"],
                "fees": ["Application fee: $100-300", "License fee: $200-500"]
            }
        }
    
    async def search_licenses(self, query: str) -> Optional[SearchResult]:
        """
        Search for licenses based on the query.
        
        Args:
            query: Search query string
            
        Returns:
            SearchResult with license information
        """
        try:
            self.logger.info(f"Searching licenses for query: {query}")
            
            # Customize this search logic for your state
            search_results = await self._perform_search(query)
            
            if not search_results:
                return None
            
            # Format the results
            content = TextContent(
                text=self._format_search_results(search_results),
                source="template_rag_server",
                metadata={
                    "state": self.state_code,
                    "query": query,
                    "results_count": len(search_results)
                }
            )
            
            return SearchResult(
                content=content,
                relevance_score=0.8,  # Customize based on your relevance logic
                source="template_rag_server"
            )
            
        except Exception as e:
            self.logger.error(f"Error searching licenses: {e}")
            return None
    
    async def get_business_steps(self) -> Optional[SearchResult]:
        """
        Get business setup steps for the state.
        
        Returns:
            SearchResult with business setup steps
        """
        try:
            self.logger.info("Getting business setup steps")
            
            # Customize these steps for your state
            business_steps = [
                "1. Choose your business structure (LLC, Corporation, etc.)",
                "2. Register your business with the state",
                "3. Obtain necessary licenses and permits",
                "4. Set up tax accounts",
                "5. Get insurance coverage",
                "6. Set up business banking",
                "7. Comply with local regulations"
            ]
            
            content = TextContent(
                text="\n".join(business_steps),
                source="template_rag_server",
                metadata={
                    "state": self.state_code,
                    "type": "business_steps"
                }
            )
            
            return SearchResult(
                content=content,
                relevance_score=1.0,
                source="template_rag_server"
            )
            
        except Exception as e:
            self.logger.error(f"Error getting business steps: {e}")
            return None
    
    async def _perform_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform the actual search operation.
        
        Args:
            query: Search query
            
        Returns:
            List of search results
        """
        # Customize this search logic for your state
        # This is a placeholder implementation
        
        results = []
        
        # Example: Search based on business type
        for business_type, config in self.business_types.items():
            if any(keyword in query.lower() for keyword in config["keywords"]):
                results.append({
                    "business_type": business_type,
                    "license_types": config["license_types"],
                    "requirements": config["requirements"],
                    "fees": config["fees"]
                })
        
        return results
    
    def _format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results into readable text.
        
        Args:
            results: List of search results
            
        Returns:
            Formatted text
        """
        if not results:
            return "No license information found for your query."
        
        formatted_text = f"# {self.state_name} Business License Information\n\n"
        
        for result in results:
            business_type = result["business_type"].title()
            formatted_text += f"## {business_type} Licenses\n\n"
            
            formatted_text += "**License Types:**\n"
            for license_type in result["license_types"]:
                formatted_text += f"- {license_type}\n"
            
            formatted_text += "\n**Requirements:**\n"
            for requirement in result["requirements"]:
                formatted_text += f"- {requirement}\n"
            
            formatted_text += "\n**Fees:**\n"
            for fee in result["fees"]:
                formatted_text += f"- {fee}\n"
            
            formatted_text += "\n---\n\n"
        
        return formatted_text
    
    def get_state_info(self) -> Dict[str, Any]:
        """Get information about this state's RAG server."""
        return {
            "state_code": self.state_code,
            "state_name": self.state_name,
            "data_sources": self.data_sources,
            "license_categories": self.license_categories,
            "business_types": list(self.business_types.keys())
        } 
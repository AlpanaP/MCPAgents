"""
Enhanced Agent for Business License Navigator

This module provides an enhanced agent that combines intelligent semantic search
with MCP server capabilities for real-time information retrieval.
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional, Any

from .core.intelligent_semantic_search import intelligent_semantic_search
from .core.ai_services import sanitize_input, call_gemini, call_ollama
from .core.prompt_builder import build_main_prompt

logger = logging.getLogger(__name__)


class EnhancedBusinessLicenseAgent:
    """Enhanced agent that combines intelligent semantic search with MCP capabilities."""
    
    def __init__(self, mcp_agent=None):
        self.mcp_agent = mcp_agent
        self.conversation_history = []
    
    async def run_enhanced_agent(self, user_input: str, ai_source: str = "gemini") -> str:
        """Run the enhanced agent with intelligent semantic search and MCP integration."""
        
        try:
            # Sanitize input
            sanitized_input = sanitize_input(user_input)
            
            # Detect state from query
            state_code = self._extract_state_code(sanitized_input)
            
            # Get intelligent semantic search results
            intelligent_results = await intelligent_semantic_search.create_intelligent_augmented_prompt(
                sanitized_input, 
                state_code=state_code
            )
            
            # If it's a configured state and MCP is available, fetch additional data
            mcp_data = None
            if intelligent_results['is_configured_state'] and self.mcp_agent:
                mcp_data = await self._fetch_mcp_data(sanitized_input, state_code)
            
            # Build enhanced prompt with all available data
            enhanced_prompt = self._build_enhanced_prompt(
                sanitized_input, 
                intelligent_results, 
                mcp_data, 
                state_code
            )
            
            # Call AI model
            if ai_source.lower() == "gemini":
                # Get API key from environment
                api_key = os.getenv("GEMINI_API_KEY")
                if api_key:
                    response = call_gemini(enhanced_prompt, api_key)
                else:
                    response = "ERROR: GEMINI_API_KEY not found. Please set your Gemini API key."
            elif ai_source.lower() == "ollama":
                response = call_ollama("llama3.1", enhanced_prompt)
            else:
                # Default to Gemini
                api_key = os.getenv("GEMINI_API_KEY")
                if api_key:
                    response = call_gemini(enhanced_prompt, api_key)
                else:
                    response = "ERROR: GEMINI_API_KEY not found. Please set your Gemini API key."
            
            # Add to conversation history
            self.conversation_history.append({
                "user_input": user_input,
                "response": response,
                "intelligent_results": intelligent_results,
                "mcp_data": mcp_data,
                "state_code": state_code
            })
            
            return response
            
        except Exception as e:
            error_msg = f"Error in enhanced agent: {e}"
            logger.error(error_msg)
            return error_msg
    
    def _extract_state_code(self, query: str) -> Optional[str]:
        """Extract state code from query."""
        query_lower = query.lower()
        
        if "florida" in query_lower or "fl" in query_lower:
            return "FL"
        elif "delaware" in query_lower or "de" in query_lower:
            return "DE"
        else:
            return None
    
    async def _fetch_mcp_data(self, query: str, state_code: str) -> Optional[Dict[str, Any]]:
        """Fetch additional data using MCP servers."""
        if not self.mcp_agent:
            return None
        
        try:
            if state_code == "FL":
                return await self._fetch_florida_mcp_data(query)
            elif state_code == "DE":
                return await self._fetch_delaware_mcp_data(query)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error fetching MCP data: {e}")
            return None
    
    async def _fetch_florida_mcp_data(self, query: str) -> Dict[str, Any]:
        """Fetch Florida-specific data using MCP servers."""
        try:
            florida_prompt = f"""
            Fetch current Florida business license information for: {query}
            
            Please use the available tools to:
            1. Search https://www2.myfloridalicense.com/ for current license requirements
            2. Get current application fees and timelines
            3. Extract official contact information
            4. Find specific forms and documents needed
            5. Provide current processing times
            
            Focus on getting the most up-to-date and accurate information from official sources.
            """
            
            response = await self.mcp_agent.run(florida_prompt)
            return {"success": True, "data": response, "source": "Florida MCP"}
            
        except Exception as e:
            logger.error(f"Error fetching Florida MCP data: {e}")
            return {"error": str(e)}
    
    async def _fetch_delaware_mcp_data(self, query: str) -> Dict[str, Any]:
        """Fetch Delaware-specific data using MCP servers."""
        try:
            delaware_prompt = f"""
            Fetch current Delaware business license information for: {query}
            
            Please use the available tools to:
            1. Search https://firststeps.delaware.gov/ for current license requirements
            2. Get current application fees and timelines
            3. Extract official contact information
            4. Find specific forms and documents needed
            5. Provide current processing times
            
            Focus on getting the most up-to-date and accurate information from official sources.
            """
            
            response = await self.mcp_agent.run(delaware_prompt)
            return {"success": True, "data": response, "source": "Delaware MCP"}
            
        except Exception as e:
            logger.error(f"Error fetching Delaware MCP data: {e}")
            return {"error": str(e)}
    
    def _build_enhanced_prompt(self, query: str, intelligent_results: Dict[str, Any], 
                              mcp_data: Optional[Dict[str, Any]], state_code: Optional[str]) -> str:
        """Build an enhanced prompt with all available data."""
        
        # Start with intelligent semantic search results
        prompt = intelligent_results['augmented_prompt']
        
        # Add MCP data if available
        if mcp_data and mcp_data.get('success'):
            prompt += f"\n\n## REAL-TIME MCP DATA:\n"
            prompt += f"**Source**: {mcp_data.get('source', 'MCP Server')}\n"
            prompt += f"**Current Information**:\n{mcp_data['data']}\n"
            
            prompt += f"""
IMPORTANT: The MCP data above contains real-time, current information from official government websites. 
Use this information to provide the most accurate and up-to-date requirements, costs, and procedures.
"""
        
        # Add conversation context if available
        if self.conversation_history:
            prompt += f"\n\n## CONVERSATION CONTEXT:\n"
            for i, turn in enumerate(self.conversation_history[-3:], 1):  # Last 3 turns
                prompt += f"Turn {i}: User asked about {turn['user_input'][:100]}...\n"
        
        return prompt
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history."""
        return self.conversation_history
    
    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.conversation_history = []


# Global instance for easy access
enhanced_agent = EnhancedBusinessLicenseAgent()


async def run_enhanced_agent(query: str, mcp_agent=None, ai_source: str = "gemini") -> str:
    """Run the enhanced agent with the given query."""
    agent = EnhancedBusinessLicenseAgent(mcp_agent)
    return await agent.run_enhanced_agent(query, ai_source) 
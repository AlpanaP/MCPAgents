"""
Chat Interface for Business License Navigator

This module provides a chat interface with conversation history and MCP server integration
for retrieving real-time business license information.
"""

import asyncio
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from dotenv import load_dotenv
from .core.ai_services import call_gemini

# Import our existing modules
from .core.intelligent_semantic_search import intelligent_semantic_search
from .core.ai_services import sanitize_input, validate_api_key
from .enhanced_agent import run_enhanced_agent

# Import MCP components
try:
    from mcp_use import MCPAgent, MCPClient
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("⚠️ MCP components not available. Install with: pip install mcp-use")

logger = logging.getLogger(__name__)


class BusinessLicenseChat:
    """Chat interface for Business License Navigator with conversation history and MCP integration."""
    
    def __init__(self, config_file: str = "./src/config/mcp_config.json"):
        self.config_file = config_file
        self.conversation_history = []
        self.mcp_client = None
        self.mcp_agent = None
        self.llm = None
        
        # Load environment variables
        load_dotenv()
        
        # Initialize MCP components if available
        if MCP_AVAILABLE:
            self._initialize_mcp()
    
    def _initialize_mcp(self):
        """Initialize MCP client and agent."""
        try:
            # Create MCP client
            self.mcp_client = MCPClient.from_config_file(self.config_file)
            
            # Initialize LLM
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if gemini_api_key:
                # Store API key for use with call_gemini
                self.gemini_api_key = gemini_api_key
                logger.info("✅ GEMINI_API_KEY found. MCP features available.")
            else:
                logger.warning("⚠️ GEMINI_API_KEY not found. MCP features will be limited.")
                
        except Exception as e:
            logger.error(f"❌ Error initializing MCP components: {e}")
            self.mcp_client = None
            self.mcp_agent = None
    
    def _get_mcp_system_prompt(self) -> str:
        """Get the system prompt for MCP agent."""
        return """You are a Business License Navigator AI assistant with access to powerful MCP (Model Context Protocol) servers. You help users find business license requirements, costs, and application processes.

AVAILABLE TOOLS:
1. **Playwright Server** - Browser automation, web scraping, taking screenshots, filling forms
2. **Fetch Server** - Web requests, data retrieval, API calls to get current information
3. **Business License Intelligence** - Intelligent semantic search for business license requirements

CRITICAL INSTRUCTIONS:
- Use Fetch server to retrieve current information from official government websites
- Use Playwright server for complex web interactions, screenshots, or form filling
- Use Business License Intelligence for semantic analysis of business types and license requirements
- ALWAYS use tools when searching for current information, official requirements, or real-time data
- For Florida and Delaware queries, use MCP servers to fetch current information from official websites

RESPONSE STRUCTURE:
## Summary
[Brief summary of what you accomplished]

## Business Analysis
[Intelligent analysis of the business type and requirements]

## License Requirements
[Specific licenses needed with costs and timelines]

## Official Resources
[Links and current information from official sources]

## Next Steps
[Action items and application process]

## Tools Used
[List the MCP servers and tools you used]

Remember: Always use tools to get current, accurate information from official sources rather than relying on potentially outdated knowledge."""

    async def fetch_florida_info(self, query: str) -> Dict[str, Any]:
        """Fetch current Florida business license information using MCP servers."""
        if not self.mcp_agent:
            return {"error": "MCP agent not available"}
        
        try:
            # Create a specific prompt for Florida information
            florida_prompt = f"""
            Fetch current Florida business license information for: {query}
            
            Please:
            1. Use Fetch server to get current information from https://www2.myfloridalicense.com/
            2. Use Playwright server to navigate and extract specific license requirements
            3. Get current application fees, timelines, and requirements
            4. Provide official links and contact information
            """
            
            response = await self.mcp_agent.run(florida_prompt)
            return {"success": True, "data": response}
            
        except Exception as e:
            logger.error(f"Error fetching Florida info: {e}")
            return {"error": str(e)}
    
    async def fetch_delaware_info(self, query: str) -> Dict[str, Any]:
        """Fetch current Delaware business license information using MCP servers."""
        if not self.mcp_agent:
            return {"error": "MCP agent not available"}
        
        try:
            # Create a specific prompt for Delaware information
            delaware_prompt = f"""
            Fetch current Delaware business license information for: {query}
            
            Please:
            1. Use Fetch server to get current information from https://firststeps.delaware.gov/
            2. Use Playwright server to navigate and extract specific license requirements
            3. Get current application fees, timelines, and requirements
            4. Provide official links and contact information
            """
            
            response = await self.mcp_agent.run(delaware_prompt)
            return {"success": True, "data": response}
            
        except Exception as e:
            logger.error(f"Error fetching Delaware info: {e}")
            return {"error": str(e)}
    
    def add_to_history(self, user_input: str, response: str, mcp_data: Dict[str, Any] = None):
        """Add a conversation turn to the history."""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "response": response,
            "mcp_data": mcp_data
        })
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history."""
        return self.conversation_history
    
    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
        if self.mcp_agent:
            self.mcp_agent.clear_conversation_history()
    
    async def process_query(self, user_input: str) -> str:
        """Process a user query with intelligent semantic search and MCP integration."""
        
        try:
            # Use the enhanced agent with MCP integration
            response = await run_enhanced_agent(
                user_input, 
                mcp_agent=self.mcp_agent, 
                ai_source="gemini"
            )
            
            return response
            
        except Exception as e:
            error_msg = f"Error processing query: {e}"
            logger.error(error_msg)
            self.add_to_history(user_input, error_msg)
            return error_msg
    
    async def run_chat(self):
        """Run the interactive chat interface."""
        
        print("\n===== Business License Navigator Chat =====")
        print("Type 'exit' or 'quit' to end the conversation")
        print("Type 'clear' to clear conversation history")
        print("Type 'history' to see conversation history")
        print("Type 'servers' to see available MCP servers")
        print("==========================================\n")
        
        if not MCP_AVAILABLE:
            print("⚠️ MCP components not available. Install with: pip install mcp-use")
            print("Chat will work with basic intelligent semantic search only.\n")
        
        try:
            while True:
                # Get user input
                user_input = input("\nYou: ")
                
                # Check for exit command
                if user_input.lower() in ["exit", "quit"]:
                    print("Ending conversation...")
                    break
                
                # Check for clear history command
                if user_input.lower() == "clear":
                    self.clear_history()
                    print("Conversation history cleared.")
                    continue
                
                # Check for history command
                if user_input.lower() == "history":
                    print("\nConversation History:")
                    for i, turn in enumerate(self.conversation_history, 1):
                        print(f"{i}. {turn['timestamp']}: {turn['user_input'][:50]}...")
                    continue
                
                # Check for servers command
                if user_input.lower() == "servers":
                    print("\nAvailable MCP Servers:")
                    if MCP_AVAILABLE:
                        print("1. Playwright - Browser automation and web scraping")
                        print("2. Fetch - Web requests and data retrieval")
                        print("3. Business License Intelligence - Semantic search")
                    else:
                        print("MCP servers not available. Install mcp-use package.")
                    continue
                
                # Process the query
                print("\nAssistant: ", end="", flush=True)
                
                try:
                    response = await self.process_query(user_input)
                    print(response)
                    
                except Exception as e:
                    error_msg = f"Error: {e}"
                    print(error_msg)
                    logger.error(error_msg)
        
        finally:
            # Clean up
            if self.mcp_client and hasattr(self.mcp_client, 'sessions'):
                await self.mcp_client.close_all_sessions()


async def main():
    """Main function to run the chat interface."""
    chat = BusinessLicenseChat()
    await chat.run_chat()


if __name__ == "__main__":
    asyncio.run(main()) 
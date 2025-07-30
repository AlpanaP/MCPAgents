import importlib
import sys
from typing import Optional, Any, Dict
from .state_handler import StateHandler

class MCPFactory:
    """Factory for creating MCP servers for different states."""
    
    def __init__(self, state_handler: StateHandler):
        """Initialize with state handler."""
        self.state_handler = state_handler
    
    def create_rag_server(self, state_code: str):
        """Create a RAG server for a specific state."""
        try:
            mcp_servers = self.state_handler.get_mcp_servers(state_code)
            rag_config = mcp_servers.get("rag_server", {})
            
            if not rag_config:
                return None
            
            module_name = rag_config.get("module")
            class_name = rag_config.get("class")
            
            if not module_name or not class_name:
                return None
            
            # Import the module
            module = importlib.import_module(module_name)
            
            # Get the class
            server_class = getattr(module, class_name)
            
            # Create instance with config
            config = rag_config.get("config", {})
            return server_class()
            
        except Exception as e:
            print(f"Error creating RAG server for {state_code}: {e}")
            return None
    
    def create_mcp_server(self, state_code: str):
        """Create an MCP server for a specific state."""
        try:
            mcp_servers = self.state_handler.get_mcp_servers(state_code)
            mcp_config = mcp_servers.get("mcp_server", {})
            
            if not mcp_config:
                return None
            
            module_name = mcp_config.get("module")
            class_name = mcp_config.get("class")
            
            if not module_name or not class_name:
                return None
            
            # Import the module
            module = importlib.import_module(module_name)
            
            # Get the class
            server_class = getattr(module, class_name)
            
            # Create instance
            return server_class()
            
        except Exception as e:
            print(f"Error creating MCP server for {state_code}: {e}")
            return None
    
    def is_server_available(self, state_code: str, server_type: str = "rag") -> bool:
        """Check if a server is available for a state."""
        try:
            mcp_servers = self.state_handler.get_mcp_servers(state_code)
            
            if server_type == "rag":
                return "rag_server" in mcp_servers
            elif server_type == "mcp":
                return "mcp_server" in mcp_servers
            
            return False
        except Exception:
            return False 
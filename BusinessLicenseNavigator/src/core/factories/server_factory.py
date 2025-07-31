"""
Server Factory for Business License Navigator.

This module provides a factory pattern for creating RAG and MCP servers
dynamically based on configuration.
"""

import importlib
import json
import logging
import os
from typing import Dict, Any, Optional, Type, List

from ..models.base_rag_server import BaseRAGServer, RAGConfig
from ..models.base_mcp_server import BaseMCPServer, MCPConfig, Tool


class ServerFactory:
    """
    Factory for creating RAG and MCP servers.
    
    This factory loads server configurations from JSON files and creates
    server instances dynamically.
    """
    
    def __init__(self, config_dir: str = "src/config"):
        """Initialize the server factory."""
        self.config_dir = config_dir
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Load configurations
        self.rag_servers_config = self._load_config("rag_servers.json")
        self.mcp_servers_config = self._load_config("mcp_servers.json")
    
    def _load_config(self, filename: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        config_path = os.path.join(self.config_dir, filename)
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading config {filename}: {e}")
            return {}
    
    def create_rag_server(self, server_name: str, **kwargs) -> Optional[BaseRAGServer]:
        """
        Create a RAG server instance.
        
        Args:
            server_name: Name of the server to create
            **kwargs: Additional configuration parameters
            
        Returns:
            RAG server instance or None if creation fails
        """
        try:
            if server_name not in self.rag_servers_config.get("servers", {}):
                self.logger.error(f"RAG server '{server_name}' not found in configuration")
                return None
            
            server_config = self.rag_servers_config["servers"][server_name]
            module_name = server_config["module"]
            class_name = server_config["class"]
            
            # Import the module
            module = importlib.import_module(module_name)
            server_class = getattr(module, class_name)
            
            # Create RAG config
            rag_config = RAGConfig(**server_config["config"])
            
            # Create server instance
            server = server_class(rag_config, **kwargs)
            
            self.logger.info(f"Successfully created RAG server: {server_name}")
            return server
            
        except Exception as e:
            self.logger.error(f"Error creating RAG server '{server_name}': {e}")
            return None
    
    def create_mcp_server(self, server_name: str, **kwargs) -> Optional[BaseMCPServer]:
        """
        Create an MCP server instance.
        
        Args:
            server_name: Name of the server to create
            **kwargs: Additional configuration parameters
            
        Returns:
            MCP server instance or None if creation fails
        """
        try:
            if server_name not in self.mcp_servers_config.get("servers", {}):
                self.logger.error(f"MCP server '{server_name}' not found in configuration")
                return None
            
            server_config = self.mcp_servers_config["servers"][server_name]
            module_name = server_config["module"]
            class_name = server_config["class"]
            
            # Import the module
            module = importlib.import_module(module_name)
            server_class = getattr(module, class_name)
            
            # Create tools from config
            tools = []
            for tool_config in server_config["config"]["tools"]:
                tool = Tool(
                    name=tool_config["name"],
                    description=tool_config["description"],
                    input_schema=tool_config["input_schema"]
                )
                tools.append(tool)
            
            # Create MCP config
            mcp_config = MCPConfig(
                server_name=server_config["config"]["server_name"],
                server_description=server_config["config"]["server_description"],
                tools=tools
            )
            
            # Create server instance
            server = server_class(mcp_config, **kwargs)
            
            self.logger.info(f"Successfully created MCP server: {server_name}")
            return server
            
        except Exception as e:
            self.logger.error(f"Error creating MCP server '{server_name}': {e}")
            return None
    
    def get_available_rag_servers(self) -> List[str]:
        """Get list of available RAG server names."""
        return list(self.rag_servers_config.get("servers", {}).keys())
    
    def get_available_mcp_servers(self) -> List[str]:
        """Get list of available MCP server names."""
        return list(self.mcp_servers_config.get("servers", {}).keys())
    
    def get_server_groups(self) -> Dict[str, List[str]]:
        """Get server groups for different states/regions."""
        return self.rag_servers_config.get("server_groups", {})
    
    def create_servers_for_state(self, state_code: str) -> Dict[str, Any]:
        """
        Create RAG and MCP servers for a specific state.
        
        Args:
            state_code: State code (e.g., 'DE', 'FL')
            
        Returns:
            Dictionary containing RAG and MCP servers for the state
        """
        state_code_lower = state_code.lower()
        server_groups = self.get_server_groups()
        
        servers = {}
        
        # Find RAG server for state
        for group_name, rag_servers in server_groups.items():
            if state_code_lower in group_name:
                for rag_server_name in rag_servers:
                    rag_server = self.create_rag_server(rag_server_name)
                    if rag_server:
                        servers["rag_server"] = rag_server
                        break
        
        # Find MCP server for state
        for group_name, mcp_servers in server_groups.items():
            if state_code_lower in group_name:
                for mcp_server_name in mcp_servers:
                    mcp_server = self.create_mcp_server(mcp_server_name)
                    if mcp_server:
                        servers["mcp_server"] = mcp_server
                        break
        
        # If no state-specific servers found, use generic servers
        if "rag_server" not in servers:
            generic_rag = self.create_rag_server("generic_rag_server")
            if generic_rag:
                servers["rag_server"] = generic_rag
        
        if "mcp_server" not in servers:
            generic_mcp = self.create_mcp_server("generic_license_server")
            if generic_mcp:
                servers["mcp_server"] = generic_mcp
        
        return servers 
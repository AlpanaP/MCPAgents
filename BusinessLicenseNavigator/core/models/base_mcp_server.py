"""
Base MCP Server Interface.

This module defines the base interface for all MCP (Model Context Protocol) servers
in the Business License Navigator system.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .tool_result import ToolResult
from .text_content import TextContent


@dataclass
class Tool:
    """MCP Tool definition."""
    name: str
    description: str
    input_schema: Dict[str, Any]


@dataclass
class MCPConfig:
    """Configuration for MCP servers."""
    server_name: str
    server_description: str
    tools: List[Tool]


class BaseMCPServer(ABC):
    """
    Base interface for MCP servers.
    
    All MCP servers must implement these methods to provide consistent
    Model Context Protocol capabilities.
    """
    
    def __init__(self, config: MCPConfig):
        """Initialize the MCP server with configuration."""
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def list_tools(self) -> List[Tool]:
        """
        List available MCP tools.
        
        Returns:
            List of available tools with their descriptions and input schemas
        """
        pass
    
    @abstractmethod
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """
        Call a specific MCP tool.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            ToolResult containing the tool's response
        """
        pass
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information and status."""
        return {
            "server_type": self.__class__.__name__,
            "server_name": self.config.server_name,
            "server_description": self.config.server_description,
            "available_tools": len(self.config.tools),
            "tools": [tool.name for tool in self.config.tools]
        } 
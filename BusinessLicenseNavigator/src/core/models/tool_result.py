"""
Tool Result Data Model.

This module defines the ToolResult class used by MCP servers
to return structured tool results.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from .text_content import TextContent


@dataclass
class ToolResult:
    """Result from an MCP tool call."""
    content: List[TextContent]
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def get_text(self) -> str:
        """Get the text content as a single string."""
        if not self.content:
            return ""
        
        text_parts = []
        for item in self.content:
            if hasattr(item, 'text'):
                text_parts.append(item.text)
            elif isinstance(item, str):
                text_parts.append(item)
        
        return "\n\n".join(text_parts)
    
    def get_first_text(self) -> str:
        """Get the first text content item."""
        if not self.content:
            return ""
        
        first_item = self.content[0]
        if hasattr(first_item, 'text'):
            return first_item.text
        elif isinstance(first_item, str):
            return first_item
        
        return ""
    
    def is_valid(self) -> bool:
        """Check if the tool result is valid."""
        return bool(self.content and not self.error and self.get_text().strip())
    
    @classmethod
    def error_result(cls, error_message: str) -> 'ToolResult':
        """Create an error result."""
        return cls(
            content=[],
            error=error_message
        ) 
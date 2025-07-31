"""
Text Content Data Model.

This module defines the TextContent class used for structured text content
in MCP tool results.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class TextContent:
    """Structured text content for MCP tool results."""
    type: str = "text"
    text: str = ""
    metadata: Optional[dict] = None
    
    def __post_init__(self):
        """Validate the text content."""
        if not isinstance(self.text, str):
            raise ValueError("text must be a string")
        
        if not isinstance(self.type, str):
            raise ValueError("type must be a string")
    
    def is_valid(self) -> bool:
        """Check if the text content is valid."""
        return bool(self.text and self.text.strip()) 
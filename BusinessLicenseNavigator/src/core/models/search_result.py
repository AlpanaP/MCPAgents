"""
Search Result Data Model.

This module defines the SearchResult class used by RAG servers
to return structured search results.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class SearchResult:
    """Result from a RAG search operation."""
    content: List[Dict[str, str]]
    metadata: Dict[str, Any]
    score: Optional[float] = None
    source: Optional[str] = None
    
    def get_text(self) -> str:
        """Get the text content as a single string."""
        if not self.content:
            return ""
        
        # Join all text content
        text_parts = []
        for item in self.content:
            if isinstance(item, dict) and 'text' in item:
                text_parts.append(item['text'])
            elif isinstance(item, str):
                text_parts.append(item)
        
        return "\n\n".join(text_parts)
    
    def get_first_text(self) -> str:
        """Get the first text content item."""
        if not self.content:
            return ""
        
        first_item = self.content[0]
        if isinstance(first_item, dict) and 'text' in first_item:
            return first_item['text']
        elif isinstance(first_item, str):
            return first_item
        
        return ""
    
    def is_valid(self) -> bool:
        """Check if the search result is valid."""
        return bool(self.content and self.get_text().strip()) 
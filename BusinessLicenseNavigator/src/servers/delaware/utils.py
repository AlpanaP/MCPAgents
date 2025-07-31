"""
Utilities for Delaware RAG Server.

This module contains utility functions for the Delaware RAG server
to improve maintainability and code organization.
"""

import re
from typing import List, Dict, Any
from urllib.parse import urlparse

from .config import ALLOWED_DOMAINS


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks."""
    if not text or not isinstance(text, str):
        return ""
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)
    # Limit length to prevent DoS
    return text[:500].strip()


def validate_url(url: str) -> bool:
    """Validate URL format and security."""
    if not url or not isinstance(url, str):
        return False
    
    try:
        parsed = urlparse(url)
        # Only allow HTTPS and specific domains
        if parsed.scheme not in ['https']:
            return False
        
        # Only allow Delaware government domains
        if parsed.netloc not in ALLOWED_DOMAINS:
            return False
        
        return True
    except Exception:
        return False


def extract_text_from_html(html_content: str) -> str:
    """Extract clean text from HTML content."""
    try:
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it up
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception:
        return ""


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks for better vector search."""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundaries
        if end < len(text):
            # Look for sentence endings
            for i in range(end, max(start, end - 100), -1):
                if text[i] in '.!?':
                    end = i + 1
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks


def find_matching_industry(business_type: str, license_data: Dict[str, Any]) -> str:
    """Find the best matching industry for a business type."""
    business_type_lower = business_type.lower()
    
    # Find matching industry
    for industry, pattern in license_data.items():
        keywords = pattern.get('keywords', [])
        if any(keyword.lower() in business_type_lower for keyword in keywords):
            return industry
    
    # Default to general business
    return "general"


def format_license_response(license_info: Dict[str, Any], business_type: str) -> str:
    """Format license information into a structured response."""
    response_parts = [
        f"# Delaware Business License Information for {business_type.title()}\n\n",
        "## License Requirements:\n"
    ]
    
    license_types = license_info.get('license_types', [])
    requirements = license_info.get('requirements', [])
    fees = license_info.get('fees', [])
    due_dates = license_info.get('due_dates', [])
    
    for i, license_type in enumerate(license_types):
        response_parts.append(f"### {license_type}\n")
        
        if i < len(fees):
            response_parts.append(f"- **Cost**: {fees[i]}\n")
        
        if i < len(due_dates):
            response_parts.append(f"- **Due Date**: {due_dates[i]}\n")
        
        response_parts.append("- **Renewal**: Annual renewal required\n\n")
    
    if requirements:
        response_parts.append("## Requirements:\n")
        for requirement in requirements:
            response_parts.append(f"- {requirement}\n")
        response_parts.append("\n")
    
    response_parts.append("## Application Process:\n")
    response_parts.append("1. Complete required training/certifications\n")
    response_parts.append("2. Gather required documents\n")
    response_parts.append("3. Submit application with fees\n")
    response_parts.append("4. Wait for approval (2-8 weeks)\n\n")
    
    response_parts.append("**Source**: Delaware Division of Professional Regulation\n")
    
    return "".join(response_parts) 
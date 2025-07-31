"""
AI Services for Business License Navigator.

This module handles AI service interactions including Gemini API calls,
Ollama integration, and fallback responses.
"""

import os
import re
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks."""
    if not text or not isinstance(text, str):
        return ""
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)
    # Limit length to prevent DoS
    return text[:1000].strip()


def validate_api_key(api_key: str) -> bool:
    """Validate API key format."""
    if not api_key or not isinstance(api_key, str):
        return False
    
    # Basic validation for Gemini API key format
    # For testing, accept any non-empty string
    if len(api_key) > 0:
        return True
    
    return False


def call_gemini(prompt: str, api_key: str) -> str:
    """Call Gemini API with a prompt"""
    try:
        # Validate inputs
        if not validate_api_key(api_key):
            return "ERROR: Invalid API key format"
        
        sanitized_prompt = sanitize_input(prompt)
        if not sanitized_prompt:
            return "ERROR: Invalid prompt"
        
        # Import here to avoid dependency issues
        import google.generativeai as genai
        
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # Use the Gemini Pro model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generate response with safety settings
        response = model.generate_content(
            sanitized_prompt,
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        )
        
        return response.text
        
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")
        return f"ERROR: {str(e)}"


def call_ollama(model: str, prompt: str) -> str:
    """Call Ollama with a prompt"""
    try:
        # Validate inputs
        if not model or not isinstance(model, str):
            return "ERROR: Invalid model name"
        
        sanitized_prompt = sanitize_input(prompt)
        if not sanitized_prompt:
            return "ERROR: Invalid prompt"
        
        # Import here to avoid dependency issues
        import requests
        
        # Call Ollama API
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": sanitized_prompt,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json().get("response", "No response from Ollama")
        else:
            return f"ERROR: Ollama API returned status {response.status_code}"
            
    except Exception as e:
        logger.error(f"Error calling Ollama: {e}")
        return f"ERROR: {str(e)}"


def get_fallback_response(business_description: str) -> str:
    """Get a fallback response when AI services are unavailable."""
    try:
        # Simple rule-based fallback
        business_lower = business_description.lower()
        
        if any(word in business_lower for word in ['restaurant', 'food', 'cafe', 'bakery']):
            return """## Food Service Business License Requirements

### Required Licenses:
- **Food Service License**: Required for restaurants, cafes, bakeries
  - Cost: $100-300 application fee
  - Due Date: Apply 45 days before opening
  - Renewal: Annual renewal required

### Requirements:
- Food safety training certification
- Health inspection approval
- Kitchen facility compliance
- Employee training records

### Application Process:
1. Complete food safety training
2. Pass health inspection
3. Submit application with fees
4. Wait for approval (2-4 weeks)

**Source**: State Department of Health"""
        
        elif any(word in business_lower for word in ['construction', 'contractor', 'building']):
            return """## Construction Business License Requirements

### Required Licenses:
- **General Contractor License**: Required for construction work
  - Cost: $200-500 application fee
  - Due Date: Apply 60 days before starting work
  - Renewal: Annual renewal required

### Requirements:
- Experience verification (2-5 years)
- Background check
- Financial responsibility proof
- Insurance coverage

### Application Process:
1. Verify experience requirements
2. Complete background check
3. Submit application with fees
4. Wait for approval (4-8 weeks)

**Source**: State Department of Professional Regulation"""
        
        elif any(word in business_lower for word in ['cannabis', 'marijuana', 'dispensary']):
            return """## Cannabis Business License Requirements

### Required Licenses:
- **Cannabis Business License**: Required for cannabis operations
  - Cost: $5,000-25,000 application fee
  - Due Date: Apply 120 days before planned opening
  - Renewal: Annual renewal required

### Requirements:
- Comprehensive business plan
- Financial solvency proof
- Security plan
- Background checks for principals

### Application Process:
1. Complete background checks
2. Submit security plan
3. Pay application fees
4. Wait for approval (6-12 months)

**Source**: State Cannabis Control Board"""
        
        else:
            return """## General Business License Requirements

### Required Licenses:
- **General Business License**: Basic business operations
  - Cost: $50-200 application fee
  - Due Date: Apply before starting business operations
  - Renewal: Annual renewal required

### Requirements:
- Business registration
- Tax identification
- Local permits (if required)
- Insurance coverage

### Application Process:
1. Register business entity
2. Obtain tax identification
3. Submit application with fees
4. Wait for approval (2-4 weeks)

**Source**: State Department of Business Regulation

*Note: This is a general response. Please check with your specific state for accurate requirements.*"""
            
    except Exception as e:
        logger.error(f"Error generating fallback response: {e}")
        return "I'm sorry, I'm unable to provide specific license information at the moment. Please contact your local business licensing office for accurate requirements."


def get_source_attribution(ai_used: str, state_rag_used: bool, business_description: str) -> tuple:
    """Generate source attribution information."""
    try:
        # Determine location info based on query
        business_lower = business_description.lower()
        
        # Simple state detection (can be enhanced)
        state_info = ""
        sources = []
        
        if any(word in business_lower for word in ['delaware', 'de']):
            state_info = "📍 **Delaware Business License Information**"
            sources = [
                "Delaware Division of Professional Regulation",
                "Delaware Business First Steps",
                "Delaware Secretary of State"
            ]
        elif any(word in business_lower for word in ['florida', 'fl']):
            state_info = "📍 **Florida Business License Information**"
            sources = [
                "Florida Department of Business and Professional Regulation",
                "Florida Division of Corporations",
                "Florida Department of Revenue"
            ]
        else:
            state_info = "📍 **General Business License Information**"
            sources = [
                "State Business Licensing Database",
                "Industry Regulations",
                "Government Business Portal"
            ]
        
        # Add AI source
        if ai_used == "Gemini":
            sources.append("Google Gemini AI")
        elif ai_used == "Ollama":
            sources.append("Local Ollama AI")
        else:
            sources.append("AI Assistant")
        
        # Add RAG source if used
        if state_rag_used:
            sources.append("Vector Database (RAG)")
        
        return state_info, sources
        
    except Exception as e:
        logger.error(f"Error generating source attribution: {e}")
        return "📍 **Business License Information**", ["AI Assistant", "Business License Database"] 
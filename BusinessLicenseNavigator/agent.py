import requests
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
import asyncio
import sys
import re
from typing import Optional

# Load environment variables from .env file
load_dotenv()

# Add the parent directory to the path so we can import Delaware RAG tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from delaware_rag.delaware_rag_server import DelawareRAGServer
    DELAWARE_RAG_AVAILABLE = True
except ImportError:
    DELAWARE_RAG_AVAILABLE = False
    print("Warning: Delaware RAG tools not available. Install dependencies with: pip install -r requirements.txt")


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
    if api_key.startswith('AI') and len(api_key) > 20:
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
        return f"ERROR: {str(e)}"


def call_ollama(model: str, prompt: str) -> str:
    """Simple function to call Ollama with a prompt (kept for local development)"""
    # Validate inputs
    if not model or not isinstance(model, str):
        return "ERROR: Invalid model name"
    
    sanitized_prompt = sanitize_input(prompt)
    if not sanitized_prompt:
        return "ERROR: Invalid prompt"
    
    url = "http://localhost:11434/api/generate"
    data = {
        "model": model,
        "prompt": sanitized_prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.ConnectionError:
        return "ERROR: Ollama server is not running. Please start Ollama with 'ollama serve' and ensure the model is installed."
    except requests.exceptions.Timeout:
        return "ERROR: Ollama request timed out. Please check if the server is running properly."
    except Exception as e:
        return f"ERROR: {str(e)}"


async def get_delaware_license_info(business_description: str) -> Optional[str]:
    """Get Delaware-specific license information using RAG tools"""
    if not DELAWARE_RAG_AVAILABLE:
        return None
    
    # Validate input
    if not business_description or not isinstance(business_description, str):
        return None
    
    sanitized_description = sanitize_input(business_description)
    if not sanitized_description:
        return None
    
    try:
        server = DelawareRAGServer()
        
        # Extract business type from description
        business_lower = sanitized_description.lower()
        
        # Determine search query based on business type
        search_query = ""
        if any(word in business_lower for word in ['restaurant', 'food', 'bakery', 'cafe', 'catering']):
            search_query = "food"
        elif any(word in business_lower for word in ['health', 'medical', 'doctor', 'nurse', 'pharmacy']):
            search_query = "health"
        elif any(word in business_lower for word in ['consulting', 'professional', 'service']):
            search_query = "profession"
        elif any(word in business_lower for word in ['construction', 'contractor', 'building']):
            search_query = "contractor"
        elif any(word in business_lower for word in ['retail', 'store', 'shop']):
            search_query = "business"
        else:
            search_query = "business"
        
        # Get Delaware license information
        delaware_info = "## 🏛️ Delaware Business License Information\n\n"
        delaware_info += "**Source**: [Delaware Business First Steps](https://firststeps.delaware.gov/topics/)\n\n"
        
        # Get business steps
        steps_result = await server._get_business_steps()
        if steps_result and not steps_result.content[0].text.startswith("Error"):
            delaware_info += "### 📋 Delaware Business Steps:\n"
            delaware_info += steps_result.content[0].text.split("Source:")[0] + "\n\n"
        
        # Get license categories
        categories_result = await server._get_license_categories()
        if categories_result and not categories_result.content[0].text.startswith("Error"):
            delaware_info += "### 🏢 Available License Categories:\n"
            categories_text = categories_result.content[0].text
            # Extract categories list
            if "Available Categories:" in categories_text:
                categories_section = categories_text.split("Available Categories:")[1]
                delaware_info += categories_section + "\n\n"
        
        # Get specific license information using RAG search
        if search_query:
            search_result = await server._search_licenses_rag({"query": search_query, "top_k": 5})
            if search_result and not search_result.content[0].text.startswith("Error"):
                delaware_info += f"### 🔍 Relevant Delaware Licenses for '{search_query}':\n"
                search_text = search_result.content[0].text
                # Extract search results
                if "Found" in search_text and "relevant license types:" in search_text:
                    results_section = search_text.split("relevant license types:")[1].split("For more detailed information")[0]
                    delaware_info += results_section + "\n\n"
        
        delaware_info += "### 📞 Delaware Resources:\n"
        delaware_info += "- **Delaware Business First Steps**: https://firststeps.delaware.gov/\n"
        delaware_info += "- **Delaware Division of Corporations**: https://corp.delaware.gov/\n"
        delaware_info += "- **Delaware Small Business Development Center**: https://www.delawaresbdc.org/\n"
        delaware_info += "- **Delaware Department of State**: https://sos.delaware.gov/\n\n"
        
        # Add comprehensive Delaware resources based on business type
        if any(word in business_lower for word in ['food', 'restaurant', 'bakery', 'cafe', 'catering']):
            delaware_info += "### 🍽️ Food Business Specific Resources:\n"
            delaware_info += "- **Food Service Licenses**: https://dhss.delaware.gov/dhss/dph/hsp/restaurant.html\n"
            delaware_info += "- **Health & Social Services**: https://dhss.delaware.gov/\n"
            delaware_info += "- **Food Safety**: https://dhss.delaware.gov/dhss/dph/hsp/food.html\n\n"
        
        elif any(word in business_lower for word in ['health', 'medical', 'doctor', 'nurse', 'pharmacy']):
            delaware_info += "### 🏥 Health Care Specific Resources:\n"
            delaware_info += "- **Health Care Licenses**: https://sos.delaware.gov/professional-regulation/health-occupations/\n"
            delaware_info += "- **Health & Social Services**: https://dhss.delaware.gov/\n"
            delaware_info += "- **Professional Licensing**: https://sos.delaware.gov/professional-regulation/\n\n"
        
        elif any(word in business_lower for word in ['construction', 'contractor', 'building']):
            delaware_info += "### 🏗️ Construction Specific Resources:\n"
            delaware_info += "- **Contractor Licenses**: https://sos.delaware.gov/professional-regulation/contractors/\n"
            delaware_info += "- **Professional Licensing**: https://sos.delaware.gov/professional-regulation/\n"
            delaware_info += "- **Workplace Safety**: https://labor.delaware.gov/workplace-safety/\n\n"
        
        elif any(word in business_lower for word in ['real estate', 'realtor', 'property']):
            delaware_info += "### 🏠 Real Estate Specific Resources:\n"
            delaware_info += "- **Real Estate Licenses**: https://sos.delaware.gov/professional-regulation/real-estate/\n"
            delaware_info += "- **Professional Licensing**: https://sos.delaware.gov/professional-regulation/\n\n"
        
        # Add tax resources
        delaware_info += "### 💰 Delaware Tax Resources:\n"
        delaware_info += "- **Division of Revenue**: https://revenue.delaware.gov/\n"
        delaware_info += "- **Business Tax Registration**: https://revenue.delaware.gov/business-tax-registration/\n"
        delaware_info += "- **Sales Tax**: https://revenue.delaware.gov/sales-tax/\n"
        delaware_info += "- **Corporate Income Tax**: https://revenue.delaware.gov/corporate-income-tax/\n\n"
        
        # Add employment resources
        delaware_info += "### 👥 Delaware Employment Resources:\n"
        delaware_info += "- **Department of Labor**: https://labor.delaware.gov/\n"
        delaware_info += "- **Workers Compensation**: https://labor.delaware.gov/workers-compensation/\n"
        delaware_info += "- **Unemployment Insurance**: https://labor.delaware.gov/unemployment-insurance/\n\n"
        
        # Add local government resources
        delaware_info += "### 🏘️ Delaware Local Government Resources:\n"
        delaware_info += "- **New Castle County**: https://www.nccde.org/\n"
        delaware_info += "- **Kent County**: https://www.co.kent.de.us/\n"
        delaware_info += "- **Sussex County**: https://www.sussexcountyde.gov/\n"
        delaware_info += "- **City of Wilmington**: https://www.wilmingtonde.gov/\n"
        delaware_info += "- **City of Dover**: https://www.cityofdover.com/\n"
        delaware_info += "- **City of Newark**: https://www.newarkde.gov/\n\n"
        
        # Add business support resources
        delaware_info += "### 🤝 Delaware Business Support:\n"
        delaware_info += "- **Delaware Economic Development**: https://choosedelaware.com/\n"
        delaware_info += "- **Delaware Chamber of Commerce**: https://www.delawarechamber.com/\n"
        delaware_info += "- **Delaware SBA**: https://www.sba.gov/offices/district/de/wilmington\n"
        delaware_info += "- **Delaware SCORE**: https://delaware.score.org/\n\n"
        
        delaware_info += "📞 **Need Help?**: Call Delaware Business First Steps at 1-800-292-7935\n"
        delaware_info += "💡 **Tip**: Contact your local Small Business Administration (SBA) office for additional guidance.\n\n"
        
        return delaware_info
        
    except Exception as e:
        print(f"Error getting Delaware license info: {e}")
        return None


def get_fallback_response(business_description):
    """Provide fallback guidance when AI is not available"""
    
    # Simple keyword-based guidance
    business_lower = business_description.lower()
    
    guidance = "## Business License Guidance\n\n"
    
    if any(word in business_lower for word in ['bakery', 'food', 'restaurant', 'cafe']):
        guidance += """
### 🍰 Food Business Requirements:

**1. Food Service License**
- Contact your local health department
- Complete food safety training
- Pass kitchen inspection

**2. Business Registration**
- Register with your state's Secretary of State
- Obtain Federal Tax ID (EIN)
- Register for sales tax

**3. Additional Permits**
- Food handler's permit
- Fire safety inspection
- Zoning compliance check

**4. Insurance**
- General liability insurance
- Product liability coverage
- Workers' compensation (if hiring)
"""
    elif any(word in business_lower for word in ['consulting', 'service', 'professional']):
        guidance += """
### 💼 Professional Service Requirements:

**1. Business Registration**
- Register with your state's Secretary of State
- Obtain Federal Tax ID (EIN)
- Professional license (if required)

**2. Insurance**
- Professional liability insurance
- General business insurance
- Errors & omissions coverage

**3. Compliance**
- Check professional licensing requirements
- Verify continuing education needs
- Review industry regulations
"""
    elif any(word in business_lower for word in ['online', 'ecommerce', 'website']):
        guidance += """
### 🌐 Online Business Requirements:

**1. Business Registration**
- Register with your state's Secretary of State
- Obtain Federal Tax ID (EIN)
- Register for sales tax collection

**2. Website Compliance**
- Privacy policy
- Terms of service
- SSL certificate
- GDPR compliance (if applicable)

**3. Payment Processing**
- Set up merchant account
- PCI compliance
- Secure payment gateway
"""
    else:
        guidance += """
### 🏢 General Business Requirements:

**1. Business Registration**
- Register with your state's Secretary of State
- Obtain Federal Tax ID (EIN)
- Register for sales tax (if applicable)

**2. Local Permits**
- Check with your city/county clerk
- Zoning compliance
- Sign permits (if applicable)

**3. Insurance**
- General liability insurance
- Property insurance
- Workers' compensation (if hiring)

**4. Additional Considerations**
- Industry-specific licenses
- Professional certifications
- Continuing education requirements
"""

    guidance += f"\n\n**Next Steps:**\n1. Contact your local Small Business Administration (SBA)\n2. Check with your city/county clerk's office\n3. Consult with a business attorney\n4. Verify requirements with your state's business licensing office\n\n*This is general guidance. Always verify specific requirements with local authorities.*"
    
    return guidance


def get_source_attribution(ai_used, delaware_rag_used, business_description):
    """Generate source attribution based on what was used"""
    sources = []
    
    if ai_used:
        if "gemini" in ai_used.lower():
            sources.append("**AI Source**: Google Gemini 1.5 Flash")
        elif "ollama" in ai_used.lower():
            sources.append("**AI Source**: Local Ollama (llama3.1:8b)")
        else:
            sources.append("**AI Source**: AI-powered guidance")
    
    if delaware_rag_used:
        sources.append("**Delaware Data Source**: [Delaware Business First Steps](https://firststeps.delaware.gov/topics/)")
        sources.append("**Vector Database**: Qdrant with semantic search")
        sources.append("**Delaware Government Resources**: [Division of Corporations](https://corp.delaware.gov/), [Department of State](https://sos.delaware.gov/), [Division of Revenue](https://revenue.delaware.gov/)")
    
    # Detect location from business description
    business_lower = business_description.lower()
    location_info = ""
    
    if any(word in business_lower for word in ['delaware', 'de', 'first state']):
        location_info = "**Location**: Delaware"
        sources.append("**State Resources**: Delaware government websites")
        sources.append("**Delaware Specific Links**: [Business First Steps](https://firststeps.delaware.gov/), [Professional Licensing](https://sos.delaware.gov/professional-regulation/), [Tax Registration](https://revenue.delaware.gov/business-tax-registration/)")
    elif any(word in business_lower for word in ['texas', 'tx']):
        location_info = "**Location**: Texas"
        sources.append("**State Resources**: Texas Secretary of State")
        sources.append("**Texas Specific Links**: [Texas Secretary of State](https://www.sos.state.tx.us/), [Texas Comptroller](https://comptroller.texas.gov/), [Texas Workforce Commission](https://www.twc.texas.gov/)")
    elif any(word in business_lower for word in ['california', 'ca']):
        location_info = "**Location**: California"
        sources.append("**State Resources**: California Secretary of State")
        sources.append("**California Specific Links**: [CA Secretary of State](https://www.sos.ca.gov/), [CA Department of Tax](https://www.cdtfa.ca.gov/), [CA Employment Development](https://www.edd.ca.gov/)")
    elif any(word in business_lower for word in ['new york', 'ny']):
        location_info = "**Location**: New York"
        sources.append("**State Resources**: New York Department of State")
        sources.append("**New York Specific Links**: [NY Department of State](https://dos.ny.gov/), [NY Department of Tax](https://www.tax.ny.gov/), [NY Department of Labor](https://dol.ny.gov/)")
    elif any(word in business_lower for word in ['florida', 'fl']):
        location_info = "**Location**: Florida"
        sources.append("**State Resources**: Florida Department of State")
        sources.append("**Florida Specific Links**: [FL Department of State](https://dos.myflorida.com/), [FL Department of Revenue](https://floridarevenue.com/), [FL Department of Economic Opportunity](https://floridajobs.org/)")
    else:
        location_info = "**Location**: General guidance (verify with your state)"
        sources.append("**General Resources**: SBA and local authorities")
        sources.append("**Federal Resources**: [SBA](https://www.sba.gov/), [IRS](https://www.irs.gov/), [Department of Labor](https://www.dol.gov/)")
    
    return location_info, sources


async def run_agent_async(user_input: str) -> str:
    """Run the business license navigator agent with Delaware RAG integration"""
    
    # Validate input
    if not user_input or not isinstance(user_input, str):
        return "ERROR: Invalid input provided"
    
    sanitized_input = sanitize_input(user_input)
    if not sanitized_input:
        return "ERROR: Input is empty or contains invalid characters"
    
    # Check if this is a Delaware-specific query
    business_lower = sanitized_input.lower()
    is_delaware_query = any(word in business_lower for word in ['delaware', 'de', 'first state'])
    
    # Create a prompt for business license guidance
    prompt = f"""
    You are a helpful business license navigator. A user has provided the following information about their business:
    
    {sanitized_input}
    
    Please provide guidance on:
    1. What type of business license they might need
    2. Any specific permits required
    3. Steps they should take to obtain the necessary licenses
    4. Any additional considerations for their business type and location
    
    Be helpful, specific, and provide actionable advice. Format your response with clear headings and bullet points.
    """
    
    # Try Gemini API first
    api_key = os.getenv('GEMINI_API_KEY')
    ai_response = None
    ai_source = None
    
    if api_key and validate_api_key(api_key):
        ai_response = call_gemini(prompt, api_key)
        if not ai_response.startswith("ERROR:"):
            ai_source = "Gemini"
        else:
            ai_response = None
    
    # Try Ollama as fallback if Gemini failed
    if not ai_response:
        ollama_response = call_ollama("llama3.1:8b", prompt)
        if not ollama_response.startswith("ERROR:"):
            ai_response = ollama_response
            ai_source = "Ollama"
    
    # Get Delaware-specific information
    delaware_info = None
    if is_delaware_query or DELAWARE_RAG_AVAILABLE:
        delaware_info = await get_delaware_license_info(sanitized_input)
    
    # Generate source attribution
    location_info, sources = get_source_attribution(ai_source, delaware_info is not None, sanitized_input)
    
    # Combine AI response with Delaware-specific information
    final_response = ""
    
    # Add source attribution at the top
    final_response += "## 📍 Response Sources\n\n"
    final_response += f"{location_info}\n\n"
    final_response += "**Information Sources:**\n"
    for source in sources:
        final_response += f"- {source}\n"
    final_response += "\n---\n\n"
    
    if ai_response:
        final_response += "## 🤖 AI-Powered Business License Guidance\n\n"
        final_response += ai_response + "\n\n"
    
    # Add Delaware-specific information if available and relevant
    if delaware_info:
        final_response += delaware_info
    
    # If no AI response, use fallback
    if not ai_response:
        final_response += "## 📋 General Business License Guidance\n\n"
        final_response += get_fallback_response(sanitized_input)
    
    return final_response


def run_agent(user_input: str) -> str:
    """Synchronous wrapper for the async agent"""
    try:
        # Validate input
        if not user_input or not isinstance(user_input, str):
            return "ERROR: Invalid input provided"
        
        return asyncio.run(run_agent_async(user_input))
    except Exception as e:
        print(f"Error in agent: {e}")
        return get_fallback_response(user_input if isinstance(user_input, str) else "")


if __name__ == "__main__":
    # Test the agent
    test_input = "I run a home bakery in Delaware"
    result = run_agent(test_input)
    print("Test result:")
    print(result) 
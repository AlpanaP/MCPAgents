import requests
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
import asyncio
import sys

# Load environment variables from .env file
load_dotenv()

# Add the parent directory to the path so we can import Delaware RAG tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from delaware_rag_server import DelawareRAGServer
    DELAWARE_RAG_AVAILABLE = True
except ImportError:
    DELAWARE_RAG_AVAILABLE = False
    print("Warning: Delaware RAG tools not available. Install dependencies with: pip install -r requirements.txt")


def call_gemini(prompt, api_key):
    """Call Gemini API with a prompt"""
    try:
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # Use the Gemini Pro model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generate response
        response = model.generate_content(prompt)
        
        return response.text
    except Exception as e:
        return f"ERROR: {str(e)}"


def call_ollama(model, prompt):
    """Simple function to call Ollama with a prompt (kept for local development)"""
    url = "http://localhost:11434/api/generate"
    data = {
        "model": model,
        "prompt": prompt,
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


async def get_delaware_license_info(business_description):
    """Get Delaware-specific license information using RAG tools"""
    if not DELAWARE_RAG_AVAILABLE:
        return None
    
    try:
        server = DelawareRAGServer()
        
        # Extract business type from description
        business_lower = business_description.lower()
        
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


async def run_agent_async(user_input):
    """Run the business license navigator agent with Delaware RAG integration"""
    
    # Check if this is a Delaware-specific query
    business_lower = user_input.lower()
    is_delaware_query = any(word in business_lower for word in ['delaware', 'de', 'first state'])
    
    # Create a prompt for business license guidance
    prompt = f"""
    You are a helpful business license navigator. A user has provided the following information about their business:
    
    {user_input}
    
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
    
    if api_key:
        ai_response = call_gemini(prompt, api_key)
        if ai_response.startswith("ERROR:"):
            ai_response = None
    
    # Try Ollama as fallback if Gemini failed
    if not ai_response:
        ollama_response = call_ollama("llama3.1:8b", prompt)
        if not ollama_response.startswith("ERROR:"):
            ai_response = ollama_response
    
    # Combine AI response with Delaware-specific information
    final_response = ""
    
    if ai_response:
        final_response += "## 🤖 AI-Powered Business License Guidance\n\n"
        final_response += ai_response + "\n\n"
    
    # Add Delaware-specific information if available and relevant
    if is_delaware_query or DELAWARE_RAG_AVAILABLE:
        delaware_info = await get_delaware_license_info(user_input)
        if delaware_info:
            final_response += delaware_info
    
    # If no AI response, use fallback
    if not ai_response:
        final_response += "## 📋 General Business License Guidance\n\n"
        final_response += get_fallback_response(user_input)
    
    return final_response


def run_agent(user_input):
    """Synchronous wrapper for the async agent"""
    try:
        return asyncio.run(run_agent_async(user_input))
    except Exception as e:
        print(f"Error in agent: {e}")
        return get_fallback_response(user_input)


if __name__ == "__main__":
    # Test the agent
    test_input = "I run a home bakery in Delaware"
    result = run_agent(test_input)
    print("Test result:")
    print(result) 
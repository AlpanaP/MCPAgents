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

# Add the parent directory to the path so we can import tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the generic handlers
try:
    from utils.business_handler import BusinessTypeHandler
    from utils.state_handler import StateHandler
    from utils.mcp_factory import MCPFactory
    
    business_handler = BusinessTypeHandler()
    state_handler = StateHandler()
    mcp_factory = MCPFactory(state_handler)
    
    # Check if Delaware RAG is available for backward compatibility
    try:
        from delaware_rag.delaware_rag_server import DelawareRAGServer
        DELAWARE_RAG_AVAILABLE = True
    except ImportError:
        DELAWARE_RAG_AVAILABLE = False
        print("Warning: Delaware RAG tools not available. Install dependencies with: pip install -r requirements.txt")
        
except ImportError as e:
    print(f"Warning: Generic handlers not available: {e}")
    business_handler = None
    state_handler = None
    mcp_factory = None
    DELAWARE_RAG_AVAILABLE = False


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


async def get_state_license_info(business_description: str) -> Optional[str]:
    """Get state-specific license information using RAG tools and MCP servers."""
    if not state_handler:
        return None
    
    # Validate input
    if not business_description or not isinstance(business_description, str):
        return None
    
    sanitized_description = sanitize_input(business_description)
    if not sanitized_description:
        return None
    
    try:
        # Detect state from query
        state_code = state_handler.detect_state_from_query(sanitized_description)
        if not state_code:
            return None
        
        # Get state configuration
        state_config = state_handler.get_state_config(state_code)
        if not state_config:
            return None
        
        state_name = state_config.get("name", "Unknown State")
        state_type = state_config.get("type", "state")
        
        # Generate state-specific guidance
        business_type = None
        if business_handler:
            business_type = business_handler.detect_business_type(sanitized_description)
        
        state_info = f"## 🏛️ {state_name} {state_type.title()} Business License Information\n\n"
        state_info += f"**Location**: {state_name} ({state_code})\n\n"
        
        # Add state-specific guidance
        state_guidance = state_handler.generate_state_guidance(state_code, sanitized_description, business_type)
        state_info += state_guidance
        
        # Try to get RAG data if available
        if state_handler.is_rag_enabled(state_code) and mcp_factory:
            rag_server = mcp_factory.create_rag_server(state_code)
            if rag_server:
                try:
                    # Get business steps
                    steps_result = await rag_server._get_business_steps()
                    if steps_result and not steps_result.content[0].text.startswith("Error"):
                        state_info += "### 📋 Business Steps:\n"
                        state_info += steps_result.content[0].text.split("Source:")[0] + "\n\n"
                    
                    # Get license categories
                    categories_result = await rag_server._get_license_categories()
                    if categories_result and not categories_result.content[0].text.startswith("Error"):
                        state_info += "### 🏢 Available License Categories:\n"
                        state_info += categories_result.content[0].text.split("Source:")[0] + "\n\n"
                        
                except Exception as e:
                    print(f"Error getting RAG data for {state_code}: {e}")
        
        # Add business type specific guidance if available
        if business_type and business_handler:
            business_guidance = business_handler.generate_business_guidance(business_type, sanitized_description)
            state_info += business_guidance
        
        return state_info
        
    except Exception as e:
        print(f"Error getting state license info: {e}")
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


def get_source_attribution(ai_used, state_rag_used, business_description):
    """Generate source attribution information"""
    sources = []
    location_info = ""
    
    # Use state handler to detect state and business type
    state_code = None
    business_type = None
    
    if state_handler:
        state_code = state_handler.detect_state_from_query(business_description)
        if business_handler:
            business_type = business_handler.detect_business_type(business_description)
    
    if ai_used:
        sources.append(f"**AI Source**: {ai_used}")
    
    if state_rag_used and state_code:
        state_config = state_handler.get_state_config(state_code)
        if state_config:
            state_name = state_config.get("name", "Unknown State")
            state_type = state_config.get("type", "state")
            
            sources.append(f"**{state_name} Data Source**: {state_name} government websites")
            
            if state_handler.is_rag_enabled(state_code):
                sources.append("**Vector Database**: Qdrant with semantic search")
            
            # Add state-specific resources
            resources = state_handler.get_state_resources(state_code)
            for category, resource in resources.items():
                if isinstance(resource, dict):
                    name = resource.get("name", "")
                    url = resource.get("url", "")
                    sources.append(f"**{name}**: [{name}]({url})")
            
            # Add business type specific sources
            if business_type:
                business_sources = state_handler.get_state_sources(state_code, business_type)
                sources.extend(business_sources)
    
    # Detect location from business description
    if state_code:
        state_config = state_handler.get_state_config(state_code)
        if state_config:
            state_name = state_config.get("name", "Unknown State")
            state_type = state_config.get("type", "state")
            country = state_config.get("country", "US")
            
            location_info = f"**Location**: {state_name} ({state_code}), {country}"
            sources.append(f"**State Resources**: {state_name} government websites")
            
            # Add state-specific links
            resources = state_handler.get_state_resources(state_code)
            main_resource = resources.get("main", {})
            if main_resource:
                name = main_resource.get("name", "")
                url = main_resource.get("url", "")
                sources.append(f"**{state_name} Specific Links**: [{name}]({url})")
    
    elif any(word in business_description.lower() for word in ['texas', 'tx']):
        location_info = "**Location**: Texas"
        sources.append("**State Resources**: Texas Secretary of State")
        sources.append("**Texas Specific Links**: [Texas Secretary of State](https://www.sos.state.tx.us/), [Texas Comptroller](https://comptroller.texas.gov/), [Texas Workforce Commission](https://www.twc.texas.gov/)")
    
    elif any(word in business_description.lower() for word in ['california', 'ca', 'cali']):
        location_info = "**Location**: California"
        sources.append("**State Resources**: California Secretary of State")
        sources.append("**California Specific Links**: [CA Secretary of State](https://www.sos.ca.gov/), [CA Department of Tax](https://www.cdtfa.ca.gov/), [CA Employment Development](https://www.edd.ca.gov/)")
    
    elif any(word in business_description.lower() for word in ['ontario', 'on']):
        location_info = "**Location**: Ontario, Canada"
        sources.append("**Province Resources**: Ontario Business Registry")
        sources.append("**Ontario Specific Links**: [Ontario Business Registry](https://www.ontario.ca/page/ontario-business-registry), [Ontario Ministry of Finance](https://www.ontario.ca/page/ministry-finance)")
    
    else:
        location_info = "**Location**: General (Multiple States)"
        sources.append("**Federal Resources**: Small Business Administration (SBA)")
        sources.append("**General Business Resources**: [SBA.gov](https://www.sba.gov/), [BusinessUSA](https://business.usa.gov/)")
    
    # Add federal resources
    sources.append("**Federal Resources**: [Small Business Administration](https://www.sba.gov/), [IRS Business](https://www.irs.gov/businesses)")
    
    return location_info, sources


async def run_agent_async(user_input: str) -> str:
    """Run the agent asynchronously with user input"""
    try:
        # Validate and sanitize input
        if not user_input or not isinstance(user_input, str):
            return "Please provide a valid business description."
        
        sanitized_input = sanitize_input(user_input)
        if not sanitized_input:
            return "Please provide a valid business description."
        
        # Detect state from query
        state_code = None
        is_state_query = False
        if state_handler:
            state_code = state_handler.detect_state_from_query(sanitized_input)
            if not state_code:
                # Try to create dynamic state config for common states
                # Extract potential state codes from the query
                import re
                state_matches = re.findall(r'\b([A-Z]{2})\b', sanitized_input.upper())
                if state_matches:
                    for potential_state in state_matches:
                        state_config = state_handler.get_or_create_state_config(potential_state)
                        if state_config:
                            state_code = potential_state
                            break
            
            is_state_query = state_code is not None
        
        # Get state-specific information if available
        state_info = None
        if is_state_query and state_handler:
            state_info = await get_state_license_info(sanitized_input)
        
        # Generate source attribution
        ai_source = "Gemini"
        state_rag_used = state_info is not None
        
        location_info, sources = get_source_attribution(ai_source, state_rag_used, sanitized_input)
        
        # Build the prompt for AI
        prompt = f"""You are a business license navigation assistant. Provide a structured, summarized response for the user's query.

User Query: {sanitized_input}

{location_info}

Please provide a structured response with the following sections:

## 📋 QUERY SUMMARY
Briefly summarize what the user is asking for.

## 🏢 LICENSES NEEDED
List the specific licenses required with:
- License name and type
- Brief description of what it covers
- **Cost information** (application fees, license fees, renewal fees)
- **Due dates** (when to apply, renewal deadlines)
- Official government URL for application

## 📝 DESCRIPTIONS
Provide clear descriptions of:
- What each license allows you to do
- Key requirements and qualifications
- **Detailed cost breakdown** (fees, taxes, insurance requirements)
- **Timeline information** (processing times, renewal schedules)

## 🔗 OFFICIAL URLs
List all relevant official government websites:
- Main licensing portal
- Application forms
- Requirements pages
- **Fee schedules and payment portals**
- Contact information

## 📋 SEQUENCE
Provide a step-by-step sequence:
1. Business registration steps
2. License application process
3. **Cost timeline** (when fees are due)
4. **Deadline management** (important dates to remember)
5. Timeline estimates
6. Order of operations

## 💡 ADDITIONAL COMMENTS
Include:
- **Budget considerations** (total estimated costs)
- **Payment deadlines** and late fee information
- Important deadlines and timing
- Common pitfalls to avoid
- Pro tips and best practices
- Local considerations
- Contact information for questions

Make sure to include specific, actionable advice and relevant links to official government websites. Focus on providing confidence-building, comprehensive information that helps users understand exactly what they need to do, when they need to do it, and how much it will cost.

Sources used: {', '.join(sources[:5])}  # Limit to first 5 sources for brevity
"""

        # Try to call Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key and validate_api_key(api_key):
            try:
                ai_response = call_gemini(prompt, api_key)
                if not ai_response.startswith("ERROR"):
                    ai_source = "Gemini"
                else:
                    raise Exception(ai_response)
            except Exception as e:
                print(f"Gemini API error: {e}")
                ai_response = get_fallback_response(sanitized_input)
                ai_source = "Fallback"
        else:
            ai_response = get_fallback_response(sanitized_input)
            ai_source = "Fallback"
        
        # Combine AI response with state-specific information
        final_response = f"📍 **Response Sources**: {location_info}\n\n"
        
        if state_info:
            final_response += state_info + "\n\n"
        
        final_response += ai_response
        
        return final_response
        
    except Exception as e:
        print(f"Error in run_agent_async: {e}")
        return f"An error occurred while processing your request. Please try again. Error: {str(e)}"


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
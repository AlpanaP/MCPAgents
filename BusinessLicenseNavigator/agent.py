import requests
import json


def call_ollama(model, prompt):
    """Simple function to call Ollama with a prompt"""
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


def get_fallback_response(business_description):
    """Provide fallback guidance when Ollama is not available"""
    
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


def run_agent(user_input):
    """Run the business license navigator agent"""
    
    # Create a prompt for business license guidance
    prompt = f"""
    You are a helpful business license navigator. A user has provided the following information about their business:
    
    {user_input}
    
    Please provide guidance on:
    1. What type of business license they might need
    2. Any specific permits required
    3. Steps they should take to obtain the necessary licenses
    4. Any additional considerations for their business type and location
    
    Be helpful, specific, and provide actionable advice.
    """
    
    # Try to call Ollama first
    response = call_ollama("llama3.1:8b", prompt)
    
    # If Ollama is not available, use fallback
    if response.startswith("ERROR:"):
        return get_fallback_response(user_input)
    
    return response


if __name__ == "__main__":
    # Test the agent
    test_input = "I run a home bakery in Austin, TX"
    result = run_agent(test_input)
    print("Test result:")
    print(result) 
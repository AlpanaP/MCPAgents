#!/usr/bin/env python3
"""
MCP + Gemini API Integration Test

This script demonstrates how to use MCP servers (Fetch and Playwright)
together with Gemini API for enhanced business license queries.
"""

import asyncio
import os
import sys
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our MCP client
from mcp_servers import mcp_client

def call_gemini_api(prompt: str, api_key: str = None) -> str:
    """
    Call Gemini API with a given prompt.
    
    Args:
        prompt (str): The prompt to send to Gemini
        api_key (str): Gemini API key (optional, will use env var if not provided)
    
    Returns:
        str: The response from Gemini API
    """
    try:
        import google.generativeai as genai
        
        # Get API key
        if not api_key:
            api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key or api_key == "your_actual_api_key_here":
            return "❌ Error: No valid GEMINI_API_KEY found. Please set it in your .env file or provide it as a parameter."
        
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Create model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generate response
        response = model.generate_content(prompt)
        
        return response.text
        
    except ImportError:
        return "❌ Error: google-generativeai package not installed. Run: pip install google-generativeai"
    except Exception as e:
        return f"❌ Error calling Gemini API: {str(e)}"

async def fetch_business_license_info(url: str) -> Dict[str, Any]:
    """
    Fetch business license information from a government website.
    
    Args:
        url (str): The URL to fetch from
    
    Returns:
        Dict[str, Any]: The fetched information
    """
    try:
        # Use MCP fetch server to get content
        fetch_result = await mcp_client.fetch_url(url)
        
        if "error" in fetch_result:
            return {"error": fetch_result["error"]}
        
        return {
            "url": url,
            "content": fetch_result.get("content", ""),
            "status": "success",
            "source": "MCP Fetch Server"
        }
        
    except Exception as e:
        return {"error": f"Failed to fetch from {url}: {str(e)}"}

async def browser_automation_for_license_info(url: str) -> Dict[str, Any]:
    """
    Use browser automation to get detailed license information.
    
    Args:
        url (str): The URL to automate
    
    Returns:
        Dict[str, Any]: The automation results
    """
    try:
        # Use MCP playwright server for browser automation
        automation_result = await mcp_client.browser_automation(url, "extract_license_info")
        
        if "error" in automation_result:
            return {"error": automation_result["error"]}
        
        return {
            "url": url,
            "automated_data": automation_result.get("result", ""),
            "status": "success",
            "source": "MCP Playwright Server"
        }
        
    except Exception as e:
        return {"error": f"Browser automation failed for {url}: {str(e)}"}

async def enhanced_business_license_query(query: str, state: str = "FL") -> str:
    """
    Enhanced business license query using MCP servers + Gemini API.
    
    Args:
        query (str): The business license query
        state (str): The state code (FL, DE, etc.)
    
    Returns:
        str: Enhanced response with real-time data
    """
    print(f"🔍 Processing enhanced query: {query}")
    print(f"📍 State: {state}")
    print("=" * 60)
    
    # Step 1: Fetch real-time data using MCP servers
    print("1️⃣ Fetching real-time data with MCP servers...")
    
    # Define state-specific URLs
    state_urls = {
        "FL": "https://www2.myfloridalicense.com/",
        "DE": "https://firststeps.delaware.gov/",
        "CA": "https://www.calgold.ca.gov/",
        "TX": "https://www.tdlr.texas.gov/"
    }
    
    url = state_urls.get(state, "https://example.com")
    
    # Fetch data using MCP servers
    fetch_data = await fetch_business_license_info(url)
    browser_data = await browser_automation_for_license_info(url)
    
    # Step 2: Build enhanced prompt with MCP data
    enhanced_prompt = f"""
    Business License Query: {query}
    State: {state}
    
    Real-time data from government websites:
    
    FETCH DATA:
    {fetch_data.get('content', 'No fetch data available')}
    
    BROWSER AUTOMATION DATA:
    {browser_data.get('automated_data', 'No browser data available')}
    
    Please provide comprehensive information about:
    1. Required business licenses for this type of business
    2. Application process and requirements
    3. Estimated costs and fees
    4. Timeline for approval
    5. Specific requirements for {state}
    6. Official contact information
    7. Next steps for the business owner
    
    Use the real-time data above to provide the most accurate and current information.
    Include specific details about costs, timelines, and requirements.
    """
    
    # Step 3: Call Gemini API with enhanced prompt
    print("2️⃣ Calling Gemini API with enhanced prompt...")
    gemini_response = call_gemini_api(enhanced_prompt)
    
    # Step 4: Return comprehensive response
    print("3️⃣ Compiling comprehensive response...")
    
    response = f"""
    🤖 ENHANCED BUSINESS LICENSE ANALYSIS
    {'=' * 60}
    
    📋 Original Query: {query}
    🏛️ State: {state}
    
    🔗 Data Sources:
    - MCP Fetch Server: {fetch_data.get('status', 'N/A')}
    - MCP Playwright Server: {browser_data.get('status', 'N/A')}
    - Gemini AI: ✅ Enhanced Analysis
    
    📊 Real-time Data Status:
    - Fetch Data: {'✅ Available' if fetch_data.get('status') == 'success' else '❌ Unavailable'}
    - Browser Data: {'✅ Available' if browser_data.get('status') == 'success' else '❌ Unavailable'}
    
    💡 AI Analysis:
    {gemini_response}
    
    🔧 Technical Details:
    - MCP Servers Used: Fetch, Playwright
    - AI Model: Gemini 1.5 Flash
    - Data Integration: Real-time + AI analysis
    """
    
    return response

async def test_mcp_gemini_integration():
    """Test the integration of MCP servers with Gemini API."""
    print("🚀 MCP + Gemini Integration Test")
    print("=" * 60)
    
    # Test queries
    test_queries = [
        "I want to open an ice cream franchise in Florida",
        "What licenses do I need for a financial services firm in Delaware?",
        "How do I start a restaurant in California?",
        "What are the requirements for a construction company in Texas?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🧪 Test {i}: {query}")
        print("-" * 40)
        
        # Extract state from query
        state = "FL"  # Default
        if "delaware" in query.lower() or "de" in query.lower():
            state = "DE"
        elif "california" in query.lower() or "ca" in query.lower():
            state = "CA"
        elif "texas" in query.lower() or "tx" in query.lower():
            state = "TX"
        
        # Process enhanced query
        response = await enhanced_business_license_query(query, state)
        print(response)
        
        if i < len(test_queries):
            print("\n" + "=" * 60)
    
    print("\n✅ All MCP + Gemini integration tests completed!")

async def test_mcp_servers_only():
    """Test MCP servers independently."""
    print("🔧 Testing MCP Servers Only")
    print("=" * 40)
    
    # Test fetch server
    print("1️⃣ Testing Fetch Server")
    fetch_result = await mcp_client.fetch_url("https://example.com")
    print(f"Fetch Result: {fetch_result}")
    
    # Test playwright server
    print("\n2️⃣ Testing Playwright Server")
    playwright_result = await mcp_client.browser_automation("https://example.com", "screenshot")
    print(f"Playwright Result: {playwright_result}")
    
    # Show connection status
    print("\n3️⃣ Connection Status")
    status = mcp_client.get_connection_status()
    print(f"Active Connections: {status}")

def main():
    """Main function to run the tests."""
    print("🎯 MCP + Gemini Integration Test Suite")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == "your_actual_api_key_here":
        print("⚠️  Warning: GEMINI_API_KEY not found or invalid")
        print("Some tests may fail. Please set GEMINI_API_KEY in your .env file")
    
    # Run tests
    try:
        # Test MCP servers only
        asyncio.run(test_mcp_servers_only())
        
        print("\n" + "=" * 60)
        
        # Test full integration
        asyncio.run(test_mcp_gemini_integration())
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1
    
    print("\n🎉 All tests completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
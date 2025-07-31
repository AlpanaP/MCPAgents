#!/usr/bin/env python3
"""
Gemini API Test Script
Tests the Gemini API with a sample business license query.
"""

import os
import sys
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

def test_business_license_query(api_key: str = None):
    """Test with a sample business license query."""
    
    # Sample query
    sample_query = """
    I want to open an ice cream franchise in Florida. 
    Please provide information about:
    1. Required business licenses
    2. Application process
    3. Estimated costs
    4. Timeline for approval
    5. Any specific requirements for food service businesses
    """
    
    print("🧪 Testing Gemini API with Business License Query")
    print("=" * 60)
    print(f"📝 Query: {sample_query.strip()}")
    print("=" * 60)
    
    # Call Gemini API
    response = call_gemini_api(sample_query, api_key)
    
    print("🤖 Gemini Response:")
    print("=" * 60)
    print(response)
    print("=" * 60)
    
    return response

def test_simple_query(api_key: str = None):
    """Test with a simple query to verify API connectivity."""
    
    simple_query = "Hello! Can you tell me about business licenses in Florida?"
    
    print("🧪 Testing Gemini API with Simple Query")
    print("=" * 60)
    print(f"📝 Query: {simple_query}")
    print("=" * 60)
    
    # Call Gemini API
    response = call_gemini_api(simple_query, api_key)
    
    print("🤖 Gemini Response:")
    print("=" * 60)
    print(response)
    print("=" * 60)
    
    return response

def get_api_key_from_user():
    """Get API key from user input if not found in environment."""
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key or api_key == "your_actual_api_key_here":
        print("🔑 No valid GEMINI_API_KEY found in environment.")
        print("Please enter your Gemini API key (or press Enter to skip):")
        api_key = input("API Key: ").strip()
        
        if not api_key:
            print("⚠️  No API key provided. Tests will fail.")
            return None
    
    return api_key

def main():
    """Main function to run the tests."""
    
    print("🚀 Gemini API Test Script")
    print("=" * 60)
    
    # Get API key
    api_key = get_api_key_from_user()
    
    if not api_key:
        print("\n❌ Cannot proceed without API key.")
        print("Please set GEMINI_API_KEY in your .env file or provide it when prompted.")
        return
    
    # Test simple query first
    print("\n1️⃣ Testing Simple Query...")
    simple_result = test_simple_query(api_key)
    
    # Test business license query
    print("\n2️⃣ Testing Business License Query...")
    business_result = test_business_license_query(api_key)
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 60)
    if "❌ Error" in simple_result:
        print("❌ Simple Query: FAILED")
    else:
        print("✅ Simple Query: SUCCESS")
    
    if "❌ Error" in business_result:
        print("❌ Business Query: FAILED")
    else:
        print("✅ Business Query: SUCCESS")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 
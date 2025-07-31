#!/usr/bin/env python3
"""
Simple Gemini API Test
Quick test to verify Gemini API connectivity and response.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_simple():
    """Simple test of Gemini API."""
    try:
        import google.generativeai as genai
        
        # Get API key
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            print("❌ No GEMINI_API_KEY found in environment")
            return False
        
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Create model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Simple test query
        test_query = "Hello! Can you give me a brief overview of business licensing in Florida?"
        
        print("🧪 Testing Gemini API...")
        print(f"📝 Query: {test_query}")
        
        # Generate response
        response = model.generate_content(test_query)
        
        print("✅ Gemini API Test SUCCESS!")
        print("📄 Response Preview:")
        print("-" * 50)
        print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
        print("-" * 50)
        
        return True
        
    except ImportError:
        print("❌ google-generativeai package not installed")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_gemini_simple()
    if success:
        print("\n🎉 Gemini API is working correctly!")
    else:
        print("\n💥 Gemini API test failed!") 
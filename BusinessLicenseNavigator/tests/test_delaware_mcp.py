#!/usr/bin/env python3
"""
Test script for Delaware MCP tools
Tests the Delaware MCP server functionality
"""

import asyncio
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from delaware_rag.delaware_mcp_server import DelawareLicenseServer

async def test_delaware_tools():
    """Test the Delaware MCP tools."""
    server = DelawareLicenseServer()
    
    print("🧪 Testing Delaware MCP Tools")
    print("=" * 50)
    
    # Test 1: Get license categories
    print("\n1. Testing get_delaware_license_categories...")
    try:
        result = await server._get_license_categories()
        print("✅ Categories retrieved successfully")
        print(f"Result: {result.content[0].text[:200]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Search for food licenses
    print("\n2. Testing search_delaware_licenses with 'food'...")
    try:
        result = await server._search_licenses({"query": "food"})
        print("✅ Food license search completed")
        print(f"Result: {result.content[0].text[:200]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Get business steps
    print("\n3. Testing get_delaware_business_steps...")
    try:
        result = await server._get_business_steps()
        print("✅ Business steps retrieved successfully")
        print(f"Result: {result.content[0].text[:200]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Get license details for Food category
    print("\n4. Testing get_delaware_license_details for 'Food'...")
    try:
        result = await server._get_license_details({"category": "Food"})
        print("✅ Food license details retrieved")
        print(f"Result: {result.content[0].text[:200]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Delaware MCP Tools Test Complete!")

def main():
    """Main function to run the test."""
    print("Starting Delaware MCP Tools Test...")
    asyncio.run(test_delaware_tools())

if __name__ == "__main__":
    main() 
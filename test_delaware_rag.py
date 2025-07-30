#!/usr/bin/env python3
"""
Test script for Delaware RAG MCP tools with Qdrant
Demonstrates how to use the Delaware business license MCP server with RAG capabilities using Qdrant
"""

import asyncio
import json
import sys
from delaware_rag_server import DelawareRAGServer

async def test_delaware_rag_tools():
    """Test the Delaware RAG MCP tools with Qdrant."""
    server = DelawareRAGServer()
    
    print("🧪 Testing Delaware RAG MCP Tools with Qdrant")
    print("=" * 70)
    
    # Test 1: Get license categories
    print("\n1. Testing get_delaware_license_categories...")
    try:
        result = await server._get_license_categories()
        print("✅ Categories retrieved successfully")
        print(f"Result: {result.content[0].text[:200]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: RAG-powered search for food licenses
    print("\n2. Testing search_delaware_licenses_rag with 'restaurant'...")
    try:
        result = await server._search_licenses_rag({"query": "restaurant", "top_k": 3})
        print("✅ RAG-powered restaurant search completed")
        print(f"Result: {result.content[0].text[:300]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: RAG-powered search for health licenses
    print("\n3. Testing search_delaware_licenses_rag with 'health'...")
    try:
        result = await server._search_licenses_rag({"query": "health", "top_k": 3})
        print("✅ RAG-powered health search completed")
        print(f"Result: {result.content[0].text[:300]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Get similar licenses
    print("\n4. Testing get_similar_licenses for 'Food Establishments'...")
    try:
        result = await server._get_similar_licenses({"license_type": "Food Establishments", "top_k": 3})
        print("✅ Similar licenses search completed")
        print(f"Result: {result.content[0].text[:300]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Get business steps
    print("\n5. Testing get_delaware_business_steps...")
    try:
        result = await server._get_business_steps()
        print("✅ Business steps retrieved successfully")
        print(f"Result: {result.content[0].text[:200]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 6: Get license details for Food category
    print("\n6. Testing get_delaware_license_details for 'Food'...")
    try:
        result = await server._get_license_details({"category": "Food"})
        print("✅ Food license details retrieved")
        print(f"Result: {result.content[0].text[:200]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("✅ Delaware RAG MCP Tools with Qdrant Test Complete!")
    
    # Print RAG status with Qdrant information
    if server.embedding_model and server.qdrant_client:
        print("🎯 RAG System Status: ✅ Active")
        print("   - Embedding Model: all-MiniLM-L6-v2")
        print("   - Vector Database: Qdrant")
        print("   - Semantic Search: Enabled")
        print("   - Similarity Search: Enabled")
        
        # Check Qdrant connection type
        try:
            collections = server.qdrant_client.get_collections()
            print(f"   - Qdrant Collections: {len(collections.collections)}")
            print(f"   - Delaware Collection: {'✅' if any(col.name == 'delaware_licenses' for col in collections.collections) else '❌'}")
        except Exception as e:
            print(f"   - Qdrant Status: In-memory mode")
    else:
        print("⚠️  RAG System Status: Fallback Mode")
        print("   - Using web scraping fallback")

def main():
    """Main function to run the test."""
    print("Starting Delaware RAG MCP Tools with Qdrant Test...")
    asyncio.run(test_delaware_rag_tools())

if __name__ == "__main__":
    main() 
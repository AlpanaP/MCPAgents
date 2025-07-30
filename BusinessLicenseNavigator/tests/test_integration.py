#!/usr/bin/env python3
"""
Integration test script for Business License Navigator
Tests all major components and functionality
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported successfully."""
    print("🧪 Testing imports...")
    
    try:
        from agent import run_agent, DELAWARE_RAG_AVAILABLE
        print("✅ Agent module imported successfully")
    except ImportError as e:
        print(f"❌ Agent import failed: {e}")
        return False
    
    try:
        import streamlit_app
        print("✅ Streamlit app imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit app import failed: {e}")
        return False
    
    try:
        from delaware_rag.delaware_rag_server import DelawareRAGServer
        print("✅ Delaware RAG server imported successfully")
    except ImportError as e:
        print(f"❌ Delaware RAG server import failed: {e}")
        return False
    
    try:
        from delaware_rag.delaware_mcp_server import DelawareLicenseServer
        print("✅ Delaware MCP server imported successfully")
    except ImportError as e:
        print(f"❌ Delaware MCP server import failed: {e}")
        return False
    
    return True

def test_agent_functionality():
    """Test the main agent functionality."""
    print("\n🧪 Testing agent functionality...")
    
    try:
        from agent import run_agent
        
        # Test Delaware query
        result = run_agent("I run a home bakery in Delaware")
        if result and len(result) > 100:
            print("✅ Delaware query processed successfully")
        else:
            print("❌ Delaware query failed")
            return False
        
        # Test general query
        result = run_agent("I want to start a consulting business")
        if result and len(result) > 100:
            print("✅ General query processed successfully")
        else:
            print("❌ General query failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Agent functionality test failed: {e}")
        return False

def test_delaware_rag():
    """Test Delaware RAG functionality."""
    print("\n🧪 Testing Delaware RAG...")
    
    try:
        from delaware_rag.delaware_rag_server import DelawareRAGServer
        import asyncio
        
        async def test_rag():
            server = DelawareRAGServer()
            
            # Test license categories
            result = await server._get_license_categories()
            if result and not result.content[0].text.startswith("Error"):
                print("✅ License categories retrieved")
            else:
                print("❌ License categories failed")
                return False
            
            # Test business steps
            result = await server._get_business_steps()
            if result and not result.content[0].text.startswith("Error"):
                print("✅ Business steps retrieved")
            else:
                print("❌ Business steps failed")
                return False
            
            return True
        
        success = asyncio.run(test_rag())
        return success
        
    except Exception as e:
        print(f"❌ Delaware RAG test failed: {e}")
        return False

def test_delaware_mcp():
    """Test Delaware MCP functionality."""
    print("\n🧪 Testing Delaware MCP...")
    
    try:
        from delaware_rag.delaware_mcp_server import DelawareLicenseServer
        import asyncio
        
        async def test_mcp():
            server = DelawareLicenseServer()
            
            # Test license categories
            result = await server._get_license_categories()
            if result and not result.content[0].text.startswith("Error"):
                print("✅ MCP license categories retrieved")
            else:
                print("❌ MCP license categories failed")
                return False
            
            return True
        
        success = asyncio.run(test_mcp())
        return success
        
    except Exception as e:
        print(f"❌ Delaware MCP test failed: {e}")
        return False

def test_configuration():
    """Test configuration files."""
    print("\n🧪 Testing configuration...")
    
    try:
        # Test license sources config
        import json
        with open('config/license_sources.json', 'r') as f:
            config = json.load(f)
            if 'sources' in config and 'delaware' in config['sources']:
                print("✅ License sources configuration valid")
            else:
                print("❌ License sources configuration invalid")
                return False
        
        # Test MCP config
        with open('config/delaware_mcp.json', 'r') as f:
            config = json.load(f)
            if 'mcpServers' in config:
                print("✅ MCP configuration valid")
            else:
                print("❌ MCP configuration invalid")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def run_integration_tests():
    """Wrapper function for test runner."""
    return main()

def main():
    """Run all integration tests."""
    print("🚀 Business License Navigator Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Agent Functionality", test_agent_functionality),
        ("Delaware RAG", test_delaware_rag),
        ("Delaware MCP", test_delaware_mcp),
        ("Configuration", test_configuration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        if test_func():
            print(f"✅ {test_name} test passed")
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
"""
Tests for the generic system functionality.

This module tests the generic state/province detection, industry matching,
and dynamic configuration capabilities.
"""

import sys
import os
from typing import Dict, Any, List

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_config import TestLogger, get_test_query, validate_test_result, get_expected_keywords

def test_generic_state_detection():
    """Test generic state detection functionality."""
    logger = TestLogger("Generic State Detection")
    
    try:
        from utils.state_handler import StateHandler
        
        state_handler = StateHandler()
        
        # Test known states
        test_cases = [
            ("I want to open a business in New York", "NY"),
            ("I want to start a restaurant in Illinois", "IL"),
            ("I want to open a beauty salon in California", "CA"),
            ("I want to start a construction company in Texas", "TX"),
            ("I want to open a restaurant in Florida", "FL")
        ]
        
        for query, expected_state in test_cases:
            detected_state = state_handler.detect_state_from_query(query)
            if detected_state == expected_state:
                logger.success(f"Correctly detected {expected_state} in: '{query}'")
            else:
                logger.error(f"Failed to detect {expected_state} in: '{query}' (got: {detected_state})")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"State detection test failed: {e}")
        return False

def test_generic_industry_detection():
    """Test generic industry detection functionality."""
    logger = TestLogger("Generic Industry Detection")
    
    try:
        from utils.business_handler import BusinessTypeHandler
        
        business_handler = BusinessTypeHandler()
        
        # Test industry detection
        test_cases = [
            ("I want to open a construction company", "construction"),
            ("I want to start a restaurant", "food_service"),
            ("I want to open a beauty salon", "beauty"),
            ("I want to start a real estate business", "real_estate"),
            ("I want to open a healthcare clinic", "healthcare")
        ]
        
        for query, expected_industry in test_cases:
            detected_industry = business_handler.detect_business_type(query)
            if detected_industry == expected_industry:
                logger.success(f"Correctly detected {expected_industry} in: '{query}'")
            else:
                logger.error(f"Failed to detect {expected_industry} in: '{query}' (got: {detected_industry})")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Industry detection test failed: {e}")
        return False

def test_generic_agent_queries():
    """Test generic agent queries for various states and industries."""
    logger = TestLogger("Generic Agent Queries")
    
    try:
        from agent import run_agent
        
        # Test queries for different states and industries
        test_queries = [
            ("I want to open a construction company in New York", ["construction", "new york"]),
            ("I want to start a restaurant in Illinois", ["restaurant", "illinois"]),
            ("I want to open a beauty salon in California", ["beauty", "california"]),
            ("I want to start a real estate business in Texas", ["real estate", "texas"]),
            ("I want to open a healthcare clinic in Florida", ["healthcare", "florida"])
        ]
        
        for query, expected_keywords in test_queries:
            logger.info(f"Testing query: '{query}'")
            
            result = run_agent(query)
            
            if validate_test_result(result, expected_keywords):
                logger.success(f"Query processed successfully: '{query}'")
            else:
                logger.error(f"Query failed validation: '{query}'")
                logger.error(f"Expected keywords: {expected_keywords}")
                logger.error(f"Result: {result[:200]}...")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Generic agent queries test failed: {e}")
        return False

def test_dynamic_state_creation():
    """Test dynamic state configuration creation."""
    logger = TestLogger("Dynamic State Creation")
    
    try:
        from utils.state_handler import StateHandler
        
        state_handler = StateHandler()
        
        # Test dynamic state creation for states not in config
        test_states = [
            ("NY", "New York"),
            ("IL", "Illinois"),
            ("CA", "California"),
            ("TX", "Texas"),
            ("WA", "Washington")
        ]
        
        for state_code, state_name in test_states:
            # Try to get or create state config
            state_config = state_handler.get_or_create_state_config(state_code)
            
            if state_config:
                logger.success(f"Successfully created config for {state_code} ({state_name})")
                
                # Verify basic config structure
                required_fields = ["name", "type", "country", "capabilities"]
                for field in required_fields:
                    if field in state_config:
                        logger.info(f"  ✅ {field}: {state_config[field]}")
                    else:
                        logger.error(f"  ❌ Missing required field: {field}")
                        return False
            else:
                logger.error(f"Failed to create config for {state_code}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Dynamic state creation test failed: {e}")
        return False

def test_generic_rag_server():
    """Test generic RAG server functionality."""
    logger = TestLogger("Generic RAG Server")
    
    try:
        from generic_rag.generic_rag_server import GenericRAGServer
        import asyncio
        
        # Create a test state config
        test_state_config = {
            "name": "Test State",
            "type": "state",
            "country": "US",
            "industry_patterns": {
                "construction": {
                    "keywords": ["construction", "contractor"],
                    "license_types": ["General Contractor"],
                    "requirements": ["Background check"],
                    "fees": ["Application fee"]
                }
            },
            "url_patterns": {
                "main_license_site": "https://teststate.gov/",
                "application_portal": "https://teststate.gov/apply/",
                "requirements": "https://teststate.gov/requirements/"
            }
        }
        
        # Initialize generic RAG server
        rag_server = GenericRAGServer(test_state_config)
        
        # Test business steps
        steps_result = asyncio.run(rag_server._get_business_steps())
        if steps_result and steps_result.content:
            logger.success("Generic RAG server business steps test passed")
        else:
            logger.error("Generic RAG server business steps test failed")
            return False
        
        # Test license categories
        categories_result = asyncio.run(rag_server._get_license_categories())
        if categories_result and categories_result.content:
            logger.success("Generic RAG server license categories test passed")
        else:
            logger.error("Generic RAG server license categories test failed")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Generic RAG server test failed: {e}")
        return False

def test_generic_mcp_server():
    """Test generic MCP server functionality."""
    logger = TestLogger("Generic MCP Server")
    
    try:
        from generic_rag.generic_mcp_server import GenericLicenseServer
        import asyncio
        
        # Create a test state config
        test_state_config = {
            "name": "Test State",
            "type": "state",
            "country": "US",
            "industry_patterns": {
                "construction": {
                    "keywords": ["construction", "contractor"],
                    "license_types": ["General Contractor"],
                    "requirements": ["Background check"],
                    "fees": ["Application fee"]
                }
            },
            "url_patterns": {
                "main_license_site": "https://teststate.gov/",
                "application_portal": "https://teststate.gov/apply/",
                "requirements": "https://teststate.gov/requirements/"
            }
        }
        
        # Initialize generic MCP server
        mcp_server = GenericLicenseServer(test_state_config)
        
        # Test tool listing
        tools = mcp_server.list_tools()
        if tools and len(tools) > 0:
            logger.success(f"Generic MCP server has {len(tools)} tools available")
        else:
            logger.error("Generic MCP server has no tools")
            return False
        
        # Test license summary tool
        summary_result = asyncio.run(mcp_server._get_license_summary("construction", "Test State"))
        if summary_result and summary_result.content:
            logger.success("Generic MCP server license summary test passed")
        else:
            logger.error("Generic MCP server license summary test failed")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Generic MCP server test failed: {e}")
        return False

def run_generic_system_tests():
    """Run all generic system tests."""
    print("🧪 Running Generic System Tests")
    print("=" * 50)
    
    tests = [
        ("Generic State Detection", test_generic_state_detection),
        ("Generic Industry Detection", test_generic_industry_detection),
        ("Generic Agent Queries", test_generic_agent_queries),
        ("Dynamic State Creation", test_dynamic_state_creation),
        ("Generic RAG Server", test_generic_rag_server),
        ("Generic MCP Server", test_generic_mcp_server)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            if test_func():
                print(f"✅ {test_name} passed")
                passed += 1
            else:
                print(f"❌ {test_name} failed")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            failed += 1
    
    print(f"\n📊 Generic System Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All generic system tests passed!")
        return True
    else:
        print(f"⚠️  {failed} generic system test(s) failed.")
        return False

if __name__ == "__main__":
    run_generic_system_tests() 
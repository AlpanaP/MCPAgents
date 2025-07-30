#!/usr/bin/env python3
"""
Test runner for Business License Navigator.

Usage:
    python tests/run_tests.py                    # Run all tests
    python tests/run_tests.py --unit             # Run unit tests only
    python tests/run_tests.py --integration      # Run integration tests only
    python tests/run_tests.py --delaware         # Run Delaware-specific tests
    python tests/run_tests.py --generic          # Run generic system tests
"""

import sys
import os
import argparse
import time
from typing import List, Dict, Any

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_unit_tests() -> Dict[str, Any]:
    """Run unit tests for individual components."""
    print("🧪 Running Unit Tests...")
    results = {"passed": 0, "failed": 0, "errors": []}
    
    try:
        # Test imports
        from agent import run_agent
        print("✅ Agent module imported successfully")
        results["passed"] += 1
    except Exception as e:
        print(f"❌ Agent module import failed: {e}")
        results["failed"] += 1
        results["errors"].append(f"Agent import: {e}")
    
    try:
        from utils.state_handler import StateHandler
        state_handler = StateHandler()
        print("✅ StateHandler imported and initialized successfully")
        results["passed"] += 1
    except Exception as e:
        print(f"❌ StateHandler test failed: {e}")
        results["failed"] += 1
        results["errors"].append(f"StateHandler: {e}")
    
    try:
        from utils.business_handler import BusinessTypeHandler
        business_handler = BusinessTypeHandler()
        print("✅ BusinessTypeHandler imported and initialized successfully")
        results["passed"] += 1
    except Exception as e:
        print(f"❌ BusinessTypeHandler test failed: {e}")
        results["failed"] += 1
        results["errors"].append(f"BusinessTypeHandler: {e}")
    
    try:
        from utils.mcp_factory import MCPFactory
        mcp_factory = MCPFactory(StateHandler())
        print("✅ MCPFactory imported and initialized successfully")
        results["passed"] += 1
    except Exception as e:
        print(f"❌ MCPFactory test failed: {e}")
        results["failed"] += 1
        results["errors"].append(f"MCPFactory: {e}")
    
    return results

def run_delaware_tests() -> Dict[str, Any]:
    """Run Delaware-specific tests."""
    print("🧪 Running Delaware Tests...")
    results = {"passed": 0, "failed": 0, "errors": []}
    
    try:
        from test_delaware_rag import test_delaware_rag
        test_delaware_rag()
        print("✅ Delaware RAG tests passed")
        results["passed"] += 1
    except Exception as e:
        print(f"❌ Delaware RAG tests failed: {e}")
        results["failed"] += 1
        results["errors"].append(f"Delaware RAG: {e}")
    
    try:
        from test_delaware_mcp import test_delaware_mcp
        test_delaware_mcp()
        print("✅ Delaware MCP tests passed")
        results["passed"] += 1
    except Exception as e:
        print(f"❌ Delaware MCP tests failed: {e}")
        results["failed"] += 1
        results["errors"].append(f"Delaware MCP: {e}")
    
    return results

def run_generic_tests() -> Dict[str, Any]:
    """Run generic system tests."""
    print("🧪 Running Generic System Tests...")
    results = {"passed": 0, "failed": 0, "errors": []}
    
    try:
        from test_generic_system import run_generic_system_tests
        if run_generic_system_tests():
            print("✅ Generic system tests passed")
            results["passed"] += 1
        else:
            print("❌ Generic system tests failed")
            results["failed"] += 1
            results["errors"].append("Generic system tests failed")
    except Exception as e:
        print(f"❌ Generic system tests failed: {e}")
        results["failed"] += 1
        results["errors"].append(f"Generic system tests: {e}")
    
    return results

def run_integration_tests() -> Dict[str, Any]:
    """Run integration tests."""
    print("🧪 Running Integration Tests...")
    results = {"passed": 0, "failed": 0, "errors": []}
    
    try:
        from test_integration import run_integration_tests
        run_integration_tests()
        print("✅ Integration tests passed")
        results["passed"] += 1
    except Exception as e:
        print(f"❌ Integration tests failed: {e}")
        results["failed"] += 1
        results["errors"].append(f"Integration: {e}")
    
    return results

def run_all_tests() -> Dict[str, Any]:
    """Run all tests."""
    print("🚀 Business License Navigator - Complete Test Suite")
    print("=" * 60)
    
    start_time = time.time()
    total_results = {"passed": 0, "failed": 0, "errors": []}
    
    # Run all test categories
    test_categories = [
        ("Unit Tests", run_unit_tests),
        ("Delaware Tests", run_delaware_tests),
        ("Generic System Tests", run_generic_tests),
        ("Integration Tests", run_integration_tests)
    ]
    
    for category_name, test_function in test_categories:
        print(f"\n📋 Running {category_name}...")
        results = test_function()
        
        total_results["passed"] += results["passed"]
        total_results["failed"] += results["failed"]
        total_results["errors"].extend(results["errors"])
        
        print(f"✅ {category_name}: {results['passed']} passed, {results['failed']} failed")
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    print(f"✅ Passed: {total_results['passed']}")
    print(f"❌ Failed: {total_results['failed']}")
    print(f"⏱️  Duration: {duration:.2f} seconds")
    
    if total_results["errors"]:
        print("\n🔍 Error Details:")
        for error in total_results["errors"]:
            print(f"  - {error}")
    
    if total_results["failed"] == 0:
        print("\n🎉 All tests passed! The system is ready to use.")
    else:
        print(f"\n⚠️  {total_results['failed']} test(s) failed. Please review the errors above.")
    
    return total_results

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run Business License Navigator tests")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--delaware", action="store_true", help="Run Delaware tests only")
    parser.add_argument("--generic", action="store_true", help="Run generic system tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    
    args = parser.parse_args()
    
    if args.unit:
        run_unit_tests()
    elif args.delaware:
        run_delaware_tests()
    elif args.generic:
        run_generic_tests()
    elif args.integration:
        run_integration_tests()
    else:
        run_all_tests()

if __name__ == "__main__":
    main() 
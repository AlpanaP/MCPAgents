#!/usr/bin/env python3
"""
System Test Runner for Business License Navigator.

Run this script to execute comprehensive system tests and check results.
"""

import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_system import run_system_tests


def main():
    """Main function to run system tests."""
    print("🚀 Business License Navigator - System Test Runner")
    print("=" * 60)
    print("This will test the entire organized structure including:")
    print("✅ Core imports and models")
    print("✅ Configuration loading")
    print("✅ Server factory functionality")
    print("✅ RAG and MCP server creation")
    print("✅ Package structure")
    print("✅ File organization")
    print("=" * 60)
    
    try:
        success = run_system_tests()
        
        if success:
            print("\n🎉 All system tests passed! The organized structure is working correctly.")
            print("✅ Core components are properly organized")
            print("✅ Configuration files are valid")
            print("✅ Server factory is functional")
            print("✅ Package structure is clean")
            print("✅ File organization is correct")
        else:
            print("\n⚠️  Some system tests failed. Please check the errors above.")
            print("🔧 Review the failed tests and fix any issues.")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️  System tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ System test runner failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 
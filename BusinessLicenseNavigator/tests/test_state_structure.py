#!/usr/bin/env python3
"""
Test script for the new state structure.

This script verifies that:
1. All states are properly configured
2. RAG and MCP servers can be created
3. State enable/disable functionality works
4. Configuration files are valid
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.core.config_manager import config_manager
from src.core.factories.server_factory import ServerFactory


def test_configuration_files():
    """Test that all configuration files are valid JSON."""
    print("🔍 Testing configuration files...")
    
    config_files = [
        "src/config/app_config.json",
        "src/config/states.json",
        "src/config/rag_servers.json",
        "src/config/mcp_servers.json"
    ]
    
    for config_file in config_files:
        file_path = project_root / config_file
        if not file_path.exists():
            print(f"❌ Configuration file not found: {config_file}")
            return False
        
        try:
            with open(file_path, 'r') as f:
                json.load(f)
            print(f"✅ {config_file} is valid JSON")
        except json.JSONDecodeError as e:
            print(f"❌ {config_file} has invalid JSON: {e}")
            return False
    
    return True


def test_state_directories():
    """Test that state directories exist and have required files."""
    print("\n📁 Testing state directories...")
    
    rag_servers_dir = project_root / "rag" / "servers"
    if not rag_servers_dir.exists():
        print(f"❌ RAG servers directory not found: {rag_servers_dir}")
        return False
    
    # Check for required directories
    required_dirs = ["delaware", "florida", "generic", "template"]
    for dir_name in required_dirs:
        dir_path = rag_servers_dir / dir_name
        if not dir_path.exists():
            print(f"❌ Required directory not found: {dir_name}")
            return False
        
        # Check for required files
        required_files = ["__init__.py"]
        if dir_name != "template":
            required_files.extend([f"{dir_name}_rag_server.py", f"{dir_name}_mcp_server.py"])
        
        for file_name in required_files:
            file_path = dir_path / file_name
            if not file_path.exists():
                print(f"❌ Required file not found: {dir_name}/{file_name}")
                return False
        
        print(f"✅ {dir_name} directory and files exist")
    
    return True


def test_config_manager():
    """Test the configuration manager functionality."""
    print("\n⚙️ Testing configuration manager...")
    
    try:
        # Test enabled states
        enabled_states = config_manager.get_enabled_states()
        print(f"✅ Enabled states: {enabled_states}")
        
        # Test state enable/disable
        test_state = "TEST"
        if config_manager.is_state_enabled(test_state):
            config_manager.disable_state(test_state)
        
        config_manager.enable_state(test_state)
        if not config_manager.is_state_enabled(test_state):
            print(f"❌ Failed to enable state: {test_state}")
            return False
        
        config_manager.disable_state(test_state)
        if config_manager.is_state_enabled(test_state):
            print(f"❌ Failed to disable state: {test_state}")
            return False
        
        print("✅ State enable/disable functionality works")
        
        # Test feature flags
        config_manager.enable_feature("test_feature")
        if not config_manager.get_feature_flag("test_feature"):
            print("❌ Failed to enable feature flag")
            return False
        
        config_manager.disable_feature("test_feature")
        if config_manager.get_feature_flag("test_feature"):
            print("❌ Failed to disable feature flag")
            return False
        
        print("✅ Feature flag functionality works")
        
    except Exception as e:
        print(f"❌ Configuration manager test failed: {e}")
        return False
    
    return True


def test_server_factory():
    """Test the server factory functionality."""
    print("\n🏭 Testing server factory...")
    
    try:
        factory = ServerFactory()
        
        # Test RAG server creation
        rag_servers = factory.get_available_rag_servers()
        print(f"✅ Available RAG servers: {rag_servers}")
        
        # Test MCP server creation
        mcp_servers = factory.get_available_mcp_servers()
        print(f"✅ Available MCP servers: {mcp_servers}")
        
        # Test server groups
        server_groups = factory.get_server_groups()
        print(f"✅ Server groups: {list(server_groups.keys())}")
        
        # Test creating servers for a state
        servers = factory.create_servers_for_state("DE")
        if not servers:
            print("❌ Failed to create servers for Delaware")
            return False
        
        print("✅ Server factory functionality works")
        
    except Exception as e:
        print(f"❌ Server factory test failed: {e}")
        return False
    
    return True


def test_state_servers():
    """Test creating servers for each enabled state."""
    print("\n🌍 Testing state servers...")
    
    try:
        factory = ServerFactory()
        enabled_states = config_manager.get_enabled_states()
        
        for state_code in enabled_states:
            print(f"Testing {state_code}...")
            
            # Test RAG server
            rag_server_name = f"{state_code.lower()}_rag_server"
            rag_server = factory.create_rag_server(rag_server_name)
            if rag_server:
                print(f"✅ {state_code} RAG server created successfully")
            else:
                print(f"⚠️ {state_code} RAG server not available (using generic)")
            
            # Test MCP server
            mcp_server_name = f"{state_code.lower()}_license_server"
            mcp_server = factory.create_mcp_server(mcp_server_name)
            if mcp_server:
                print(f"✅ {state_code} MCP server created successfully")
            else:
                print(f"⚠️ {state_code} MCP server not available (using generic)")
        
        print("✅ State server testing completed")
        
    except Exception as e:
        print(f"❌ State server test failed: {e}")
        return False
    
    return True


def test_template_structure():
    """Test that the template structure is properly set up."""
    print("\n📋 Testing template structure...")
    
    template_dir = project_root / "rag" / "servers" / "template"
    if not template_dir.exists():
        print("❌ Template directory not found")
        return False
    
    required_files = [
        "__init__.py",
        "template_rag_server.py",
        "template_mcp_server.py"
    ]
    
    for file_name in required_files:
        file_path = template_dir / file_name
        if not file_path.exists():
            print(f"❌ Template file not found: {file_name}")
            return False
    
    print("✅ Template structure is properly set up")
    return True


def main():
    """Run all tests."""
    print("🧪 Testing Business License Navigator State Structure")
    print("=" * 60)
    
    tests = [
        ("Configuration Files", test_configuration_files),
        ("State Directories", test_state_directories),
        ("Configuration Manager", test_config_manager),
        ("Server Factory", test_server_factory),
        ("State Servers", test_state_servers),
        ("Template Structure", test_template_structure)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The state structure is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 
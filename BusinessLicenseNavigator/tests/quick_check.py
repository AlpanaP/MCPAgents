#!/usr/bin/env python3
"""
Quick Check for Business License Navigator.

Run this script for a rapid check of key components.
"""

import sys
import os
import json

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_imports():
    """Quick check of key imports."""
    print("🔍 Checking imports...")
    
    try:
        # Core imports
        from core.models import BaseRAGServer, BaseMCPServer
        print("✅ Core models imported")
        
        from core.factories.server_factory import ServerFactory
        print("✅ Server factory imported")
        
        # RAG servers
        from rag.servers.delaware import DelawareRAGServer
        from rag.servers.florida import FloridaRAGServer
        from rag.servers.generic import GenericRAGServer
        print("✅ RAG servers imported")
        
        # MCP servers
        from mcp_server.servers.delaware import DelawareLicenseServer
        from mcp_server.servers.florida import FloridaLicenseServer
        from mcp_server.servers.generic import GenericLicenseServer
        print("✅ MCP servers imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Import check failed: {e}")
        return False


def check_configuration():
    """Quick check of configuration files."""
    print("\n🔍 Checking configuration files...")
    
    try:
        # Check RAG servers config
        with open('config/rag_servers.json', 'r') as f:
            rag_config = json.load(f)
        
        rag_servers = list(rag_config["servers"].keys())
        print(f"✅ RAG servers config: {len(rag_servers)} servers found")
        print(f"   Servers: {', '.join(rag_servers)}")
        
        # Check MCP servers config
        with open('config/mcp_servers.json', 'r') as f:
            mcp_config = json.load(f)
        
        mcp_servers = list(mcp_config["servers"].keys())
        print(f"✅ MCP servers config: {len(mcp_servers)} servers found")
        print(f"   Servers: {', '.join(mcp_servers)}")
        
        # Check states config
        with open('config/states.json', 'r') as f:
            states_config = json.load(f)
        
        states = list(states_config["states"].keys())
        print(f"✅ States config: {len(states)} states found")
        print(f"   States: {', '.join(states[:5])}{'...' if len(states) > 5 else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration check failed: {e}")
        return False


def check_file_structure():
    """Quick check of file structure."""
    print("\n🔍 Checking file structure...")
    
    try:
        # Core structure
        assert os.path.exists("core/models/__init__.py")
        assert os.path.exists("core/factories/server_factory.py")
        print("✅ Core structure exists")
        
        # RAG structure
        assert os.path.exists("rag/servers/delaware/delaware_rag_server.py")
        assert os.path.exists("rag/servers/florida/florida_rag_server.py")
        assert os.path.exists("rag/servers/generic/generic_rag_server.py")
        print("✅ RAG structure exists")
        
        # MCP server structure
        assert os.path.exists("mcp_server/servers/delaware/delaware_mcp_server.py")
        assert os.path.exists("mcp_server/servers/florida/florida_mcp_server.py")
        assert os.path.exists("mcp_server/servers/generic/generic_mcp_server.py")
        print("✅ MCP server structure exists")
        
        # Config files
        assert os.path.exists("config/rag_servers.json")
        assert os.path.exists("config/mcp_servers.json")
        assert os.path.exists("config/states.json")
        print("✅ Configuration files exist")
        
        return True
        
    except Exception as e:
        print(f"❌ File structure check failed: {e}")
        return False


def check_server_factory():
    """Quick check of server factory."""
    print("\n🔍 Checking server factory...")
    
    try:
        from core.factories.server_factory import ServerFactory
        
        factory = ServerFactory()
        
        rag_servers = factory.get_available_rag_servers()
        mcp_servers = factory.get_available_mcp_servers()
        
        print(f"✅ Server factory working")
        print(f"   RAG servers: {len(rag_servers)} available")
        print(f"   MCP servers: {len(mcp_servers)} available")
        
        return True
        
    except Exception as e:
        print(f"❌ Server factory check failed: {e}")
        return False


def main():
    """Main function for quick check."""
    print("🚀 Business License Navigator - Quick Check")
    print("=" * 50)
    
    checks = [
        ("Imports", check_imports),
        ("Configuration", check_configuration),
        ("File Structure", check_file_structure),
        ("Server Factory", check_server_factory)
    ]
    
    passed = 0
    failed = 0
    
    for check_name, check_func in checks:
        if check_func():
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 Quick Check Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All checks passed! The organized structure is working correctly.")
        return 0
    else:
        print(f"⚠️  {failed} check(s) failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 
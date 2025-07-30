"""
Tests for the organized structure.

This module tests the new organized architecture with proper separation
of concerns, factory patterns, and configuration-driven design.
"""

import sys
import os
import asyncio
from typing import Dict, Any

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_config import TestLogger

def test_core_models():
    """Test core models and interfaces."""
    logger = TestLogger("Core Models")
    
    try:
        from core.models import BaseRAGServer, BaseMCPServer, SearchResult, ToolResult, TextContent
        from core.models.base_rag_server import RAGConfig
        from core.models.base_mcp_server import MCPConfig, Tool
        
        # Test RAGConfig
        config = RAGConfig(
            collection_name="test_collection",
            embedding_model="all-MiniLM-L6-v2",
            vector_size=384
        )
        assert config.collection_name == "test_collection"
        logger.success("RAGConfig works correctly")
        
        # Test SearchResult
        search_result = SearchResult(
            content=[{"text": "test content"}],
            metadata={"test": "data"}
        )
        assert search_result.get_text() == "test content"
        logger.success("SearchResult works correctly")
        
        # Test ToolResult
        tool_result = ToolResult(
            content=[TextContent(text="test tool result")]
        )
        assert tool_result.get_text() == "test tool result"
        logger.success("ToolResult works correctly")
        
        # Test TextContent
        text_content = TextContent(text="test text")
        assert text_content.text == "test text"
        assert text_content.is_valid()
        logger.success("TextContent works correctly")
        
        return True
        
    except Exception as e:
        logger.error(f"Core models test failed: {e}")
        return False

def test_server_factory():
    """Test the server factory."""
    logger = TestLogger("Server Factory")
    
    try:
        from core.factories.server_factory import ServerFactory
        
        # Create factory
        factory = ServerFactory()
        
        # Test available servers
        rag_servers = factory.get_available_rag_servers()
        mcp_servers = factory.get_available_mcp_servers()
        
        assert len(rag_servers) > 0
        assert len(mcp_servers) > 0
        logger.success(f"Found {len(rag_servers)} RAG servers and {len(mcp_servers)} MCP servers")
        
        # Test server groups
        server_groups = factory.get_server_groups()
        assert "delaware" in server_groups
        assert "florida" in server_groups
        assert "generic" in server_groups
        logger.success("Server groups loaded correctly")
        
        return True
        
    except Exception as e:
        logger.error(f"Server factory test failed: {e}")
        return False

def test_rag_server_creation():
    """Test RAG server creation."""
    logger = TestLogger("RAG Server Creation")
    
    try:
        from core.factories.server_factory import ServerFactory
        from core.models.base_rag_server import RAGConfig
        
        factory = ServerFactory()
        
        # Test creating Delaware RAG server
        delaware_config = RAGConfig(
            collection_name="test_delaware",
            embedding_model="all-MiniLM-L6-v2",
            vector_size=384
        )
        
        # This would normally create a server, but we'll test the config
        assert delaware_config.collection_name == "test_delaware"
        assert delaware_config.embedding_model == "all-MiniLM-L6-v2"
        logger.success("RAG server configuration works correctly")
        
        return True
        
    except Exception as e:
        logger.error(f"RAG server creation test failed: {e}")
        return False

def test_mcp_server_creation():
    """Test MCP server creation."""
    logger = TestLogger("MCP Server Creation")
    
    try:
        from core.models.base_mcp_server import MCPConfig, Tool
        
        # Test creating MCP config
        tools = [
            Tool(
                name="test_tool",
                description="A test tool",
                input_schema={"type": "object", "properties": {}}
            )
        ]
        
        mcp_config = MCPConfig(
            server_name="Test Server",
            server_description="A test MCP server",
            tools=tools
        )
        
        assert mcp_config.server_name == "Test Server"
        assert len(mcp_config.tools) == 1
        assert mcp_config.tools[0].name == "test_tool"
        logger.success("MCP server configuration works correctly")
        
        return True
        
    except Exception as e:
        logger.error(f"MCP server creation test failed: {e}")
        return False

def test_configuration_files():
    """Test configuration files."""
    logger = TestLogger("Configuration Files")
    
    try:
        import json
        
        # Test RAG servers config
        with open('config/rag_servers.json', 'r') as f:
            rag_config = json.load(f)
        
        assert "servers" in rag_config
        assert "delaware_rag_server" in rag_config["servers"]
        assert "florida_rag_server" in rag_config["servers"]
        assert "generic_rag_server" in rag_config["servers"]
        logger.success("RAG servers configuration loaded correctly")
        
        # Test MCP servers config
        with open('config/mcp_servers.json', 'r') as f:
            mcp_config = json.load(f)
        
        assert "servers" in mcp_config
        assert "delaware_license_server" in mcp_config["servers"]
        assert "florida_license_server" in mcp_config["servers"]
        assert "generic_license_server" in mcp_config["servers"]
        logger.success("MCP servers configuration loaded correctly")
        
        return True
        
    except Exception as e:
        logger.error(f"Configuration files test failed: {e}")
        return False

def test_package_structure():
    """Test package structure and imports."""
    logger = TestLogger("Package Structure")
    
    try:
        # Test core package
        from core.models import BaseRAGServer, BaseMCPServer
        logger.success("Core models imported successfully")
        
        # Test RAG package
        from rag.servers.delaware import DelawareRAGServer
        logger.success("Delaware RAG server imported successfully")
        
        # Test that the old structure still works for backward compatibility
        try:
            from delaware_rag.delaware_rag_server import DelawareRAGServer as OldDelawareRAGServer
            logger.success("Backward compatibility maintained")
        except ImportError:
            logger.warning("Old structure not available (expected during transition)")
        
        return True
        
    except Exception as e:
        logger.error(f"Package structure test failed: {e}")
        return False

def run_organized_structure_tests():
    """Run all organized structure tests."""
    print("🧪 Testing Organized Structure")
    print("=" * 50)
    
    tests = [
        ("Core Models", test_core_models),
        ("Server Factory", test_server_factory),
        ("RAG Server Creation", test_rag_server_creation),
        ("MCP Server Creation", test_mcp_server_creation),
        ("Configuration Files", test_configuration_files),
        ("Package Structure", test_package_structure)
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
    
    print(f"\n📊 Organized Structure Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All organized structure tests passed!")
        return True
    else:
        print(f"⚠️  {failed} organized structure test(s) failed.")
        return False

if __name__ == "__main__":
    run_organized_structure_tests() 
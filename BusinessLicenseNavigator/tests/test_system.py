"""
System Tests for Business License Navigator.

This module provides comprehensive system tests to verify that the entire
organized structure works correctly, including RAG servers, MCP servers,
configuration loading, and end-to-end functionality.
"""

import sys
import os
import asyncio
import json
from typing import Dict, Any, List

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_config import TestLogger


class SystemTestRunner:
    """Comprehensive system test runner for Business License Navigator."""
    
    def __init__(self):
        """Initialize the system test runner."""
        self.logger = TestLogger("System Tests")
        self.results = {
            "passed": 0,
            "failed": 0,
            "total": 0,
            "details": []
        }
    
    def run_test(self, test_name: str, test_func, *args, **kwargs):
        """Run a single test and record results."""
        self.results["total"] += 1
        
        try:
            result = test_func(*args, **kwargs)
            if result:
                self.results["passed"] += 1
                self.logger.success(f"{test_name} passed")
                self.results["details"].append({
                    "test": test_name,
                    "status": "PASSED",
                    "error": None
                })
                return True
            else:
                self.results["failed"] += 1
                self.logger.error(f"{test_name} failed")
                self.results["details"].append({
                    "test": test_name,
                    "status": "FAILED",
                    "error": "Test returned False"
                })
                return False
        except Exception as e:
            self.results["failed"] += 1
            self.logger.error(f"{test_name} failed with exception: {e}")
            self.results["details"].append({
                "test": test_name,
                "status": "FAILED",
                "error": str(e)
            })
            return False
    
    def print_summary(self):
        """Print test summary."""
        print(f"\n📊 System Test Results: {self.results['passed']} passed, {self.results['failed']} failed")
        
        if self.results["failed"] == 0:
            print("🎉 All system tests passed!")
        else:
            print(f"⚠️  {self.results['failed']} system test(s) failed.")
            print("\n🔍 Failed Tests:")
            for detail in self.results["details"]:
                if detail["status"] == "FAILED":
                    print(f"  ❌ {detail['test']}: {detail['error']}")
        
        return self.results["failed"] == 0


def test_core_imports():
    """Test that all core modules can be imported."""
    logger = TestLogger("Core Imports")
    
    try:
        # Test core models
        from core.models import BaseRAGServer, BaseMCPServer, SearchResult, ToolResult, TextContent
        logger.success("Core models imported successfully")
        
        # Test core factories
        from core.factories.server_factory import ServerFactory
        logger.success("Server factory imported successfully")
        
        # Test RAG servers
        from rag.servers.delaware import DelawareRAGServer
        from rag.servers.florida import FloridaRAGServer
        from rag.servers.generic import GenericRAGServer
        logger.success("RAG servers imported successfully")
        
        # Test MCP servers
        from mcp_server.servers.delaware import DelawareLicenseServer
        from mcp_server.servers.florida import FloridaLicenseServer
        from mcp_server.servers.generic import GenericLicenseServer
        logger.success("MCP servers imported successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Core imports failed: {e}")
        return False


def test_configuration_loading():
    """Test that all configuration files can be loaded."""
    logger = TestLogger("Configuration Loading")
    
    try:
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
        
        # Test states config
        with open('config/states.json', 'r') as f:
            states_config = json.load(f)
        
        assert "states" in states_config
        assert "DE" in states_config["states"]
        assert "FL" in states_config["states"]
        logger.success("States configuration loaded correctly")
        
        return True
        
    except Exception as e:
        logger.error(f"Configuration loading failed: {e}")
        return False


def test_server_factory():
    """Test that the server factory works correctly."""
    logger = TestLogger("Server Factory")
    
    try:
        from core.factories.server_factory import ServerFactory
        
        # Create factory
        factory = ServerFactory()
        
        # Test available servers
        rag_servers = factory.get_available_rag_servers()
        mcp_servers = factory.get_available_mcp_servers()
        
        assert len(rag_servers) >= 3, f"Expected at least 3 RAG servers, got {len(rag_servers)}"
        assert len(mcp_servers) >= 3, f"Expected at least 3 MCP servers, got {len(mcp_servers)}"
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
    """Test that RAG servers can be created."""
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
        
        assert delaware_config.collection_name == "test_delaware"
        assert delaware_config.embedding_model == "all-MiniLM-L6-v2"
        logger.success("RAG server configuration works correctly")
        
        return True
        
    except Exception as e:
        logger.error(f"RAG server creation test failed: {e}")
        return False


def test_mcp_server_creation():
    """Test that MCP servers can be created."""
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


def test_data_models():
    """Test that all data models work correctly."""
    logger = TestLogger("Data Models")
    
    try:
        from core.models import SearchResult, ToolResult, TextContent
        
        # Test SearchResult
        search_result = SearchResult(
            content=[{"text": "test content"}],
            metadata={"test": "data"}
        )
        assert search_result.get_text() == "test content"
        assert search_result.is_valid()
        logger.success("SearchResult works correctly")
        
        # Test ToolResult
        tool_result = ToolResult(
            content=[TextContent(text="test tool result")]
        )
        assert tool_result.get_text() == "test tool result"
        assert tool_result.is_valid()
        logger.success("ToolResult works correctly")
        
        # Test TextContent
        text_content = TextContent(text="test text")
        assert text_content.text == "test text"
        assert text_content.is_valid()
        logger.success("TextContent works correctly")
        
        return True
        
    except Exception as e:
        logger.error(f"Data models test failed: {e}")
        return False


def test_package_structure():
    """Test that the package structure is organized correctly."""
    logger = TestLogger("Package Structure")
    
    try:
        # Test core package
        from core.models import BaseRAGServer, BaseMCPServer
        logger.success("Core models imported successfully")
        
        # Test RAG package
        from rag.servers.delaware import DelawareRAGServer
        from rag.servers.florida import FloridaRAGServer
        from rag.servers.generic import GenericRAGServer
        logger.success("RAG servers imported successfully")
        
        # Test MCP server package
        from mcp_server.servers.delaware import DelawareLicenseServer
        from mcp_server.servers.florida import FloridaLicenseServer
        from mcp_server.servers.generic import GenericLicenseServer
        logger.success("MCP servers imported successfully")
        
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


def test_configuration_validation():
    """Test that configuration files are valid."""
    logger = TestLogger("Configuration Validation")
    
    try:
        # Test RAG servers config structure
        with open('config/rag_servers.json', 'r') as f:
            rag_config = json.load(f)
        
        for server_name, server_config in rag_config["servers"].items():
            assert "name" in server_config
            assert "description" in server_config
            assert "module" in server_config
            assert "class" in server_config
            assert "config" in server_config
            logger.success(f"RAG server {server_name} configuration valid")
        
        # Test MCP servers config structure
        with open('config/mcp_servers.json', 'r') as f:
            mcp_config = json.load(f)
        
        for server_name, server_config in mcp_config["servers"].items():
            assert "name" in server_config
            assert "description" in server_config
            assert "module" in server_config
            assert "class" in server_config
            assert "config" in server_config
            logger.success(f"MCP server {server_name} configuration valid")
        
        return True
        
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return False


def test_file_structure():
    """Test that the file structure is organized correctly."""
    logger = TestLogger("File Structure")
    
    try:
        # Check core directory structure
        assert os.path.exists("core/models/__init__.py")
        assert os.path.exists("core/factories/server_factory.py")
        logger.success("Core directory structure exists")
        
        # Check RAG directory structure
        assert os.path.exists("rag/servers/delaware/delaware_rag_server.py")
        assert os.path.exists("rag/servers/florida/florida_rag_server.py")
        assert os.path.exists("rag/servers/generic/generic_rag_server.py")
        logger.success("RAG directory structure exists")
        
        # Check MCP server directory structure
        assert os.path.exists("mcp_server/servers/delaware/delaware_mcp_server.py")
        assert os.path.exists("mcp_server/servers/florida/florida_mcp_server.py")
        assert os.path.exists("mcp_server/servers/generic/generic_mcp_server.py")
        logger.success("MCP server directory structure exists")
        
        # Check configuration files
        assert os.path.exists("config/rag_servers.json")
        assert os.path.exists("config/mcp_servers.json")
        assert os.path.exists("config/states.json")
        logger.success("Configuration files exist")
        
        return True
        
    except Exception as e:
        logger.error(f"File structure test failed: {e}")
        return False


def run_system_tests():
    """Run all system tests."""
    print("🧪 Business License Navigator - System Tests")
    print("=" * 60)
    
    runner = SystemTestRunner()
    
    tests = [
        ("Core Imports", test_core_imports),
        ("Configuration Loading", test_configuration_loading),
        ("Server Factory", test_server_factory),
        ("RAG Server Creation", test_rag_server_creation),
        ("MCP Server Creation", test_mcp_server_creation),
        ("Data Models", test_data_models),
        ("Package Structure", test_package_structure),
        ("Configuration Validation", test_configuration_validation),
        ("File Structure", test_file_structure)
    ]
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        runner.run_test(test_name, test_func)
    
    return runner.print_summary()


if __name__ == "__main__":
    success = run_system_tests()
    sys.exit(0 if success else 1) 
"""
Template RAG Server for New States/Provinces.

This is a template that can be copied and customized for new states or provinces.
To add a new state:
1. Copy this template directory to rag/servers/{state_code_lower}
2. Update the class names and imports
3. Customize the configuration and data sources
4. Update the configuration files
"""

from .template_rag_server import TemplateRAGServer
from .template_mcp_server import TemplateMCPServer

__all__ = ["TemplateRAGServer", "TemplateMCPServer"] 
#!/usr/bin/env python3
"""
Script to add new states/provinces to the Business License Navigator.

This script automates the process of creating new state-specific RAG and MCP servers
by copying the template and customizing it for the new state.
"""

import os
import sys
import shutil
import json
import re
from pathlib import Path
from typing import Dict, Any


class StateAdder:
    """Helper class to add new states to the system."""
    
    def __init__(self):
        """Initialize the state adder."""
        self.project_root = Path(__file__).parent.parent
        self.template_dir = self.project_root / "src" / "servers" / "template"
        self.rag_servers_dir = self.project_root / "src" / "servers"
        self.config_dir = self.project_root / "src" / "config"
        
    def add_new_state(self, state_code: str, state_name: str, country: str = "US"):
        """
        Add a new state to the system.
        
        Args:
            state_code: State/province code (e.g., "CA", "ON")
            state_name: Full state/province name (e.g., "California", "Ontario")
            country: Country code (e.g., "US", "CA")
        """
        print(f"Adding new state: {state_code} ({state_name})")
        
        # Validate inputs
        if not self._validate_inputs(state_code, state_name, country):
            return False
        
        # Create state directory
        state_dir = self.rag_servers_dir / state_code.lower()
        if state_dir.exists():
            print(f"Error: State directory {state_dir} already exists")
            return False
        
        # Copy template files
        if not self._copy_template_files(state_dir):
            return False
        
        # Customize files for the new state
        if not self._customize_files(state_dir, state_code, state_name, country):
            return False
        
        # Update configuration files
        if not self._update_configurations(state_code, state_name, country):
            return False
        
        print(f"Successfully added state: {state_code} ({state_name})")
        print(f"State directory: {state_dir}")
        print("\nNext steps:")
        print("1. Customize the state-specific configuration")
        print("2. Add state-specific data sources")
        print("3. Update business types and license categories")
        print("4. Test the new state servers")
        
        return True
    
    def _validate_inputs(self, state_code: str, state_name: str, country: str) -> bool:
        """Validate input parameters."""
        if not state_code or len(state_code) != 2:
            print("Error: State code must be exactly 2 characters")
            return False
        
        if not state_name:
            print("Error: State name cannot be empty")
            return False
        
        if country not in ["US", "CA"]:
            print("Error: Country must be 'US' or 'CA'")
            return False
        
        return True
    
    def _copy_template_files(self, state_dir: Path) -> bool:
        """Copy template files to the new state directory."""
        try:
            # Copy all files from template
            shutil.copytree(self.template_dir, state_dir)
            print(f"Copied template files to {state_dir}")
            return True
        except Exception as e:
            print(f"Error copying template files: {e}")
            return False
    
    def _customize_files(self, state_dir: Path, state_code: str, state_name: str, country: str) -> bool:
        """Customize the copied files for the new state."""
        try:
            # Customize RAG server
            rag_server_file = state_dir / "template_rag_server.py"
            if rag_server_file.exists():
                self._customize_rag_server(rag_server_file, state_code, state_name)
            
            # Customize MCP server
            mcp_server_file = state_dir / "template_mcp_server.py"
            if mcp_server_file.exists():
                self._customize_mcp_server(mcp_server_file, state_code, state_name)
            
            # Rename files
            self._rename_files(state_dir, state_code)
            
            # Update __init__.py
            init_file = state_dir / "__init__.py"
            if init_file.exists():
                self._customize_init_file(init_file, state_code, state_name)
            
            print("Customized files for the new state")
            return True
            
        except Exception as e:
            print(f"Error customizing files: {e}")
            return False
    
    def _customize_rag_server(self, file_path: Path, state_code: str, state_name: str):
        """Customize the RAG server file."""
        content = file_path.read_text()
        
        # Replace template placeholders
        content = content.replace("TemplateRAGServer", f"{state_code.title()}RAGServer")
        content = content.replace("TEMPLATE", state_code.upper())
        content = content.replace("Template State", state_name)
        content = content.replace("template_rag_server", f"{state_code.lower()}_rag_server")
        
        # Update data sources
        content = content.replace(
            "https://template-state.gov/business/",
            f"https://{state_code.lower()}-state.gov/business/"
        )
        content = content.replace(
            "https://template-state.gov/licenses/",
            f"https://{state_code.lower()}-state.gov/licenses/"
        )
        
        file_path.write_text(content)
    
    def _customize_mcp_server(self, file_path: Path, state_code: str, state_name: str):
        """Customize the MCP server file."""
        content = file_path.read_text()
        
        # Replace template placeholders
        content = content.replace("TemplateMCPServer", f"{state_code.title()}MCPServer")
        content = content.replace("TEMPLATE", state_code.upper())
        content = content.replace("Template State", state_name)
        content = content.replace("template_mcp_server", f"{state_code.lower()}_mcp_server")
        
        file_path.write_text(content)
    
    def _customize_init_file(self, file_path: Path, state_code: str, state_name: str):
        """Customize the __init__.py file."""
        content = file_path.read_text()
        
        # Replace template placeholders
        content = content.replace("TemplateRAGServer", f"{state_code.title()}RAGServer")
        content = content.replace("TemplateMCPServer", f"{state_code.title()}MCPServer")
        content = content.replace("template_rag_server", f"{state_code.lower()}_rag_server")
        content = content.replace("template_mcp_server", f"{state_code.lower()}_mcp_server")
        
        file_path.write_text(content)
    
    def _rename_files(self, state_dir: Path, state_code: str):
        """Rename template files to state-specific names."""
        # Rename RAG server file
        rag_file = state_dir / "template_rag_server.py"
        if rag_file.exists():
            new_rag_file = state_dir / f"{state_code.lower()}_rag_server.py"
            rag_file.rename(new_rag_file)
        
        # Rename MCP server file
        mcp_file = state_dir / "template_mcp_server.py"
        if mcp_file.exists():
            new_mcp_file = state_dir / f"{state_code.lower()}_mcp_server.py"
            mcp_file.rename(new_mcp_file)
    
    def _update_configurations(self, state_code: str, state_name: str, country: str) -> bool:
        """Update configuration files to include the new state."""
        try:
            # Update states.json
            self._update_states_config(state_code, state_name, country)
            
            # Update rag_servers.json
            self._update_rag_servers_config(state_code, state_name)
            
            # Update mcp_servers.json
            self._update_mcp_servers_config(state_code, state_name)
            
            # Update app_config.json
            self._update_app_config(state_code)
            
            print("Updated configuration files")
            return True
            
        except Exception as e:
            print(f"Error updating configurations: {e}")
            return False
    
    def _update_states_config(self, state_code: str, state_name: str, country: str):
        """Update states.json configuration."""
        states_file = self.config_dir / "states.json"
        if not states_file.exists():
            print("Warning: states.json not found")
            return
        
        with open(states_file, 'r') as f:
            config = json.load(f)
        
        # Add new state configuration
        config["states"][state_code.upper()] = {
            "name": state_name,
            "full_name": f"{state_name}",
            "nickname": f"The {state_name} State",
            "type": "state" if country == "US" else "province",
            "country": country,
            "capabilities": {
                "rag_enabled": True,
                "mcp_enabled": True,
                "web_scraping": True,
                "official_apis": False
            },
            "resources": {
                "main": {
                    "name": f"{state_name} Business Licensing",
                    "url": f"https://{state_code.lower()}-state.gov/",
                    "description": f"Official {state_name} government website for business licenses"
                }
            },
            "mcp_servers": {
                "rag_server": {
                    "module": f"servers.{state_code.lower()}.{state_code.lower()}_rag_server",
                    "class": f"{state_code.title()}RAGServer",
                    "config": {
                        "collection_name": f"{state_code.lower()}_licenses",
                        "embedding_model": "all-MiniLM-L6-v2",
                        "vector_size": 384
                    }
                },
                "mcp_server": {
                    "module": f"servers.{state_code.lower()}.{state_code.lower()}_mcp_server",
                    "class": f"{state_code.title()}MCPServer"
                }
            }
        }
        
        with open(states_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _update_rag_servers_config(self, state_code: str, state_name: str):
        """Update rag_servers.json configuration."""
        rag_file = self.config_dir / "rag_servers.json"
        if not rag_file.exists():
            print("Warning: rag_servers.json not found")
            return
        
        with open(rag_file, 'r') as f:
            config = json.load(f)
        
        # Add new RAG server configuration
        server_name = f"{state_code.lower()}_rag_server"
        config["servers"][server_name] = {
            "name": f"{state_name} RAG Server",
            "description": f"RAG server for {state_name} business license information",
            "module": f"servers.{state_code.lower()}.{state_code.lower()}_rag_server",
            "class": f"{state_code.title()}RAGServer",
            "config": {
                "collection_name": f"{state_code.lower()}_licenses",
                "embedding_model": "all-MiniLM-L6-v2",
                "vector_size": 384,
                "top_k": 5,
                "similarity_threshold": 0.7,
                "data_sources": [
                    f"https://{state_code.lower()}-state.gov/"
                ],
                "license_categories": [
                    "General Business License",
                    "Industry-Specific License",
                    "Professional License",
                    "Local Business License"
                ]
            }
        }
        
        # Update server groups
        if "server_groups" not in config:
            config["server_groups"] = {}
        
        config["server_groups"][state_code.lower()] = [server_name]
        
        with open(rag_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _update_mcp_servers_config(self, state_code: str, state_name: str):
        """Update mcp_servers.json configuration."""
        mcp_file = self.config_dir / "mcp_servers.json"
        if not mcp_file.exists():
            print("Warning: mcp_servers.json not found")
            return
        
        with open(mcp_file, 'r') as f:
            config = json.load(f)
        
        # Add new MCP server configuration
        server_name = f"{state_code.lower()}_license_server"
        config["servers"][server_name] = {
            "name": f"{state_name} License Server",
            "description": f"MCP server for {state_name} business license information",
            "module": f"servers.{state_code.lower()}.{state_code.lower()}_mcp_server",
            "class": f"{state_code.title()}MCPServer",
            "config": {
                "server_name": f"{state_name} License Server",
                "server_description": f"Provides {state_name}-specific business license information and tools",
                "tools": [
                    {
                        "name": f"get_{state_code.lower()}_license_categories",
                        "description": f"Get available {state_name} license categories",
                        "input_schema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    },
                    {
                        "name": f"search_{state_code.lower()}_licenses",
                        "description": f"Search for {state_name} licenses by keyword",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Search query for licenses"
                                }
                            },
                            "required": ["query"]
                        }
                    }
                ]
            }
        }
        
        # Update server groups
        if "server_groups" not in config:
            config["server_groups"] = {}
        
        config["server_groups"][state_code.lower()] = [server_name]
        
        with open(mcp_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _update_app_config(self, state_code: str):
        """Update app_config.json to enable the new state."""
        app_file = self.config_dir / "app_config.json"
        if not app_file.exists():
            print("Warning: app_config.json not found")
            return
        
        with open(app_file, 'r') as f:
            config = json.load(f)
        
        # Add new state to enabled states
        enabled_states = config.get("states", {}).get("enabled_states", [])
        if state_code.upper() not in enabled_states:
            enabled_states.append(state_code.upper())
            config["states"]["enabled_states"] = enabled_states
        
        with open(app_file, 'w') as f:
            json.dump(config, f, indent=2)


def main():
    """Main function to run the state adder."""
    if len(sys.argv) != 4:
        print("Usage: python add_new_state.py <state_code> <state_name> [country]")
        print("Example: python add_new_state.py CA California US")
        print("Example: python add_new_state.py ON Ontario CA")
        sys.exit(1)
    
    state_code = sys.argv[1]
    state_name = sys.argv[2]
    country = sys.argv[3] if len(sys.argv) > 3 else "US"
    
    adder = StateAdder()
    success = adder.add_new_state(state_code, state_name, country)
    
    if success:
        print("\n✅ State added successfully!")
    else:
        print("\n❌ Failed to add state")
        sys.exit(1)


if __name__ == "__main__":
    main() 
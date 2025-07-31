"""
Configuration Manager for Business License Navigator.

This module provides centralized configuration management with:
- Feature flags for easy enable/disable of functionality
- State management for enabling/disabling specific states
- Security settings
- Monitoring and deployment configurations
"""

import json
import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path


class ConfigManager:
    """
    Centralized configuration manager for the Business License Navigator.
    
    Provides:
    - Feature flag management
    - State enable/disable functionality
    - Security configuration
    - Monitoring settings
    - Deployment configurations
    """
    
    def __init__(self, config_dir: str = "src/config"):
        """Initialize the configuration manager."""
        self.config_dir = Path(config_dir)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Load all configurations
        self.app_config = self._load_config("app_config.json")
        self.states_config = self._load_config("states.json")
        self.rag_servers_config = self._load_config("rag_servers.json")
        self.mcp_servers_config = self._load_config("mcp_servers.json")
        self.business_types_config = self._load_config("business_types.json")
        
        # Validate configurations
        self._validate_configurations()
    
    def _load_config(self, filename: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        config_path = self.config_dir / filename
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                self.logger.info(f"Loaded configuration: {filename}")
                return config
        except Exception as e:
            self.logger.error(f"Error loading config {filename}: {e}")
            return {}
    
    def _validate_configurations(self):
        """Validate all loaded configurations."""
        required_configs = [
            ("app_config", self.app_config),
            ("states_config", self.states_config),
            ("rag_servers_config", self.rag_servers_config),
            ("mcp_servers_config", self.mcp_servers_config)
        ]
        
        for name, config in required_configs:
            if not config:
                self.logger.warning(f"Configuration {name} is empty or invalid")
    
    def get_feature_flag(self, feature: str) -> bool:
        """Get a feature flag value."""
        return self.app_config.get("features", {}).get(feature, False)
    
    def is_state_enabled(self, state_code: str) -> bool:
        """Check if a state is enabled."""
        enabled_states = self.app_config.get("states", {}).get("enabled_states", [])
        return state_code.upper() in enabled_states
    
    def get_enabled_states(self) -> List[str]:
        """Get list of enabled states."""
        return self.app_config.get("states", {}).get("enabled_states", [])
    
    def get_default_state(self) -> str:
        """Get the default state."""
        return self.app_config.get("states", {}).get("default_state", "DE")
    
    def get_state_config(self, state_code: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific state."""
        states = self.states_config.get("states", {})
        return states.get(state_code.upper())
    
    def get_ai_service_config(self) -> Dict[str, Any]:
        """Get AI service configuration."""
        return self.app_config.get("ai_services", {})
    
    def get_rag_config(self) -> Dict[str, Any]:
        """Get RAG configuration."""
        return self.app_config.get("rag", {})
    
    def get_qdrant_config(self) -> Dict[str, Any]:
        """Get Qdrant configuration."""
        return self.app_config.get("qdrant", {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration."""
        return self.app_config.get("security", {})
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration."""
        return self.app_config.get("monitoring", {})
    
    def get_caching_config(self) -> Dict[str, Any]:
        """Get caching configuration."""
        return self.app_config.get("caching", {})
    
    def get_deployment_config(self) -> Dict[str, Any]:
        """Get deployment configuration."""
        return self.app_config.get("deployment", {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.app_config.get("logging", {})
    
    def enable_state(self, state_code: str) -> bool:
        """Enable a state."""
        enabled_states = self.app_config.get("states", {}).get("enabled_states", [])
        if state_code.upper() not in enabled_states:
            enabled_states.append(state_code.upper())
            self.app_config["states"]["enabled_states"] = enabled_states
            self._save_app_config()
            self.logger.info(f"Enabled state: {state_code}")
            return True
        return False
    
    def disable_state(self, state_code: str) -> bool:
        """Disable a state."""
        enabled_states = self.app_config.get("states", {}).get("enabled_states", [])
        if state_code.upper() in enabled_states:
            enabled_states.remove(state_code.upper())
            self.app_config["states"]["enabled_states"] = enabled_states
            self._save_app_config()
            self.logger.info(f"Disabled state: {state_code}")
            return True
        return False
    
    def enable_feature(self, feature: str) -> bool:
        """Enable a feature flag."""
        features = self.app_config.get("features", {})
        if not features.get(feature, False):
            features[feature] = True
            self.app_config["features"] = features
            self._save_app_config()
            self.logger.info(f"Enabled feature: {feature}")
            return True
        return False
    
    def disable_feature(self, feature: str) -> bool:
        """Disable a feature flag."""
        features = self.app_config.get("features", {})
        if features.get(feature, False):
            features[feature] = False
            self.app_config["features"] = features
            self._save_app_config()
            self.logger.info(f"Disabled feature: {feature}")
            return True
        return False
    
    def _save_app_config(self):
        """Save the app configuration to file."""
        try:
            config_path = self.config_dir / "app_config.json"
            with open(config_path, 'w') as f:
                json.dump(self.app_config, f, indent=2)
            self.logger.info("Saved app configuration")
        except Exception as e:
            self.logger.error(f"Error saving app configuration: {e}")
    
    def get_server_config(self, server_type: str, server_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific server."""
        if server_type == "rag":
            config = self.rag_servers_config
        elif server_type == "mcp":
            config = self.mcp_servers_config
        else:
            return None
        
        servers = config.get("servers", {})
        return servers.get(server_name)
    
    def get_all_server_configs(self, server_type: str) -> Dict[str, Any]:
        """Get all server configurations for a type."""
        if server_type == "rag":
            return self.rag_servers_config.get("servers", {})
        elif server_type == "mcp":
            return self.mcp_servers_config.get("servers", {})
        else:
            return {}
    
    def is_server_enabled(self, server_type: str, server_name: str) -> bool:
        """Check if a server is enabled."""
        server_config = self.get_server_config(server_type, server_name)
        if not server_config:
            return False
        
        # Check if the server's state is enabled
        state_code = self._extract_state_from_server_name(server_name)
        if state_code:
            return self.is_state_enabled(state_code)
        
        return True
    
    def _extract_state_from_server_name(self, server_name: str) -> Optional[str]:
        """Extract state code from server name."""
        if "delaware" in server_name.lower():
            return "DE"
        elif "florida" in server_name.lower():
            return "FL"
        elif "texas" in server_name.lower():
            return "TX"
        elif "california" in server_name.lower():
            return "CA"
        elif "ontario" in server_name.lower():
            return "ON"
        return None
    
    def get_environment(self) -> str:
        """Get current environment."""
        return self.app_config.get("app", {}).get("environment", "development")
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return self.app_config.get("app", {}).get("debug", False)
    
    def get_log_level(self) -> str:
        """Get log level."""
        return self.app_config.get("app", {}).get("log_level", "INFO")
    
    def get_version(self) -> str:
        """Get application version."""
        return self.app_config.get("app", {}).get("version", "1.0.0")


# Global configuration manager instance
config_manager = ConfigManager() 
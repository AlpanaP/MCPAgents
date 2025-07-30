import json
import os
import re
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse

class StateHandler:
    """Generic handler for different states/provinces based on configuration."""
    
    def __init__(self, config_path: str = "config/states.json"):
        """Initialize with state configuration."""
        self.config_path = config_path
        self.states_config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load state configuration from JSON file."""
        try:
            config_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_file = os.path.join(config_dir, self.config_path)
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading state config: {e}")
            return {"states": {}, "default_capabilities": {}}
    
    def detect_state_from_query(self, business_description: str) -> Optional[str]:
        """Detect state/province from business description."""
        business_lower = business_description.lower()
        
        # Look for state abbreviations and names
        for state_code, config in self.states_config.get("states", {}).items():
            state_name = config.get("name", "").lower()
            full_name = config.get("full_name", "").lower()
            nickname = config.get("nickname", "").lower()
            
            # Check for state code (e.g., "DE", "TX")
            if state_code.lower() in business_lower:
                return state_code
            
            # Check for state name (e.g., "delaware", "texas")
            if state_name in business_lower:
                return state_code
            
            # Check for full name (e.g., "state of delaware")
            if full_name in business_lower:
                return state_code
            
            # Check for nickname (e.g., "first state")
            if nickname in business_lower:
                return state_code
        
        return None
    
    def get_state_config(self, state_code: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific state/province."""
        return self.states_config.get("states", {}).get(state_code.upper())
    
    def get_state_capabilities(self, state_code: str) -> Dict[str, bool]:
        """Get capabilities for a specific state."""
        state_config = self.get_state_config(state_code)
        if not state_config:
            return self.states_config.get("default_capabilities", {})
        
        return state_config.get("capabilities", self.states_config.get("default_capabilities", {}))
    
    def is_rag_enabled(self, state_code: str) -> bool:
        """Check if RAG is enabled for a state."""
        capabilities = self.get_state_capabilities(state_code)
        return capabilities.get("rag_enabled", False)
    
    def is_mcp_enabled(self, state_code: str) -> bool:
        """Check if MCP is enabled for a state."""
        capabilities = self.get_state_capabilities(state_code)
        return capabilities.get("mcp_enabled", False)
    
    def is_web_scraping_enabled(self, state_code: str) -> bool:
        """Check if web scraping is enabled for a state."""
        capabilities = self.get_state_capabilities(state_code)
        return capabilities.get("web_scraping", True)
    
    def get_state_resources(self, state_code: str) -> Dict[str, Any]:
        """Get resources for a specific state."""
        state_config = self.get_state_config(state_code)
        if not state_config:
            return {}
        
        return state_config.get("resources", {})
    
    def get_local_governments(self, state_code: str) -> Dict[str, List[Dict[str, str]]]:
        """Get local government resources for a state."""
        state_config = self.get_state_config(state_code)
        if not state_config:
            return {}
        
        return state_config.get("local_governments", {})
    
    def get_business_support(self, state_code: str) -> List[Dict[str, str]]:
        """Get business support resources for a state."""
        state_config = self.get_state_config(state_code)
        if not state_config:
            return []
        
        return state_config.get("business_support", [])
    
    def get_mcp_servers(self, state_code: str) -> Dict[str, Any]:
        """Get MCP server configuration for a state."""
        state_config = self.get_state_config(state_code)
        if not state_config:
            return {}
        
        return state_config.get("mcp_servers", {})
    
    def get_scraping_config(self, state_code: str) -> Dict[str, Any]:
        """Get web scraping configuration for a state."""
        state_config = self.get_state_config(state_code)
        if not state_config:
            return {}
        
        return state_config.get("scraping_config", {})
    
    def get_business_type_resources(self, state_code: str, business_type: str) -> Dict[str, Any]:
        """Get business type specific resources for a state."""
        state_config = self.get_state_config(state_code)
        if not state_config:
            return {}
        
        business_types = state_config.get("business_types", {})
        return business_types.get(business_type, {})
    
    def generate_state_guidance(self, state_code: str, business_description: str, business_type: str = None) -> str:
        """Generate comprehensive guidance for a state/province."""
        state_config = self.get_state_config(state_code)
        if not state_config:
            return self._generate_general_guidance(business_description)
        
        state_name = state_config.get("name", "Unknown State")
        state_type = state_config.get("type", "state")
        country = state_config.get("country", "US")
        
        guidance = f"## 🏛️ {state_name} {state_type.title()} Business Requirements\n\n"
        guidance += f"**Location**: {state_name} ({state_code}), {country}\n\n"
        
        # Add state-specific resources
        resources = self.get_state_resources(state_code)
        if resources:
            guidance += "### 🔗 Essential {state_name} Resources:\n\n"
            for category, resource in resources.items():
                if isinstance(resource, dict):
                    name = resource.get("name", "")
                    url = resource.get("url", "")
                    description = resource.get("description", "")
                    guidance += f"**{name}**: {url}\n"
                    if description:
                        guidance += f"*{description}*\n"
                    guidance += "\n"
        
        # Add business type specific resources
        if business_type:
            business_resources = self.get_business_type_resources(state_code, business_type)
            if business_resources:
                guidance += f"### 🎯 {business_type.title()} Specific Resources:\n\n"
                resources_list = business_resources.get("resources", [])
                for resource in resources_list:
                    name = resource.get("name", "")
                    url = resource.get("url", "")
                    guidance += f"- 🔗 [{name}]({url})\n"
                
                contact = business_resources.get("contact", {})
                if contact:
                    phone = contact.get("phone", "")
                    contact_name = contact.get("name", "")
                    guidance += f"- 📞 **{contact_name}**: {phone}\n"
                guidance += "\n"
        
        # Add local government resources
        local_govs = self.get_local_governments(state_code)
        if local_govs:
            guidance += "### 🏘️ Local Government Resources:\n\n"
            for gov_type, gov_list in local_govs.items():
                if gov_list:
                    guidance += f"**{gov_type.title()}:**\n"
                    for gov in gov_list:
                        name = gov.get("name", "")
                        url = gov.get("url", "")
                        guidance += f"- 🔗 [{name}]({url})\n"
                    guidance += "\n"
        
        # Add business support resources
        business_support = self.get_business_support(state_code)
        if business_support:
            guidance += "### 🚀 Business Support Resources:\n\n"
            for support in business_support:
                name = support.get("name", "")
                url = support.get("url", "")
                guidance += f"- 🔗 [{name}]({url})\n"
            guidance += "\n"
        
        # Add capabilities information
        capabilities = self.get_state_capabilities(state_code)
        if capabilities:
            guidance += "### ⚙️ Available Services:\n\n"
            if capabilities.get("rag_enabled"):
                guidance += "- ✅ **RAG Search**: Semantic search with vector database\n"
            if capabilities.get("mcp_enabled"):
                guidance += "- ✅ **MCP Tools**: Model Context Protocol tools available\n"
            if capabilities.get("web_scraping"):
                guidance += "- ✅ **Web Scraping**: Real-time data from government websites\n"
            if capabilities.get("official_apis"):
                guidance += "- ✅ **Official APIs**: Direct API access to government data\n"
            guidance += "\n"
        
        return guidance
    
    def _generate_general_guidance(self, business_description: str) -> str:
        """Generate general guidance when no specific state is detected."""
        guidance = "## 🏢 General Business Requirements\n\n"
        guidance += "### 📋 General Setup Process:\n\n"
        
        guidance += "**Step 1: Business Registration**\n"
        guidance += "- ✅ Register your business with the appropriate state agency\n"
        guidance += "- ✅ Obtain a business license\n"
        guidance += "- ✅ Register for sales tax if applicable\n"
        guidance += "- ✅ Apply for an Employer Identification Number (EIN)\n\n"
        
        guidance += "**Step 2: Location & Zoning**\n"
        guidance += "- ✅ Check local zoning requirements\n"
        guidance += "- ✅ Ensure adequate space for your business\n"
        guidance += "- ✅ Verify parking and accessibility requirements\n\n"
        
        guidance += "**Step 3: Insurance & Compliance**\n"
        guidance += "- ✅ Obtain general liability insurance\n"
        guidance += "- ✅ Set up proper accounting systems\n"
        guidance += "- ✅ Plan for compliance requirements\n\n"
        
        guidance += "### 🔗 General Resources:\n\n"
        guidance += "- **Small Business Administration**: https://www.sba.gov/\n"
        guidance += "- **IRS Business**: https://www.irs.gov/businesses\n"
        guidance += "- **BusinessUSA**: https://business.usa.gov/\n\n"
        
        return guidance
    
    def get_state_sources(self, state_code: str, business_type: str = None) -> List[str]:
        """Get source attribution for a state."""
        state_config = self.get_state_config(state_code)
        if not state_config:
            return []
        
        sources = []
        state_name = state_config.get("name", "Unknown State")
        
        # Add general state resources
        resources = self.get_state_resources(state_code)
        for category, resource in resources.items():
            if isinstance(resource, dict):
                name = resource.get("name", "")
                url = resource.get("url", "")
                sources.append(f"**{name}**: [{name}]({url})")
        
        # Add business type specific sources
        if business_type:
            business_resources = self.get_business_type_resources(state_code, business_type)
            resources_list = business_resources.get("resources", [])
            for resource in resources_list:
                name = resource.get("name", "")
                url = resource.get("url", "")
                sources.append(f"**{state_name} {business_type.title()}**: [{name}]({url})")
        
        return sources
    
    def validate_url(self, url: str, state_code: str) -> bool:
        """Validate URL for a specific state's allowed domains."""
        if not url or not isinstance(url, str):
            return False
        
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ['https']:
                return False
            
            scraping_config = self.get_scraping_config(state_code)
            allowed_domains = scraping_config.get("allowed_domains", [])
            
            if not allowed_domains:
                return True  # If no restrictions, allow all HTTPS URLs
            
            return parsed.netloc in allowed_domains
        except Exception:
            return False
    
    def get_supported_states(self) -> List[str]:
        """Get list of supported state/province codes."""
        return list(self.states_config.get("states", {}).keys())
    
    def get_supported_countries(self) -> Dict[str, Any]:
        """Get supported countries and their states/provinces."""
        return self.states_config.get("supported_countries", {}) 
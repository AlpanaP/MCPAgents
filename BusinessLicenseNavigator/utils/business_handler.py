import json
import os
from typing import Dict, List, Optional, Any

class BusinessTypeHandler:
    """Generic handler for different business types based on configuration."""
    
    def __init__(self, config_path: str = "config/business_types.json"):
        """Initialize with business type configuration."""
        self.config_path = config_path
        self.business_types = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load business type configuration from JSON file."""
        try:
            config_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_file = os.path.join(config_dir, self.config_path)
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading business type config: {e}")
            return {"business_types": {}, "general_resources": {}}
    
    def detect_business_type(self, business_description: str) -> Optional[str]:
        """Detect business type from description using keywords."""
        business_lower = business_description.lower()
        
        for business_type, config in self.business_types.get("business_types", {}).items():
            keywords = config.get("keywords", [])
            if any(keyword in business_lower for keyword in keywords):
                return business_type
        
        return None
    
    def get_business_config(self, business_type: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific business type."""
        return self.business_types.get("business_types", {}).get(business_type)
    
    def generate_business_guidance(self, business_type: str, business_description: str) -> str:
        """Generate comprehensive guidance for a business type."""
        config = self.get_business_config(business_type)
        if not config:
            return self._generate_general_guidance(business_description)
        
        guidance = f"## {config.get('icon', '🏢')} {config.get('title', 'Delaware Business Requirements')}\n\n"
        
        # Add step-by-step process
        guidance += "### 📋 Step-by-Step Setup Process:\n\n"
        steps = config.get("steps", [])
        for step in steps:
            guidance += f"**{step['title']}**\n"
            for item in step.get("items", []):
                guidance += f"- ✅ {item}\n"
            guidance += "\n"
        
        # Add resources
        guidance += "### 🔗 Essential Delaware Resources:\n\n"
        resources = config.get("resources", {})
        
        for category, resource_list in resources.items():
            if resource_list:
                category_title = category.replace("_", " ").title()
                guidance += f"**{category_title}:**\n"
                for resource in resource_list:
                    name = resource.get("name", "")
                    url = resource.get("url", "")
                    phone = resource.get("phone", "")
                    if phone:
                        guidance += f"- 📞 **{name}**: {phone}\n"
                    else:
                        guidance += f"- 🔗 [{name}]({url})\n"
                guidance += "\n"
        
        # Add compliance notes
        compliance_notes = config.get("compliance_notes", [])
        if compliance_notes:
            guidance += "### ⚠️ Important Compliance Notes:\n\n"
            for note in compliance_notes:
                guidance += f"- **{note}**\n"
            guidance += "\n"
        
        # Add next steps
        next_steps = config.get("next_steps", [])
        if next_steps:
            guidance += "### 🎯 Next Steps for Your Business:\n\n"
            for step in next_steps:
                timeline = step.get("timeline", "")
                items = step.get("items", [])
                guidance += f"**{timeline}:**\n"
                for item in items:
                    guidance += f"   - {item}\n"
                guidance += "\n"
        
        # Add pro tip
        pro_tip = config.get("pro_tip", "")
        if pro_tip:
            guidance += f"**💡 Pro Tip**: {pro_tip}\n\n"
        
        return guidance
    
    def _generate_general_guidance(self, business_description: str) -> str:
        """Generate general guidance when no specific business type is detected."""
        guidance = "## 🏢 Delaware General Business Requirements\n\n"
        guidance += "### 📋 General Setup Process:\n\n"
        
        guidance += "**Step 1: Business Registration**\n"
        guidance += "- ✅ Register your business with Delaware Division of Corporations\n"
        guidance += "- ✅ Obtain a Delaware business license\n"
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
        
        # Add general resources
        guidance += "### 🔗 Essential Delaware Resources:\n\n"
        general_resources = self.business_types.get("general_resources", {})
        
        for category, resource_list in general_resources.items():
            if resource_list:
                category_title = category.replace("_", " ").title()
                guidance += f"**{category_title}:**\n"
                for resource in resource_list:
                    name = resource.get("name", "")
                    url = resource.get("url", "")
                    guidance += f"- 🔗 [{name}]({url})\n"
                guidance += "\n"
        
        return guidance
    
    def get_business_sources(self, business_type: str) -> List[str]:
        """Get source attribution for a business type."""
        config = self.get_business_config(business_type)
        if not config:
            return []
        
        sources = []
        resources = config.get("resources", {})
        
        for category, resource_list in resources.items():
            for resource in resource_list:
                name = resource.get("name", "")
                url = resource.get("url", "")
                if url and not url.startswith("tel:"):
                    sources.append(f"**{name}**: [{name}]({url})")
        
        return sources
    
    def get_search_query(self, business_type: str) -> str:
        """Get search query for a business type."""
        config = self.get_business_config(business_type)
        return config.get("search_query", "business") if config else "business" 
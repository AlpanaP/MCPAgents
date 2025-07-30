import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup

@dataclass
class Tool:
    name: str
    description: str
    inputSchema: Dict[str, Any]

@dataclass
class TextContent:
    type: str
    text: str

@dataclass
class ToolResult:
    content: List[TextContent]

class GenericLicenseServer:
    """Generic MCP server for business license information."""
    
    def __init__(self, state_config: Dict[str, Any] = None):
        """Initialize the generic MCP server."""
        self.logger = logging.getLogger(__name__)
        self.state_config = state_config or {}
        
    def list_tools(self) -> List[Tool]:
        """List available MCP tools."""
        return [
            Tool(
                name="get_license_summary",
                description="Get a structured summary of licenses needed for a business type in a specific location",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "business_type": {
                            "type": "string",
                            "description": "The type of business (e.g., construction, restaurant, real estate)"
                        },
                        "location": {
                            "type": "string",
                            "description": "The location (state/province and city)"
                        }
                    },
                    "required": ["business_type", "location"]
                }
            ),
            Tool(
                name="get_license_requirements",
                description="Get detailed requirements for a specific license type",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "license_type": {
                            "type": "string",
                            "description": "The specific license type"
                        },
                        "state": {
                            "type": "string",
                            "description": "The state or province"
                        }
                    },
                    "required": ["license_type", "state"]
                }
            ),
            Tool(
                name="get_application_sequence",
                description="Get the step-by-step application sequence for business licensing",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "business_type": {
                            "type": "string",
                            "description": "The type of business"
                        },
                        "state": {
                            "type": "string",
                            "description": "The state or province"
                        }
                    },
                    "required": ["business_type", "state"]
                }
            ),
            Tool(
                name="get_additional_comments",
                description="Get additional important information and comments for business licensing",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "business_type": {
                            "type": "string",
                            "description": "The type of business"
                        },
                        "state": {
                            "type": "string",
                            "description": "The state or province"
                        }
                    },
                    "required": ["business_type", "state"]
                }
            )
        ]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Call a specific MCP tool."""
        try:
            if name == "get_license_summary":
                return await self._get_license_summary(
                    arguments.get("business_type", ""),
                    arguments.get("location", "")
                )
            elif name == "get_license_requirements":
                return await self._get_license_requirements(
                    arguments.get("license_type", ""),
                    arguments.get("state", "")
                )
            elif name == "get_application_sequence":
                return await self._get_application_sequence(
                    arguments.get("business_type", ""),
                    arguments.get("state", "")
                )
            elif name == "get_additional_comments":
                return await self._get_additional_comments(
                    arguments.get("business_type", ""),
                    arguments.get("state", "")
                )
            else:
                return ToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")])
        except Exception as e:
            self.logger.error(f"Error calling tool {name}: {e}")
            return ToolResult(content=[TextContent(type="text", text=f"Error: {str(e)}")])
    
    async def _get_license_summary(self, business_type: str, location: str) -> ToolResult:
        """Get a structured summary of licenses needed."""
        industry_patterns = self.state_config.get("industry_patterns", {})
        
        # Find matching industry
        matching_industry = None
        for industry, pattern in industry_patterns.items():
            if business_type.lower() in pattern.get("keywords", []):
                matching_industry = industry
                break
        
        if not matching_industry:
            # Try to match by business type name
            for industry in industry_patterns.keys():
                if business_type.lower() in industry.lower():
                    matching_industry = industry
                    break
        
        if matching_industry:
            pattern = industry_patterns[matching_industry]
            license_types = pattern.get("license_types", [])
            fees = pattern.get("fees", [])
            due_dates = pattern.get("due_dates", [])
            
            summary = [
                f"## License Summary for {business_type.title()} in {location}\n\n",
                "### Required Licenses:\n"
            ]
            
            for i, license_type in enumerate(license_types):
                summary.append(f"- **{license_type}**\n")
                if i < len(fees):
                    summary.append(f"  - Cost: {fees[i]}\n")
                else:
                    summary.append(f"  - Cost: Application fee + License fee\n")
                
                if i < len(due_dates):
                    summary.append(f"  - Due Date: {due_dates[i]}\n")
                else:
                    summary.append(f"  - Due Date: Apply before starting business operations\n")
                
                summary.append(f"  - Renewal: Annual renewal required\n\n")
            
            summary.append(f"### Description:\n")
            summary.append(f"These licenses are required for {business_type} operations in {location}. ")
            summary.append(f"Each license type covers specific aspects of {matching_industry} business operations.\n\n")
            
            summary.append(f"### Application URLs:\n")
            summary.append(f"- **Main Licensing Portal**: {self.state_config.get('url_patterns', {}).get('main_license_site', 'https://state.gov/')}\n")
            summary.append(f"- **Application Portal**: {self.state_config.get('url_patterns', {}).get('application_portal', 'https://state.gov/apply/')}\n")
            summary.append(f"- **Requirements**: {self.state_config.get('url_patterns', {}).get('requirements', 'https://state.gov/requirements/')}\n")
            summary.append(f"- **Fee Schedule**: {self.state_config.get('url_patterns', {}).get('fees', 'https://state.gov/fees/')}\n")
            
        else:
            summary = [
                f"## License Summary for {business_type.title()} in {location}\n\n",
                "### Required Licenses:\n",
                "- **General Business License**: Basic business operations\n",
                "  - Cost: $50-200 application fee\n",
                "  - Due Date: Apply before starting business operations\n",
                "  - Renewal: Annual renewal required\n\n",
                "- **Industry-Specific License**: Based on business type\n",
                "  - Cost: $100-500 application fee\n",
                "  - Due Date: Apply before starting business operations\n",
                "  - Renewal: Annual renewal required\n\n",
                "- **Local Business License**: City/county requirements\n",
                "  - Cost: $25-150 application fee\n",
                "  - Due Date: Apply before starting business operations\n",
                "  - Renewal: Annual renewal required\n\n",
                "### Description:\n",
                f"Standard business licensing requirements for {business_type} operations in {location}.\n\n",
                "### Application URLs:\n",
                "- **Main Licensing Portal**: https://state.gov/\n",
                "- **Application Portal**: https://state.gov/apply/\n",
                "- **Requirements**: https://state.gov/requirements/\n",
                "- **Fee Schedule**: https://state.gov/fees/\n"
            ]
        
        return ToolResult(content=[TextContent(type="text", text="".join(summary))])
    
    async def _get_license_requirements(self, license_type: str, state: str) -> ToolResult:
        """Get detailed requirements for a specific license type."""
        industry_patterns = self.state_config.get("industry_patterns", {})
        
        # Find the industry that matches the license type
        matching_industry = None
        for industry, pattern in industry_patterns.items():
            if license_type.lower() in [lt.lower() for lt in pattern.get("license_types", [])]:
                matching_industry = industry
                break
        
        if matching_industry:
            pattern = industry_patterns[matching_industry]
            requirements = pattern.get("requirements", [])
            fees = pattern.get("fees", [])
            due_dates = pattern.get("due_dates", [])
            
            result = [
                f"## {license_type} Requirements in {state}\n\n",
                "### Requirements:\n"
            ]
            
            for requirement in requirements:
                result.append(f"- {requirement}\n")
            
            result.append(f"\n### Costs and Fees:\n")
            for fee in fees:
                result.append(f"- {fee}\n")
            
            result.append(f"\n### Due Dates:\n")
            if due_dates:
                for due_date in due_dates:
                    result.append(f"- {due_date}\n")
            else:
                result.append("- **Application**: Submit 30-60 days before planned business start\n")
                result.append("- **Background Check**: Complete before license approval\n")
                result.append("- **Examination**: Pass required exam before application\n")
                result.append("- **Renewal**: Annual renewal due 30 days before expiration\n")
            
            result.append(f"\n### Application Process:\n")
            result.append("1. Complete required education/training\n")
            result.append("2. Pass required examination\n")
            result.append("3. Submit background check\n")
            result.append("4. Provide proof of financial responsibility\n")
            result.append("5. Submit application with fees\n")
            result.append("6. Wait for approval (4-8 weeks)\n\n")
            
            result.append(f"### Application URLs:\n")
            result.append(f"- **Application Portal**: {self.state_config.get('url_patterns', {}).get('application_portal', 'https://state.gov/apply/')}\n")
            result.append(f"- **Requirements**: {self.state_config.get('url_patterns', {}).get('requirements', 'https://state.gov/requirements/')}\n")
            result.append(f"- **Fees**: {self.state_config.get('url_patterns', {}).get('fees', 'https://state.gov/fees/')}\n")
            
        else:
            result = [
                f"## {license_type} Requirements in {state}\n\n",
                "### Requirements:\n",
                "- Complete required education/training\n",
                "- Pass required examination\n",
                "- Submit background check\n",
                "- Provide proof of financial responsibility\n",
                "- Submit application with fees\n\n",
                "### Costs and Fees:\n",
                "- Application fee: $50-200\n",
                "- License fee: $100-500\n",
                "- Background check fee: $25-75\n",
                "- Examination fee: $50-150\n",
                "- Renewal fee: $50-200 annually\n\n",
                "### Due Dates:\n",
                "- **Application**: Submit 30-60 days before planned business start\n",
                "- **Background Check**: Complete before license approval\n",
                "- **Examination**: Pass required exam before application\n",
                "- **Renewal**: Annual renewal due 30 days before expiration\n\n",
                "### Application Process:\n",
                "1. Complete required education/training\n",
                "2. Pass required examination\n",
                "3. Submit background check\n",
                "4. Provide proof of financial responsibility\n",
                "5. Submit application with fees\n",
                "6. Wait for approval (4-8 weeks)\n\n",
                "### Application URLs:\n",
                "- **Application Portal**: https://state.gov/apply/\n",
                "- **Requirements**: https://state.gov/requirements/\n",
                "- **Fees**: https://state.gov/fees/\n"
            ]
        
        return ToolResult(content=[TextContent(type="text", text="".join(result))])
    
    async def _get_application_sequence(self, business_type: str, state: str) -> ToolResult:
        """Get the step-by-step application sequence."""
        sequence = [
            f"## Application Sequence for {business_type.title()} in {state}\n\n",
            "### Step 1: Business Registration\n",
            "- Register business entity with state Division of Corporations\n",
            "- Choose business structure (LLC, Corporation, Partnership)\n",
            "- File Articles of Organization/Incorporation\n",
            "- Obtain EIN from IRS\n\n",
            "### Step 2: Industry-Specific Licensing\n",
            "- Determine required licenses for your business type\n",
            "- Complete required education or training\n",
            "- Pass required examinations\n",
            "- Submit background checks if required\n",
            "- Apply for licenses through state portal\n\n",
            "### Step 3: Tax Registration\n",
            "- Register for state sales tax\n",
            "- Register for federal taxes\n",
            "- Set up accounting and record keeping\n\n",
            "### Step 4: Local Requirements\n",
            "- Check local city/county requirements\n",
            "- Apply for local business licenses\n",
            "- Check zoning requirements\n",
            "- Obtain local permits if needed\n\n",
            "### Step 5: Insurance and Compliance\n",
            "- Obtain required insurance coverage\n",
            "- Set up compliance monitoring\n",
            "- Establish record keeping procedures\n\n",
            "### Timeline:\n",
            "- Business registration: 1-2 weeks\n",
            "- License application: 4-8 weeks\n",
            "- Local permits: 2-4 weeks\n",
            "- Total estimated time: 2-3 months\n\n",
            "### Application URLs:\n",
            f"- **Business Registration**: {self.state_config.get('url_patterns', {}).get('business_registration', 'https://state.gov/business/')}\n",
            f"- **License Application**: {self.state_config.get('url_patterns', {}).get('application_portal', 'https://state.gov/apply/')}\n",
            f"- **Requirements**: {self.state_config.get('url_patterns', {}).get('requirements', 'https://state.gov/requirements/')}\n"
        ]
        
        return ToolResult(content=[TextContent(type="text", text="".join(sequence))])
    
    async def _get_additional_comments(self, business_type: str, state: str) -> ToolResult:
        """Get additional important information and comments."""
        comments = [
            f"## Additional Comments for {business_type.title()} in {state}\n\n",
            "### Important Notes:\n",
            "- **Timing**: Start the application process 2-3 months before planned opening\n",
            "- **Costs**: Budget for application fees, licensing fees, and insurance costs\n",
            "- **Compliance**: Maintain ongoing compliance with state and local regulations\n",
            "- **Renewals**: Most licenses require annual renewal with continuing education\n\n",
            "### Common Pitfalls:\n",
            "- Not checking local zoning requirements before signing leases\n",
            "- Underestimating the time required for background checks\n",
            "- Not having sufficient financial resources for bonds/insurance\n",
            "- Missing required education or training hours\n\n",
            "### Pro Tips:\n",
            "- Contact the licensing board early to clarify requirements\n",
            "- Keep detailed records of all education and experience\n",
            "- Consider hiring a business consultant for complex applications\n",
            "- Network with other business owners in your industry\n\n",
            "### Resources:\n",
            f"- **State Licensing Board**: {self.state_config.get('url_patterns', {}).get('main_license_site', 'https://state.gov/')}\n",
            f"- **Business Support**: {self.state_config.get('url_patterns', {}).get('contact', 'https://state.gov/contact/')}\n",
            "- **SBA Resources**: https://www.sba.gov/\n",
            "- **SCORE Mentoring**: https://www.score.org/\n\n",
            "### Contact Information:\n",
            "- **State Licensing Board**: Contact through state website\n",
            "- **Local Government**: Check city/county websites\n",
            "- **Business Support**: State economic development office\n"
        ]
        
        return ToolResult(content=[TextContent(type="text", text="".join(comments))]) 
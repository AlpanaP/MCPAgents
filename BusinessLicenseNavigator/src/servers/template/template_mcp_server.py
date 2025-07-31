"""
Template MCP Server for New States/Provinces.

This template provides a base structure for creating MCP servers for new states.
Customize the tools, responses, and business logic for your specific state.
"""

import logging
from typing import Dict, Any, List, Optional
from core.models.base_mcp_server import BaseMCPServer, MCPConfig, Tool, ToolResult
from core.models.text_content import TextContent


class TemplateMCPServer(BaseMCPServer):
    """
    Template MCP Server for {STATE_NAME}.
    
    This server provides business license tools for {STATE_NAME}.
    Customize the tools and responses for your specific state.
    """
    
    def __init__(self, config: MCPConfig):
        """Initialize the template MCP server."""
        super().__init__(config)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Customize these for your state
        self.state_code = "TEMPLATE"  # Change to your state code
        self.state_name = "Template State"  # Change to your state name
        
        # Initialize state-specific data
        self._init_state_data()
    
    def _init_state_data(self):
        """Initialize state-specific data."""
        # Customize this data for your state
        self.license_categories = [
            "General Business License",
            "Industry-Specific License",
            "Professional License",
            "Local Business License"
        ]
        
        self.business_types = {
            "construction": {
                "keywords": ["construction", "contractor", "building"],
                "license_types": ["General Contractor", "Building Contractor"],
                "requirements": ["Background check", "Experience verification"],
                "fees": ["Application fee: $200-500", "License fee: $300-800"],
                "timeline": "60-90 days"
            },
            "food_service": {
                "keywords": ["restaurant", "food", "cafe", "catering"],
                "license_types": ["Food Service License", "Restaurant License"],
                "requirements": ["Food safety training", "Health inspection"],
                "fees": ["Application fee: $100-300", "License fee: $200-500"],
                "timeline": "30-45 days"
            }
        }
        
        self.business_steps = [
            "1. Choose your business structure (LLC, Corporation, etc.)",
            "2. Register your business with the state",
            "3. Obtain necessary licenses and permits",
            "4. Set up tax accounts",
            "5. Get insurance coverage",
            "6. Set up business banking",
            "7. Comply with local regulations"
        ]
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """
        Call a specific tool.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            ToolResult with the response
        """
        try:
            self.logger.info(f"Calling tool: {tool_name} with arguments: {arguments}")
            
            if tool_name == "get_license_summary":
                return await self._get_license_summary(arguments)
            elif tool_name == "get_license_requirements":
                return await self._get_license_requirements(arguments)
            elif tool_name == "get_application_sequence":
                return await self._get_application_sequence(arguments)
            elif tool_name == "get_additional_comments":
                return await self._get_additional_comments(arguments)
            else:
                return ToolResult(
                    success=False,
                    content=TextContent(
                        text=f"Unknown tool: {tool_name}",
                        source="template_mcp_server"
                    )
                )
                
        except Exception as e:
            self.logger.error(f"Error calling tool {tool_name}: {e}")
            return ToolResult(
                success=False,
                content=TextContent(
                    text=f"Error calling tool: {str(e)}",
                    source="template_mcp_server"
                )
            )
    
    async def _get_license_summary(self, arguments: Dict[str, Any]) -> ToolResult:
        """Get a structured summary of licenses needed."""
        business_type = arguments.get("business_type", "").lower()
        location = arguments.get("location", "")
        
        # Find matching business type
        matching_type = None
        for type_name, config in self.business_types.items():
            if any(keyword in business_type for keyword in config["keywords"]):
                matching_type = type_name
                break
        
        if not matching_type:
            return ToolResult(
                success=False,
                content=TextContent(
                    text="No license information found for this business type.",
                    source="template_mcp_server"
                )
            )
        
        config = self.business_types[matching_type]
        
        summary = f"""# {self.state_name} License Summary for {matching_type.title()}

**Business Type:** {matching_type.title()}
**Location:** {location}

## Required Licenses:
{chr(10).join(f"- {license_type}" for license_type in config["license_types"])}

## Requirements:
{chr(10).join(f"- {requirement}" for requirement in config["requirements"])}

## Fees:
{chr(10).join(f"- {fee}" for fee in config["fees"])}

## Timeline:
- {config["timeline"]}

## Next Steps:
1. Review requirements
2. Gather necessary documents
3. Submit application
4. Pay required fees
5. Wait for approval
"""
        
        return ToolResult(
            success=True,
            content=TextContent(
                text=summary,
                source="template_mcp_server",
                metadata={
                    "state": self.state_code,
                    "business_type": matching_type,
                    "location": location
                }
            )
        )
    
    async def _get_license_requirements(self, arguments: Dict[str, Any]) -> ToolResult:
        """Get detailed requirements for a specific license type."""
        license_type = arguments.get("license_type", "")
        state = arguments.get("state", "")
        
        # Find matching license type
        matching_config = None
        for business_type, config in self.business_types.items():
            if license_type.lower() in [lt.lower() for lt in config["license_types"]]:
                matching_config = config
                break
        
        if not matching_config:
            return ToolResult(
                success=False,
                content=TextContent(
                    text=f"No detailed requirements found for {license_type}.",
                    source="template_mcp_server"
                )
            )
        
        requirements = f"""# Detailed Requirements for {license_type}

## Requirements:
{chr(10).join(f"- {requirement}" for requirement in matching_config["requirements"])}

## Fees:
{chr(10).join(f"- {fee}" for fee in matching_config["fees"])}

## Timeline:
- {matching_config["timeline"]}

## Additional Information:
- Contact the state licensing board for specific requirements
- Ensure all documents are properly notarized
- Keep copies of all submitted materials
- Follow up on application status regularly
"""
        
        return ToolResult(
            success=True,
            content=TextContent(
                text=requirements,
                source="template_mcp_server",
                metadata={
                    "state": self.state_code,
                    "license_type": license_type
                }
            )
        )
    
    async def _get_application_sequence(self, arguments: Dict[str, Any]) -> ToolResult:
        """Get the step-by-step application sequence."""
        business_type = arguments.get("business_type", "")
        state = arguments.get("state", "")
        
        sequence = f"""# Application Sequence for {business_type.title()} in {state}

## Step-by-Step Process:

{chr(10).join(self.business_steps)}

## Additional Steps for {business_type.title()}:
1. Complete required training courses
2. Pass background checks
3. Provide proof of insurance
4. Submit to inspections (if required)
5. Pay all applicable fees
6. Wait for license approval

## Timeline:
- Total process: 60-90 days
- Background check: 30 days
- Training completion: 45 days before application
- License processing: 30-45 days after submission

## Important Notes:
- Start the process early to avoid delays
- Keep all documentation organized
- Follow up regularly on application status
- Maintain compliance with all requirements
"""
        
        return ToolResult(
            success=True,
            content=TextContent(
                text=sequence,
                source="template_mcp_server",
                metadata={
                    "state": self.state_code,
                    "business_type": business_type
                }
            )
        )
    
    async def _get_additional_comments(self, arguments: Dict[str, Any]) -> ToolResult:
        """Get additional important information and comments."""
        business_type = arguments.get("business_type", "")
        state = arguments.get("state", "")
        
        comments = f"""# Additional Information for {business_type.title()} in {state}

## Important Considerations:

### Legal Requirements:
- Consult with a business attorney for legal advice
- Ensure compliance with all state and local regulations
- Maintain proper record-keeping practices

### Financial Planning:
- Budget for all application and license fees
- Consider ongoing compliance costs
- Plan for insurance requirements

### Operational Considerations:
- Develop standard operating procedures
- Train staff on compliance requirements
- Establish monitoring and reporting systems

### Risk Management:
- Obtain appropriate insurance coverage
- Implement safety protocols
- Regular compliance audits

### Resources:
- State Business Licensing Website
- Local Chamber of Commerce
- Small Business Development Center
- Professional Associations

## Contact Information:
- State Licensing Board: (555) 123-4567
- Business Development Office: (555) 987-6543
- Emergency Contact: (555) 111-2222

## Notes:
- All information is subject to change
- Verify requirements with official sources
- Keep documentation for at least 7 years
- Regular license renewal required
"""
        
        return ToolResult(
            success=True,
            content=TextContent(
                text=comments,
                source="template_mcp_server",
                metadata={
                    "state": self.state_code,
                    "business_type": business_type
                }
            )
        )
    
    def get_state_info(self) -> Dict[str, Any]:
        """Get information about this state's MCP server."""
        return {
            "state_code": self.state_code,
            "state_name": self.state_name,
            "license_categories": self.license_categories,
            "business_types": list(self.business_types.keys()),
            "available_tools": [tool.name for tool in self.tools]
        } 
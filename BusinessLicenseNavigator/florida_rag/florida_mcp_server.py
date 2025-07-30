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

class FloridaLicenseServer:
    """Florida MCP server for business license information."""
    
    def __init__(self):
        """Initialize the Florida MCP server."""
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://www2.myfloridalicense.com/"
        
    def list_tools(self) -> List[Tool]:
        """List available MCP tools."""
        return [
            Tool(
                name="get_florida_license_categories",
                description="Get all available Florida business license categories",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="get_florida_license_details",
                description="Get detailed information about a specific Florida license type",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "license_type": {
                            "type": "string",
                            "description": "The type of license to get details for"
                        }
                    },
                    "required": ["license_type"]
                }
            ),
            Tool(
                name="search_florida_licenses",
                description="Search Florida licenses by keyword",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for Florida licenses"
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="get_florida_business_steps",
                description="Get step-by-step process for Florida business registration",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="get_florida_construction_requirements",
                description="Get specific requirements for Florida construction contractor licenses",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="get_palm_harbor_requirements",
                description="Get local requirements for business in Palm Harbor, Florida",
                inputSchema={"type": "object", "properties": {}}
            )
        ]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Call a specific MCP tool."""
        try:
            if name == "get_florida_license_categories":
                return await self._get_florida_license_categories()
            elif name == "get_florida_license_details":
                return await self._get_florida_license_details(arguments.get("license_type", ""))
            elif name == "search_florida_licenses":
                return await self._search_florida_licenses(arguments.get("query", ""))
            elif name == "get_florida_business_steps":
                return await self._get_florida_business_steps()
            elif name == "get_florida_construction_requirements":
                return await self._get_florida_construction_requirements()
            elif name == "get_palm_harbor_requirements":
                return await self._get_palm_harbor_requirements()
            else:
                return ToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")])
        except Exception as e:
            self.logger.error(f"Error calling tool {name}: {e}")
            return ToolResult(content=[TextContent(type="text", text=f"Error: {str(e)}")])
    
    async def _get_florida_license_categories(self) -> ToolResult:
        """Get Florida license categories."""
        categories = [
            "## Florida Business License Categories\n\n",
            "### Construction Industry\n",
            "- **General Contractor**: Residential and commercial construction\n",
            "- **Building Contractor**: Structural construction\n",
            "- **Residential Contractor**: Single-family and multi-family homes\n",
            "- **Roofing Contractor**: Roof installation and repair\n",
            "- **Plumbing Contractor**: Plumbing systems\n",
            "- **Electrical Contractor**: Electrical systems\n",
            "- **HVAC Contractor**: Heating, ventilation, air conditioning\n",
            "- **Specialty Contractor**: Specific trades\n\n",
            "### Real Estate\n",
            "- **Real Estate Broker**: Licensed to sell real estate\n",
            "- **Real Estate Sales Associate**: Licensed to assist brokers\n",
            "- **Property Manager**: Manage rental properties\n\n",
            "### Food Service\n",
            "- **Restaurant License**: Food service establishments\n",
            "- **Catering License**: Food catering services\n",
            "- **Food Service License**: Various food service operations\n\n",
            "### Professional Services\n",
            "- **Accountant**: Certified public accountants\n",
            "- **Attorney**: Legal services\n",
            "- **Engineer**: Professional engineering\n",
            "- **Architect**: Professional architecture\n\n",
            "**Source**: [MyFloridaLicense.com](https://www2.myfloridalicense.com/)"
        ]
        
        return ToolResult(content=[TextContent(type="text", text="".join(categories))])
    
    async def _get_florida_license_details(self, license_type: str) -> ToolResult:
        """Get detailed information about a specific Florida license."""
        license_details = {
            "construction": [
                "## Florida Construction Contractor License Details\n\n",
                "### Requirements:\n",
                "- Must be at least 18 years old\n",
                "- Pass background check\n",
                "- Pass Florida contractor examination\n",
                "- Provide proof of financial responsibility\n",
                "- Submit application with required fees\n\n",
                "### Application Process:\n",
                "1. Register business entity with Florida Division of Corporations\n",
                "2. Complete background check through DBPR\n",
                "3. Study and pass Florida contractor exam\n",
                "4. Obtain proof of financial responsibility (bond/insurance)\n",
                "5. Submit application through MyFloridaLicense.com\n",
                "6. Pay application and licensing fees\n",
                "7. Wait for approval (typically 4-6 weeks)\n\n",
                "### Fees:\n",
                "- Application fee: $249\n",
                "- License fee: $209\n",
                "- Background check: $50\n",
                "- Exam fee: $135\n\n",
                "**Source**: [Florida Construction Industry Licensing Board](https://www.myfloridalicense.com/DBPR/construction-industry-licensing-board/)"
            ],
            "real_estate": [
                "## Florida Real Estate License Details\n\n",
                "### Requirements:\n",
                "- Complete 63 hours of pre-licensing education\n",
                "- Pass Florida real estate exam\n",
                "- Submit application with fingerprints\n",
                "- Pay licensing fees\n\n",
                "### Application Process:\n",
                "1. Complete pre-licensing education\n",
                "2. Pass Florida real estate examination\n",
                "3. Submit application through MyFloridaLicense.com\n",
                "4. Complete fingerprinting\n",
                "5. Pay licensing fees\n",
                "6. Wait for approval\n\n",
                "**Source**: [Florida Real Estate Commission](https://www.myfloridalicense.com/DBPR/real-estate-commission/)"
            ],
            "food": [
                "## Florida Food Service License Details\n\n",
                "### Requirements:\n",
                "- Complete food safety training\n",
                "- Pass health inspection\n",
                "- Submit application with fees\n",
                "- Comply with health regulations\n\n",
                "### Application Process:\n",
                "1. Complete food safety training\n",
                "2. Pass health department inspection\n",
                "3. Submit application through MyFloridaLicense.com\n",
                "4. Pay licensing fees\n",
                "5. Receive license\n\n",
                "**Source**: [Florida Division of Hotels and Restaurants](https://www.myfloridalicense.com/DBPR/hotels-restaurants/)"
            ]
        }
        
        details = license_details.get(license_type.lower(), ["No specific details available for this license type."])
        return ToolResult(content=[TextContent(type="text", text="".join(details))])
    
    async def _search_florida_licenses(self, query: str) -> ToolResult:
        """Search Florida licenses by keyword."""
        search_results = [
            f"## Florida License Search Results for: {query}\n\n"
        ]
        
        if "construction" in query.lower() or "contractor" in query.lower():
            search_results.extend([
                "### Construction Licenses Found:\n",
                "- **General Contractor**: Residential and commercial construction\n",
                "- **Building Contractor**: Structural construction\n",
                "- **Residential Contractor**: Single-family and multi-family homes\n",
                "- **Roofing Contractor**: Roof installation and repair\n",
                "- **Plumbing Contractor**: Plumbing systems\n",
                "- **Electrical Contractor**: Electrical systems\n",
                "- **HVAC Contractor**: Heating, ventilation, air conditioning\n\n",
                "**Source**: [Florida Construction Industry Licensing Board](https://www.myfloridalicense.com/DBPR/construction-industry-licensing-board/)"
            ])
        elif "real estate" in query.lower() or "realtor" in query.lower():
            search_results.extend([
                "### Real Estate Licenses Found:\n",
                "- **Real Estate Broker**: Licensed to sell real estate\n",
                "- **Real Estate Sales Associate**: Licensed to assist brokers\n",
                "- **Property Manager**: Manage rental properties\n\n",
                "**Source**: [Florida Real Estate Commission](https://www.myfloridalicense.com/DBPR/real-estate-commission/)"
            ])
        elif "food" in query.lower() or "restaurant" in query.lower():
            search_results.extend([
                "### Food Service Licenses Found:\n",
                "- **Restaurant License**: Food service establishments\n",
                "- **Catering License**: Food catering services\n",
                "- **Food Service License**: Various food service operations\n\n",
                "**Source**: [Florida Division of Hotels and Restaurants](https://www.myfloridalicense.com/DBPR/hotels-restaurants/)"
            ])
        else:
            search_results.append("No specific Florida licenses found for your search query.")
        
        return ToolResult(content=[TextContent(type="text", text="".join(search_results))])
    
    async def _get_florida_business_steps(self) -> ToolResult:
        """Get step-by-step process for Florida business registration."""
        steps = [
            "## Florida Business Registration Steps\n\n",
            "### Step 1: Business Entity Registration\n",
            "- Register your business with Florida Division of Corporations\n",
            "- Choose between LLC, Corporation, or Partnership\n",
            "- File Articles of Organization/Incorporation\n",
            "- Obtain EIN from IRS\n\n",
            "### Step 2: Industry-Specific Licensing\n",
            "- Determine required licenses for your business type\n",
            "- Apply for licenses through MyFloridaLicense.com\n",
            "- Complete required education or training\n",
            "- Pass required examinations\n",
            "- Submit background checks if required\n\n",
            "### Step 3: Tax Registration\n",
            "- Register for Florida sales tax\n",
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
            "**Source**: [MyFloridaLicense.com](https://www2.myfloridalicense.com/)"
        ]
        
        return ToolResult(content=[TextContent(type="text", text="".join(steps))])
    
    async def _get_florida_construction_requirements(self) -> ToolResult:
        """Get specific requirements for Florida construction contractor licenses."""
        requirements = [
            "## Florida Construction Contractor License Requirements\n\n",
            "### Basic Requirements:\n",
            "- Must be at least 18 years old\n",
            "- Must be a U.S. citizen or legal resident\n",
            "- Must have good moral character\n",
            "- Must pass background check\n\n",
            "### Education and Experience:\n",
            "- Complete required education hours\n",
            "- Demonstrate relevant work experience\n",
            "- Pass Florida contractor examination\n\n",
            "### Financial Requirements:\n",
            "- Provide proof of financial responsibility\n",
            "- Obtain surety bond or insurance\n",
            "- Demonstrate financial stability\n\n",
            "### Application Process:\n",
            "1. Register business entity with Florida Division of Corporations\n",
            "2. Complete background check through DBPR\n",
            "3. Study and pass Florida contractor exam\n",
            "4. Obtain proof of financial responsibility\n",
            "5. Submit application through MyFloridaLicense.com\n",
            "6. Pay application and licensing fees\n",
            "7. Wait for approval (typically 4-6 weeks)\n\n",
            "### Fees:\n",
            "- Application fee: $249\n",
            "- License fee: $209\n",
            "- Background check: $50\n",
            "- Exam fee: $135\n",
            "- Total estimated cost: $643\n\n",
            "### License Types:\n",
            "- **General Contractor**: Residential and commercial construction\n",
            "- **Building Contractor**: Structural construction\n",
            "- **Residential Contractor**: Single-family and multi-family homes\n",
            "- **Roofing Contractor**: Roof installation and repair\n",
            "- **Plumbing Contractor**: Plumbing systems\n",
            "- **Electrical Contractor**: Electrical systems\n",
            "- **HVAC Contractor**: Heating, ventilation, air conditioning\n\n",
            "**Source**: [Florida Construction Industry Licensing Board](https://www.myfloridalicense.com/DBPR/construction-industry-licensing-board/)"
        ]
        
        return ToolResult(content=[TextContent(type="text", text="".join(requirements))])
    
    async def _get_palm_harbor_requirements(self) -> ToolResult:
        """Get local requirements for business in Palm Harbor, Florida."""
        requirements = [
            "## Palm Harbor, Florida Business Requirements\n\n",
            "### Location Information:\n",
            "- **County**: Pinellas County\n",
            "- **State**: Florida\n",
            "- **Population**: Approximately 60,000\n",
            "- **Business Climate**: Growing residential and commercial area\n\n",
            "### Local Government Requirements:\n",
            "1. **Palm Harbor Development Services Department**\n",
            "   - Building permits for construction projects\n",
            "   - Zoning compliance checks\n",
            "   - Development approvals\n",
            "   - Contact: (727) 784-3600\n\n",
            "2. **Pinellas County Building Department**\n",
            "   - County-level building permits\n",
            "   - Construction inspections\n",
            "   - Code compliance\n",
            "   - Contact: (727) 464-3888\n\n",
            "### Business Registration Steps:\n",
            "1. **State Level**: Register with Florida Division of Corporations\n",
            "2. **County Level**: Check Pinellas County requirements\n",
            "3. **City Level**: Apply for Palm Harbor business license\n",
            "4. **Industry Level**: Obtain required professional licenses\n\n",
            "### Construction-Specific Requirements:\n",
            "- Valid Florida contractor license required\n",
            "- Palm Harbor building permits for construction projects\n",
            "- Pinellas County inspections required\n",
            "- Compliance with local building codes\n",
            "- Zoning approval for commercial projects\n\n",
            "### Local Resources:\n",
            "- **Palm Harbor Development Services**: https://www.palmharbor.org/departments/development-services/\n",
            "- **Pinellas County Building Department**: https://www.pinellascounty.org/building/\n",
            "- **Palm Harbor Chamber of Commerce**: Local business networking\n",
            "- **Pinellas County Economic Development**: Business support services\n\n",
            "### Contact Information:\n",
            "- **Palm Harbor City Hall**: (727) 784-3600\n",
            "- **Pinellas County Building**: (727) 464-3888\n",
            "- **Florida DBPR**: (850) 487-1395\n\n",
            "**Source**: [Palm Harbor Development Services](https://www.palmharbor.org/departments/development-services/)"
        ]
        
        return ToolResult(content=[TextContent(type="text", text="".join(requirements))]) 
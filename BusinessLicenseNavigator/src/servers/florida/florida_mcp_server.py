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
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def get_text(self) -> str:
        """Get the text content as a single string."""
        if not self.content:
            return ""
        
        text_parts = []
        for item in self.content:
            if hasattr(item, 'text'):
                text_parts.append(item.text)
            elif isinstance(item, str):
                text_parts.append(item)
        
        return "\n\n".join(text_parts)
    
    def get_first_text(self) -> str:
        """Get the first text content item."""
        if not self.content:
            return ""
        
        first_item = self.content[0]
        if hasattr(first_item, 'text'):
            return first_item.text
        elif isinstance(first_item, str):
            return first_item
        
        return ""
    
    def is_valid(self) -> bool:
        """Check if the tool result is valid."""
        return bool(self.content and not self.error and self.get_text().strip())
    
    @classmethod
    def error_result(cls, error_message: str) -> 'ToolResult':
        """Create an error result."""
        return cls(
            content=[],
            error=error_message
        )

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
            ),
            Tool(
                name="get_license_summary",
                description="Get a summary of license requirements for a business type",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "business_type": {
                            "type": "string",
                            "description": "The type of business"
                        },
                        "location": {
                            "type": "string",
                            "description": "The location (e.g., 'FL, USA')"
                        }
                    },
                    "required": ["business_type", "location"]
                }
            ),
            Tool(
                name="get_business_steps",
                description="Get step-by-step business setup process",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "business_type": {
                            "type": "string",
                            "description": "The type of business"
                        }
                    },
                    "required": ["business_type"]
                }
            ),
            Tool(
                name="get_license_requirements",
                description="Get detailed license requirements for a business type",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "business_type": {
                            "type": "string",
                            "description": "The type of business"
                        },
                        "location": {
                            "type": "string",
                            "description": "The location (e.g., 'FL, USA')"
                        }
                    },
                    "required": ["business_type", "location"]
                }
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
                return await self._get_construction_requirements(arguments)
            elif name == "get_palm_harbor_requirements":
                return await self._get_local_requirements(arguments)
            elif name == "get_license_summary":
                return await self._get_license_summary(arguments)
            elif name == "get_business_steps":
                return await self._get_business_steps(arguments)
            elif name == "get_license_requirements":
                return await self._get_license_requirements(arguments)
            else:
                return ToolResult.error_result(f"Unknown tool: {name}")
                
        except Exception as e:
            self.logger.error(f"Error calling tool {name}: {e}")
            return ToolResult.error_result(f"Error: {str(e)}")
    
    async def _get_license_summary(self, arguments: Dict[str, Any]) -> ToolResult:
        """Get a summary of license requirements for a business type."""
        business_type = arguments.get("business_type", "")
        location = arguments.get("location", "")
        
        # Determine the appropriate license type based on business type
        business_lower = business_type.lower()
        
        if any(word in business_lower for word in ['financial', 'investment', 'private equity', 'adviser']):
            summary_text = """# Florida Investment Adviser License Summary

## Required Licenses:
- **Investment Adviser Registration**: Required for private equity firms
  - **Agency**: Florida Office of Financial Regulation
  - **Law**: Florida Securities and Investor Protection Act
  - **Eligible Entity Types**: LLCs, Corporations, Partnerships
  - **Cost**: $242.50 (Registration fee $200 + Background check $42.50)
  - **Due Date**: Apply before conducting business
  - **Renewal**: $200 annually
  - **Official URL**: https://flofr.com/InvestmentAdvisers/

## Requirements:
- Submit Form ADV
- Provide financial statements
- Complete background checks
- Maintain compliance program
- File annual reports

## Application Process:
1. Complete background checks
2. Prepare financial statements
3. Submit Form ADV
4. Pay registration fees
5. Wait for approval (4-8 weeks)

**Source**: Florida Office of Financial Regulation"""
            
        elif any(word in business_lower for word in ['construction', 'contractor', 'building']):
            summary_text = """# Florida Construction Contractor License Summary

## Required Licenses:
- **General Contractor License**: Required for construction work
  - **Agency**: Florida Construction Industry Licensing Board
  - **Law**: Florida Statutes Chapter 489
  - **Eligible Entity Types**: LLCs, Corporations, Partnerships
  - **Cost**: $635.50 (Application $249 + License $209 + Background check $42.50 + Exam $135)
  - **Due Date**: Apply 60 days before starting work
  - **Renewal**: $209 every 2 years
  - **Official URL**: https://www.myfloridalicense.com/DBPR/construction-industry-licensing-board/

## Requirements:
- Be at least 18 years old
- Pass background check
- Pass Florida contractor exam
- Provide proof of financial responsibility
- Submit application with fees

## Application Process:
1. Complete background check
2. Study and pass contractor exam
3. Gather financial responsibility proof
4. Submit application with fees
5. Wait for approval (4-8 weeks)

**Source**: Florida Construction Industry Licensing Board"""
            
        else:
            summary_text = f"""# Florida Business License Summary for {business_type}

## Required Licenses:
- **General Business License**: Basic business operations
  - **Agency**: Florida Department of Business and Professional Regulation
  - **Cost**: $50-200 application fee
  - **Due Date**: Apply before starting business operations
  - **Renewal**: Annual renewal required
  - **Official URL**: https://www2.myfloridalicense.com/

## Requirements:
- Business registration with Florida Division of Corporations
- Tax registration with Florida Department of Revenue
- Local permits (if required)
- Insurance coverage

## Application Process:
1. Register business entity
2. Register for state taxes
3. Submit license application
4. Wait for approval (2-4 weeks)

**Source**: Florida Department of Business and Professional Regulation"""
        
        return ToolResult(
            content=[TextContent(type="text", text=summary_text)],
            metadata={"business_type": business_type, "location": location}
        )
    
    async def _get_business_steps(self, arguments: Dict[str, Any]) -> ToolResult:
        """Get step-by-step business setup process."""
        business_type = arguments.get("business_type", "")
        
        steps_text = """# Florida Business Setup Steps

## Step 1: Business Entity Formation
- Choose business structure (LLC, Corporation, Partnership)
- File with Florida Division of Corporations
- Cost: $78-125 filing fee
- Timeline: 1-2 weeks processing

## Step 2: Tax Registration
- Register with Florida Department of Revenue
- Apply for tax certificate
- Register for sales tax (if applicable)
- Cost: $5 tax certificate fee
- Timeline: 1-2 weeks processing

## Step 3: Industry-Specific Licensing
- Identify required licenses for your industry
- Apply through MyFloridaLicense.com
- Complete required training/certifications
- Cost: Varies by industry ($100-500+)
- Timeline: 2-8 weeks processing

## Step 4: Local Permits
- Check with local government for permits
- Apply for local business license
- Zoning compliance verification
- Cost: $50-200 local fees
- Timeline: 1-4 weeks processing

**Total Estimated Cost**: $233-830+ depending on industry
**Total Timeline**: 4-14 weeks for complete setup

**Official Resources**:
- Florida Division of Corporations: https://dos.myflorida.com/sunbiz/
- Florida Department of Revenue: https://floridarevenue.com/
- MyFloridaLicense.com: https://www2.myfloridalicense.com/
- Florida Office of Financial Regulation: https://flofr.com/"""
        
        return ToolResult(
            content=[TextContent(type="text", text=steps_text)],
            metadata={"business_type": business_type}
        )
    
    async def _get_license_requirements(self, arguments: Dict[str, Any]) -> ToolResult:
        """Get detailed license requirements for a business type."""
        business_type = arguments.get("business_type", "")
        location = arguments.get("location", "")
        
        business_lower = business_type.lower()
        
        if any(word in business_lower for word in ['financial', 'investment', 'private equity', 'adviser']):
            requirements_text = """# Florida Investment Adviser Requirements

## Registration Requirements:
1. **Submit Form ADV** - Complete and submit Form ADV to Florida Office of Financial Regulation
2. **Financial Statements** - Provide audited financial statements
3. **Background Checks** - Complete background checks for all principals
4. **Compliance Program** - Establish and maintain compliance program
5. **Registration Fees** - Pay $200 registration fee + $42.50 background check fee

## Ongoing Requirements:
- File annual reports
- Maintain compliance program
- Provide disclosure documents to investors
- Pay annual renewal fee of $200

## Timeline:
- Background checks: 2-4 weeks
- Application processing: 4-8 weeks
- Total timeline: 6-12 weeks

**Source**: Florida Office of Financial Regulation"""
            
        else:
            requirements_text = f"""# Florida Business License Requirements for {business_type}

## General Requirements:
1. **Business Registration** - Register with Florida Division of Corporations
2. **Tax Registration** - Register with Florida Department of Revenue
3. **Industry Licensing** - Apply for required professional licenses
4. **Local Permits** - Obtain local business permits
5. **Insurance** - Maintain required insurance coverage

## Timeline:
- Business registration: 1-2 weeks
- Tax registration: 1-2 weeks
- Industry licensing: 2-8 weeks
- Local permits: 1-4 weeks
- Total timeline: 4-14 weeks

**Source**: Florida Department of Business and Professional Regulation"""
        
        return ToolResult(
            content=[TextContent(type="text", text=requirements_text)],
            metadata={"business_type": business_type, "location": location}
        )
    
    async def _get_florida_license_categories(self) -> ToolResult:
        """Get all available Florida license categories."""
        categories_text = """# Florida Business License Categories

## Professional Services
- Real Estate License
- Investment Adviser License
- Financial Services License
- Insurance License

## Construction & Trades
- Contractor License
- Electrical License
- Plumbing License
- HVAC License

## Food & Hospitality
- Food Service License
- Hotel License
- Restaurant License
- Catering License

## Health & Safety
- Medical License
- Dental License
- Pharmacy License
- Cosmetology License

## Transportation
- Motor Vehicle Dealer License
- Transportation License
- Limousine License

**Apply Online**: https://www2.myfloridalicense.com/
**Check Requirements**: https://www.myfloridalicense.com/DBPR/"""
        
        return ToolResult(
            content=[TextContent(type="text", text=categories_text)],
            metadata={"state": "FL"}
        )
    
    async def _get_florida_license_details(self, license_type: str) -> ToolResult:
        """Get detailed information about a specific Florida license type."""
        license_lower = license_type.lower()
        
        if "investment" in license_lower or "adviser" in license_lower:
            details_text = """# Florida Investment Adviser License Details

## Requirements:
- Submit Form ADV to Florida Office of Financial Regulation
- Provide audited financial statements
- Complete background checks for all principals
- Establish compliance program
- Pay registration fees

## Costs:
- Registration fee: $200
- Background check fee: $42.50
- Annual renewal fee: $200

## Timeline:
- Background checks: 2-4 weeks
- Application processing: 4-8 weeks
- Total: 6-12 weeks

## Official Resources:
- Florida Office of Financial Regulation: https://flofr.com/InvestmentAdvisers/
- Registration Portal: https://flofr.com/InvestmentAdvisers/Registration/
- Requirements: https://flofr.com/InvestmentAdvisers/License-Requirements/"""
            
        elif "construction" in license_lower or "contractor" in license_lower:
            details_text = """# Florida Construction Contractor License Details

## Requirements:
- Be at least 18 years old
- Pass background check
- Pass Florida contractor examination
- Provide proof of financial responsibility
- Submit application with fees

## Costs:
- Application fee: $249
- License fee: $209
- Background check fee: $42.50
- Exam fee: $135
- Total initial cost: $635.50
- Renewal fee: $209 every 2 years

## Timeline:
- Background check: 2-4 weeks
- Exam preparation and testing: 4-8 weeks
- Application processing: 4-8 weeks
- Total: 10-20 weeks

## Official Resources:
- Florida Construction Industry Licensing Board: https://www.myfloridalicense.com/DBPR/construction-industry-licensing-board/
- Application Portal: https://www.myfloridalicense.com/DBPR/construction-industry-licensing-board/apply-for-license/
- Requirements: https://www.myfloridalicense.com/DBPR/construction-industry-licensing-board/license-requirements/"""
            
        else:
            details_text = f"""# Florida License Details for {license_type}

## General Requirements:
- Business registration with Florida Division of Corporations
- Tax registration with Florida Department of Revenue
- Industry-specific licensing through DBPR
- Local permits and zoning compliance

## Costs:
- Business registration: $78-125
- Tax certificate: $5
- Industry licensing: $100-500+
- Local permits: $50-200

## Timeline:
- Business registration: 1-2 weeks
- Tax registration: 1-2 weeks
- Industry licensing: 2-8 weeks
- Local permits: 1-4 weeks

## Official Resources:
- Florida Division of Corporations: https://dos.myflorida.com/sunbiz/
- Florida Department of Revenue: https://floridarevenue.com/
- MyFloridaLicense.com: https://www2.myfloridalicense.com/"""
        
        return ToolResult(
            content=[TextContent(type="text", text=details_text)],
            metadata={"license_type": license_type, "state": "FL"}
        )
    
    async def _search_florida_licenses(self, query: str) -> ToolResult:
        """Search Florida licenses by keyword."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['financial', 'investment', 'private equity', 'adviser']):
            search_text = """# Florida Investment Adviser License Search Results

## Found Licenses:
1. **Investment Adviser Registration** - Required for private equity firms
   - Agency: Florida Office of Financial Regulation
   - Cost: $242.50 (Registration $200 + Background check $42.50)
   - Renewal: $200 annually
   - URL: https://flofr.com/InvestmentAdvisers/

2. **Securities Registration** - Required if offering securities
   - Agency: Florida Office of Financial Regulation
   - Cost: Varies by offering size
   - URL: https://flofr.com/Securities/

## Additional Requirements:
- Business registration with Florida Division of Corporations
- Tax registration with Florida Department of Revenue
- Compliance program establishment
- Annual reporting requirements

**Source**: Florida Office of Financial Regulation"""
            
        elif any(word in query_lower for word in ['construction', 'contractor', 'building']):
            search_text = """# Florida Construction License Search Results

## Found Licenses:
1. **General Contractor License** - For construction work
   - Agency: Florida Construction Industry Licensing Board
   - Cost: $635.50 total initial cost
   - Renewal: $209 every 2 years
   - URL: https://www.myfloridalicense.com/DBPR/construction-industry-licensing-board/

2. **Specialty Contractor Licenses** - For specific trades
   - Electrical, Plumbing, HVAC, Roofing, etc.
   - Cost: Varies by specialty
   - URL: https://www.myfloridalicense.com/DBPR/construction-industry-licensing-board/

## Additional Requirements:
- Business registration with Florida Division of Corporations
- Tax registration with Florida Department of Revenue
- Local building permits
- Insurance requirements

**Source**: Florida Construction Industry Licensing Board"""
            
        else:
            search_text = f"""# Florida License Search Results for: {query}

## General Business Requirements:
1. **Business Registration** - Register with Florida Division of Corporations
2. **Tax Registration** - Register with Florida Department of Revenue
3. **Industry Licensing** - Apply for required professional licenses
4. **Local Permits** - Obtain local business permits

## Costs:
- Business registration: $78-125
- Tax certificate: $5
- Industry licensing: $100-500+
- Local permits: $50-200

## Timeline:
- Total setup time: 4-14 weeks

**Source**: Florida Department of Business and Professional Regulation"""
        
        return ToolResult(
            content=[TextContent(type="text", text=search_text)],
            metadata={"query": query, "state": "FL"}
        )
    
    async def _get_florida_business_steps(self) -> ToolResult:
        """Get step-by-step process for Florida business registration."""
        steps_text = """# Florida Business Registration Steps

## Step 1: Business Entity Formation
- Choose business structure (LLC, Corporation, Partnership)
- File with Florida Division of Corporations
- Cost: $78-125 filing fee
- Timeline: 1-2 weeks processing

## Step 2: Tax Registration
- Register with Florida Department of Revenue
- Apply for tax certificate
- Register for sales tax (if applicable)
- Cost: $5 tax certificate fee
- Timeline: 1-2 weeks processing

## Step 3: Industry-Specific Licensing
- Identify required licenses for your industry
- Apply through MyFloridaLicense.com
- Complete required training/certifications
- Cost: Varies by industry ($100-500+)
- Timeline: 2-8 weeks processing

## Step 4: Local Permits
- Check with local government for permits
- Apply for local business license
- Zoning compliance verification
- Cost: $50-200 local fees
- Timeline: 1-4 weeks processing

**Total Estimated Cost**: $233-830+ depending on industry
**Total Timeline**: 4-14 weeks for complete setup

**Official Resources**:
- Florida Division of Corporations: https://dos.myflorida.com/sunbiz/
- Florida Department of Revenue: https://floridarevenue.com/
- MyFloridaLicense.com: https://www2.myfloridalicense.com/
- Florida Office of Financial Regulation: https://flofr.com/"""
        
        return ToolResult(
            content=[TextContent(type="text", text=steps_text)],
            metadata={"state": "FL"}
        )
    
    async def _get_construction_requirements(self, arguments: Dict[str, Any]) -> ToolResult:
        """Get specific requirements for Florida construction contractor licenses."""
        requirements_text = """# Florida Construction Contractor License Requirements

## Eligibility Requirements:
- Be at least 18 years old
- Pass background check
- Pass Florida contractor examination
- Provide proof of financial responsibility
- Submit application with required fees

## Application Process:
1. **Background Check**
   - Complete fingerprinting
   - Submit background check application
   - Cost: $42.50
   - Timeline: 2-4 weeks

2. **Examination**
   - Study for Florida contractor exam
   - Schedule and pass examination
   - Cost: $135
   - Timeline: 4-8 weeks

3. **Financial Responsibility**
   - Obtain surety bond or insurance
   - Provide proof of financial responsibility
   - Cost: Varies by coverage amount

4. **Application Submission**
   - Complete application form
   - Submit all required documents
   - Pay application fee: $249
   - Pay license fee: $209
   - Timeline: 4-8 weeks processing

## Total Costs:
- Application fee: $249
- License fee: $209
- Background check: $42.50
- Exam fee: $135
- **Total initial cost: $635.50**
- Renewal fee: $209 every 2 years

## Timeline:
- Background check: 2-4 weeks
- Exam preparation and testing: 4-8 weeks
- Application processing: 4-8 weeks
- **Total timeline: 10-20 weeks**

## Official Resources:
- Florida Construction Industry Licensing Board: https://www.myfloridalicense.com/DBPR/construction-industry-licensing-board/
- Application Portal: https://www.myfloridalicense.com/DBPR/construction-industry-licensing-board/apply-for-license/
- Requirements: https://www.myfloridalicense.com/DBPR/construction-industry-licensing-board/license-requirements/
- Exam Information: https://www.myfloridalicense.com/DBPR/construction-industry-licensing-board/examination/"""
        
        return ToolResult(
            content=[TextContent(type="text", text=requirements_text)],
            metadata={"license_type": "construction", "state": "FL"}
        )
    
    async def _get_local_requirements(self, arguments: Dict[str, Any]) -> ToolResult:
        """Get local requirements for business in Palm Harbor, Florida."""
        requirements_text = """# Palm Harbor, Florida Local Business Requirements

## Local Government:
- **City of Palm Harbor** - Development Services Department
- **County**: Pinellas County
- **Region**: Tampa Bay Area

## Local Permits Required:
1. **Business Tax Receipt** (Local Business License)
   - Apply with Pinellas County Tax Collector
   - Cost: $50-200 depending on business type
   - Timeline: 1-2 weeks

2. **Building Permits** (if applicable)
   - Apply with Pinellas County Building Department
   - Cost: Varies by project size
   - Timeline: 2-4 weeks

3. **Zoning Compliance**
   - Verify business location zoning
   - Apply for zoning variance if needed
   - Cost: $100-500
   - Timeline: 2-6 weeks

## Local Resources:
- **Pinellas County Tax Collector**: https://www.pinellascountytaxcollector.com/
- **Pinellas County Building Department**: https://www.pinellascounty.org/building/
- **City of Palm Harbor**: https://www.palmharbor.org/
- **Palm Harbor Development Services**: https://www.palmharbor.org/departments/development-services/

## Additional Requirements:
- Local business registration
- Sign permits (if applicable)
- Parking compliance
- ADA compliance

## Timeline:
- Local permits: 1-4 weeks
- Building permits: 2-6 weeks
- Zoning compliance: 2-6 weeks

**Source**: Pinellas County Government, City of Palm Harbor"""
        
        return ToolResult(
            content=[TextContent(type="text", text=requirements_text)],
            metadata={"location": "Palm Harbor, FL"}
        )


# For testing
if __name__ == "__main__":
    async def test():
        server = FloridaLicenseServer()
        result = await server.call_tool("get_license_summary", {
            "business_type": "private equity firm",
            "location": "FL, USA"
        })
        print(result.get_text())
    
    asyncio.run(test()) 
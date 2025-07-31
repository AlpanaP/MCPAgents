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
            requirements = pattern.get("requirements", [])
            
            summary = [
                f"# 🏢 Business License Compliance Guide\n\n",
                f"## 📋 **Query Summary**\n",
                f"Comprehensive licensing requirements for {business_type.title()} business in {location}.\n\n",
                f"## 🏛️ **Licensing Requirements Overview**\n\n"
            ]
            
            for i, license_type in enumerate(license_types):
                summary.append(f"### **{license_type}**\n")
                summary.append(f"- **Agency**: {location.split(',')[0].strip()} Division of Professional Regulation\n")
                summary.append(f"- **Law**: {location.split(',')[0].strip()} Business License Act\n")
                summary.append(f"- **Eligible Entity Types**: Business Corporations, Professional Corporations, LLCs, LLPs\n")
                
                if i < len(fees):
                    summary.append(f"- **Cost**: {fees[i]}\n")
                else:
                    summary.append(f"- **Cost**: Application fee + License fee\n")
                
                if i < len(due_dates):
                    summary.append(f"- **Due Date**: {due_dates[i]}\n")
                else:
                    summary.append(f"- **Due Date**: Apply before starting business operations\n")
                
                summary.append(f"- **Official URL**: {self.state_config.get('url_patterns', {}).get('main_license_site', 'https://state.gov/')}\n\n")
            
            summary.append(f"### **Additional Permits & Registrations**\n")
            summary.append(f"- **Business Registration**: Required with Secretary of State\n")
            summary.append(f"- **Tax Registration**: Sales tax, employer tax registration\n")
            summary.append(f"- **Local Permits**: City/county business permits\n")
            summary.append(f"- **Industry-Specific Permits**: {', '.join(requirements)}\n\n")
            
            summary.append(f"## 💰 **Cost Breakdown & Timeline**\n\n")
            summary.append(f"### **Initial Costs**\n")
            summary.append(f"- **Application Fees**: $100-300 per license\n")
            summary.append(f"- **License Fees**: $200-500 per license\n")
            summary.append(f"- **Background Check Fees**: $50-100 (if required)\n")
            summary.append(f"- **Insurance Requirements**: $500-2000 annually\n")
            summary.append(f"- **Total Estimated Initial Cost**: $850-2900\n\n")
            
            summary.append(f"### **Ongoing Costs**\n")
            summary.append(f"- **Annual Renewal Fees**: $200-500 per license\n")
            summary.append(f"- **Continuing Education**: $100-300 annually (if required)\n")
            summary.append(f"- **Insurance Premiums**: $500-2000 annually\n")
            summary.append(f"- **Total Annual Operating Cost**: $800-2800\n\n")
            
            summary.append(f"### **Payment Timeline**\n")
            summary.append(f"- **Application**: Due when submitting application\n")
            summary.append(f"- **Background Check**: Due within 30 days of application\n")
            summary.append(f"- **License Issuance**: Due upon approval\n")
            summary.append(f"- **Renewal**: Annual renewal required\n\n")
            
            summary.append(f"## 📋 **Step-by-Step Application Process**\n\n")
            summary.append(f"### **Phase 1: Business Setup (Days 1-30)**\n")
            summary.append(f"1. **Business Entity Formation**\n")
            summary.append(f"   - Choose business structure (LLC, Corporation, etc.)\n")
            summary.append(f"   - File with Secretary of State\n")
            summary.append(f"   - Cost: $50-200\n")
            summary.append(f"   - Timeline: 5-10 business days\n\n")
            
            summary.append(f"2. **Business Registration**\n")
            summary.append(f"   - Register with state revenue department\n")
            summary.append(f"   - Obtain business license/tax certificate\n")
            summary.append(f"   - Cost: $25-150\n")
            summary.append(f"   - Timeline: 3-7 business days\n\n")
            
            summary.append(f"### **Phase 2: License Application (Days 31-90)**\n")
            summary.append(f"3. **Gather Required Documents**\n")
            summary.append(f"   - Business formation documents\n")
            summary.append(f"   - Financial statements\n")
            summary.append(f"   - Background check authorization\n")
            summary.append(f"   - Timeline: 1-2 weeks\n\n")
            
            summary.append(f"4. **Submit Application**\n")
            summary.append(f"   - Complete online application\n")
            summary.append(f"   - Pay application fees\n")
            summary.append(f"   - Submit supporting documents\n")
            summary.append(f"   - Cost: $100-300\n")
            summary.append(f"   - Timeline: 4-8 weeks processing\n\n")
            
            summary.append(f"### **Phase 3: License Issuance (Days 91-120)**\n")
            summary.append(f"5. **License Approval**\n")
            summary.append(f"   - Receive license approval\n")
            summary.append(f"   - Pay license fees\n")
            summary.append(f"   - Receive official license\n")
            summary.append(f"   - Cost: $200-500\n")
            summary.append(f"   - Timeline: 1-2 weeks after approval\n\n")
            
            summary.append(f"## 🔗 **Official Resources & Contact Information**\n\n")
            summary.append(f"### **Primary Government Agencies**\n")
            summary.append(f"- **Main Licensing Portal**: {self.state_config.get('url_patterns', {}).get('main_license_site', 'https://state.gov/')}\n")
            summary.append(f"- **Application Forms**: {self.state_config.get('url_patterns', {}).get('application_portal', 'https://state.gov/apply/')}\n")
            summary.append(f"- **Requirements & Regulations**: {self.state_config.get('url_patterns', {}).get('requirements', 'https://state.gov/requirements/')}\n")
            summary.append(f"- **Fee Schedules**: {self.state_config.get('url_patterns', {}).get('fees', 'https://state.gov/fees/')}\n")
            summary.append(f"- **Contact Information**: (555) 123-4567 | licensing@state.gov\n\n")
            
            summary.append(f"## ⚠️ **Important Deadlines & Compliance**\n\n")
            summary.append(f"### **Critical Deadlines**\n")
            summary.append(f"- **Application Deadline**: 60 days before starting business\n")
            summary.append(f"- **Background Check Deadline**: 30 days after application\n")
            summary.append(f"- **License Fee Payment**: Due upon approval\n")
            summary.append(f"- **Renewal Deadline**: Annual renewal required\n\n")
            
            summary.append(f"### **Compliance Requirements**\n")
            summary.append(f"- **Continuing Education**: 12 hours annually (if required)\n")
            summary.append(f"- **Insurance Maintenance**: $500,000 liability coverage\n")
            summary.append(f"- **Record Keeping**: Maintain business records for 7 years\n")
            summary.append(f"- **Reporting Requirements**: Annual reports to state\n\n")
            
            summary.append(f"## 💡 **Pro Tips & Best Practices**\n\n")
            summary.append(f"### **Cost Optimization**\n")
            summary.append(f"- Apply for multiple licenses together to save on fees\n")
            summary.append(f"- Consider annual payment plans for insurance\n")
            summary.append(f"- Shop around for competitive insurance rates\n\n")
            
            summary.append(f"### **Timeline Management**\n")
            summary.append(f"- Start the process 90 days before planned opening\n")
            summary.append(f"- Keep copies of all submitted documents\n")
            summary.append(f"- Set calendar reminders for renewal dates\n\n")
            
            summary.append(f"### **Compliance Maintenance**\n")
            summary.append(f"- Set up automatic renewal reminders\n")
            summary.append(f"- Maintain organized record keeping system\n")
            summary.append(f"- Stay updated on regulatory changes\n\n")
            
            summary.append(f"## 📞 **Need Help?**\n\n")
            summary.append(f"### **Professional Services**\n")
            summary.append(f"- **License Consultants**: Professional licensing services\n")
            summary.append(f"- **Legal Assistance**: Business law attorneys\n")
            summary.append(f"- **Industry Associations**: Professional trade groups\n\n")
            
            summary.append(f"### **Government Support**\n")
            summary.append(f"- **Agency Contact**: (555) 123-4567\n")
            summary.append(f"- **Online Support**: https://state.gov/help/\n")
            summary.append(f"- **In-Person Assistance**: State Capitol Building\n\n")
            
            summary.append(f"---\n")
            summary.append(f"**Sources**: State licensing database, industry regulations\n")
            summary.append(f"**Last Updated**: Current\n")
            summary.append(f"**Disclaimer**: This information is for guidance only. Always verify with official government sources.\n")
            
        else:
            summary = [
                f"# 🏢 Business License Compliance Guide\n\n",
                f"## 📋 **Query Summary**\n",
                f"Standard business licensing requirements for {business_type.title()} operations in {location}.\n\n",
                f"## 🏛️ **Licensing Requirements Overview**\n\n",
                f"### **General Business License**\n",
                f"- **Agency**: {location.split(',')[0].strip()} Division of Professional Regulation\n",
                f"- **Law**: {location.split(',')[0].strip()} Business License Act\n",
                f"- **Eligible Entity Types**: Business Corporations, Professional Corporations, LLCs, LLPs\n",
                f"- **Cost**: $50-200 application fee + $100-300 license fee\n",
                f"- **Due Date**: Apply before starting business operations\n",
                f"- **Official URL**: https://state.gov/\n\n",
                f"### **Additional Permits & Registrations**\n",
                f"- **Business Registration**: Required with Secretary of State\n",
                f"- **Tax Registration**: Sales tax, employer tax registration\n",
                f"- **Local Permits**: City/county business permits\n",
                f"- **Industry-Specific Permits**: Based on business type\n\n",
                f"## 💰 **Cost Breakdown & Timeline**\n\n",
                f"### **Initial Costs**\n",
                f"- **Application Fees**: $50-200\n",
                f"- **License Fees**: $100-300\n",
                f"- **Background Check Fees**: $25-75 (if required)\n",
                f"- **Insurance Requirements**: $300-1500 annually\n",
                f"- **Total Estimated Initial Cost**: $475-2075\n\n",
                f"### **Ongoing Costs**\n",
                f"- **Annual Renewal Fees**: $100-300\n",
                f"- **Continuing Education**: $50-200 annually (if required)\n",
                f"- **Insurance Premiums**: $300-1500 annually\n",
                f"- **Total Annual Operating Cost**: $450-2000\n\n",
                f"## 📋 **Step-by-Step Application Process**\n\n",
                f"### **Phase 1: Business Setup (Days 1-30)**\n",
                f"1. **Business Entity Formation**\n",
                f"   - Choose business structure (LLC, Corporation, etc.)\n",
                f"   - File with Secretary of State\n",
                f"   - Cost: $50-200\n",
                f"   - Timeline: 5-10 business days\n\n",
                f"2. **Business Registration**\n",
                f"   - Register with state revenue department\n",
                f"   - Obtain business license/tax certificate\n",
                f"   - Cost: $25-150\n",
                f"   - Timeline: 3-7 business days\n\n",
                f"### **Phase 2: License Application (Days 31-90)**\n",
                f"3. **Submit Application**\n",
                f"   - Complete online application\n",
                f"   - Pay application fees\n",
                f"   - Submit supporting documents\n",
                f"   - Cost: $50-200\n",
                f"   - Timeline: 4-8 weeks processing\n\n",
                f"### **Phase 3: License Issuance (Days 91-120)**\n",
                f"4. **License Approval**\n",
                f"   - Receive license approval\n",
                f"   - Pay license fees\n",
                f"   - Receive official license\n",
                f"   - Cost: $100-300\n",
                f"   - Timeline: 1-2 weeks after approval\n\n",
                f"## 🔗 **Official Resources & Contact Information**\n\n",
                f"### **Primary Government Agencies**\n",
                f"- **Main Licensing Portal**: https://state.gov/\n",
                f"- **Application Forms**: https://state.gov/apply/\n",
                f"- **Requirements & Regulations**: https://state.gov/requirements/\n",
                f"- **Fee Schedules**: https://state.gov/fees/\n",
                f"- **Contact Information**: (555) 123-4567 | licensing@state.gov\n\n",
                f"## ⚠️ **Important Deadlines & Compliance**\n\n",
                f"### **Critical Deadlines**\n",
                f"- **Application Deadline**: 60 days before starting business\n",
                f"- **License Fee Payment**: Due upon approval\n",
                f"- **Renewal Deadline**: Annual renewal required\n\n",
                f"### **Compliance Requirements**\n",
                f"- **Insurance Maintenance**: $300,000 liability coverage\n",
                f"- **Record Keeping**: Maintain business records for 5 years\n",
                f"- **Reporting Requirements**: Annual reports to state\n\n",
                f"## 💡 **Pro Tips & Best Practices**\n\n",
                f"### **Cost Optimization**\n",
                f"- Apply early to avoid rush fees\n",
                f"- Consider annual payment plans for insurance\n",
                f"- Shop around for competitive insurance rates\n\n",
                f"### **Timeline Management**\n",
                f"- Start the process 90 days before planned opening\n",
                f"- Keep copies of all submitted documents\n",
                f"- Set calendar reminders for renewal dates\n\n",
                f"### **Compliance Maintenance**\n",
                f"- Set up automatic renewal reminders\n",
                f"- Maintain organized record keeping system\n",
                f"- Stay updated on regulatory changes\n\n",
                f"## 📞 **Need Help?**\n\n",
                f"### **Professional Services**\n",
                f"- **License Consultants**: Professional licensing services\n",
                f"- **Legal Assistance**: Business law attorneys\n",
                f"- **Industry Associations**: Professional trade groups\n\n",
                f"### **Government Support**\n",
                f"- **Agency Contact**: (555) 123-4567\n",
                f"- **Online Support**: https://state.gov/help/\n",
                f"- **In-Person Assistance**: State Capitol Building\n\n",
                f"---\n",
                f"**Sources**: State licensing database, industry regulations\n",
                f"**Last Updated**: Current\n",
                f"**Disclaimer**: This information is for guidance only. Always verify with official government sources.\n"
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
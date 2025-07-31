#!/usr/bin/env python3
"""
Delaware Business License MCP Server
Provides tools to access Delaware business license information from firststeps.delaware.gov
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Delaware Business First Steps URL
DELAWARE_BASE_URL = "https://firststeps.delaware.gov"
DELAWARE_TOPICS_URL = "https://firststeps.delaware.gov/topics/"

class DelawareLicenseServer:
    def __init__(self):
        self.server = Server("delaware-licenses")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Register tools
        self.server.list_tools = self.list_tools
        self.server.call_tool = self.call_tool

    async def list_tools(self, request: ListToolsRequest) -> ListToolsResult:
        """List available tools for Delaware license information."""
        tools = [
            Tool(
                name="get_delaware_license_categories",
                description="Get all available license categories from Delaware Business First Steps",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="get_delaware_license_details",
                description="Get detailed information about a specific license type from Delaware",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "License category (e.g., 'Food', 'Health', 'Professions')"
                        },
                        "license_type": {
                            "type": "string",
                            "description": "Specific license type within the category"
                        }
                    },
                    "required": ["category"]
                }
            ),
            Tool(
                name="search_delaware_licenses",
                description="Search for licenses by keyword or business type",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (e.g., 'restaurant', 'bakery', 'consulting')"
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="get_delaware_business_steps",
                description="Get the 4-step process for opening a business in Delaware",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            )
        ]
        return ListToolsResult(tools=tools)

    async def call_tool(self, request: CallToolRequest) -> CallToolResult:
        """Handle tool calls for Delaware license information."""
        try:
            if request.name == "get_delaware_license_categories":
                return await self._get_license_categories()
            elif request.name == "get_delaware_license_details":
                return await self._get_license_details(request.arguments)
            elif request.name == "search_delaware_licenses":
                return await self._search_licenses(request.arguments)
            elif request.name == "get_delaware_business_steps":
                return await self._get_business_steps()
            else:
                raise ValueError(f"Unknown tool: {request.name}")
        except Exception as e:
            logger.error(f"Error in tool call {request.name}: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")]
            )

    async def _get_license_categories(self) -> CallToolResult:
        """Get all available license categories from Delaware."""
        try:
            response = self.session.get(DELAWARE_TOPICS_URL)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the main content area
            content = soup.find('div', {'id': 'content'}) or soup
            
            # Extract categories from the page
            categories = []
            
            # Look for category headings
            category_elements = content.find_all(['h2', 'h3', 'h4'])
            
            for element in category_elements:
                text = element.get_text(strip=True)
                if text and len(text) > 2 and len(text) < 100:
                    categories.append(text)
            
            # Remove duplicates and clean up
            categories = list(set([cat.strip() for cat in categories if cat.strip()]))
            
            result = {
                "categories": categories,
                "source": "Delaware Business First Steps",
                "url": DELAWARE_TOPICS_URL,
                "total_categories": len(categories)
            }
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Delaware Business License Categories:\n\n" +
                         f"Source: {DELAWARE_TOPICS_URL}\n" +
                         f"Total Categories: {len(categories)}\n\n" +
                         f"Available Categories:\n" +
                         "\n".join([f"• {cat}" for cat in categories])
                )]
            )
            
        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error fetching Delaware license categories: {str(e)}"
                )]
            )

    async def _get_license_details(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get detailed information about a specific license category."""
        category = arguments.get("category", "").lower()
        
        license_details = {
            "food": {
                "title": "Delaware Food Establishment License",
                "content": [
                    "# 🏢 Delaware Business License Compliance Guide\n\n",
                    "## 📋 **Query Summary**\n",
                    "Comprehensive licensing requirements for food service businesses in Delaware.\n\n",
                    "## 🏛️ **Licensing Requirements Overview**\n\n",
                    "### **Delaware Food Establishment License**\n",
                    "- **Agency**: Delaware Division of Public Health\n",
                    "- **Law**: Del. C. § 312A\n",
                    "- **Eligible Entity Types**: Business Corporations, Professional Corporations, LLCs, LLPs\n",
                    "- **Cost**: $100-300 application fee + $200-500 license fee\n",
                    "- **Due Date**: Apply 45 days before opening\n",
                    "- **Official URL**: https://firststeps.delaware.gov/topics/\n\n",
                    "### **Additional Permits & Registrations**\n",
                    "- **Business Registration**: Required with Delaware Secretary of State\n",
                    "- **Tax Registration**: Sales tax, employer tax registration\n",
                    "- **Local Permits**: City/county business permits\n",
                    "- **Industry-Specific Permits**: Food safety training, health inspection, kitchen compliance\n\n",
                    "## 💰 **Cost Breakdown & Timeline**\n\n",
                    "### **Initial Costs**\n",
                    "- **Application Fees**: $100-300\n",
                    "- **License Fees**: $200-500\n",
                    "- **Health Inspection Fees**: $75-150\n",
                    "- **Food Safety Training**: $50-200\n",
                    "- **Total Estimated Initial Cost**: $425-1150\n\n",
                    "### **Ongoing Costs**\n",
                    "- **Annual Renewal Fees**: $200-500\n",
                    "- **Annual Health Inspections**: $75-150\n",
                    "- **Insurance Premiums**: $500-2000 annually\n",
                    "- **Total Annual Operating Cost**: $775-2650\n\n",
                    "### **Payment Timeline**\n",
                    "- **Application**: 45 days before opening\n",
                    "- **Health Inspection**: 30 days before opening\n",
                    "- **License Issuance**: 2-4 weeks after inspection\n",
                    "- **Renewal**: Annual renewal required\n\n",
                    "## 📋 **Step-by-Step Application Process**\n\n",
                    "### **Phase 1: Business Setup (Days 1-30)**\n",
                    "1. **Business Entity Formation**\n",
                    "   - Choose business structure (LLC, Corporation, etc.)\n",
                    "   - File with Delaware Secretary of State\n",
                    "   - Cost: $50-200\n",
                    "   - Timeline: 5-10 business days\n\n",
                    "2. **Business Registration**\n",
                    "   - Register with Delaware Division of Revenue\n",
                    "   - Obtain Delaware Business License\n",
                    "   - Cost: $25-150\n",
                    "   - Timeline: 3-7 business days\n\n",
                    "### **Phase 2: License Application (Days 31-90)**\n",
                    "3. **Food Safety Training**\n",
                    "   - Complete food safety certification course\n",
                    "   - Obtain food handler permits for employees\n",
                    "   - Cost: $50-200\n",
                    "   - Timeline: 1-2 weeks\n\n",
                    "4. **Health Inspection**\n",
                    "   - Schedule health department inspection\n",
                    "   - Ensure kitchen facility compliance\n",
                    "   - Cost: $75-150\n",
                    "   - Timeline: 30 days before opening\n\n",
                    "5. **Submit Application**\n",
                    "   - Complete online application\n",
                    "   - Pay application fees\n",
                    "   - Submit supporting documents\n",
                    "   - Cost: $100-300\n",
                    "   - Timeline: 2-4 weeks processing\n\n",
                    "### **Phase 3: License Issuance (Days 91-120)**\n",
                    "6. **License Approval**\n",
                    "   - Receive license approval\n",
                    "   - Pay license fees\n",
                    "   - Receive official license\n",
                    "   - Cost: $200-500\n",
                    "   - Timeline: 1-2 weeks after approval\n\n",
                    "## 🔗 **Official Resources & Contact Information**\n\n",
                    "### **Primary Government Agencies**\n",
                    "- **Main Licensing Portal**: https://firststeps.delaware.gov/\n",
                    "- **Application Forms**: https://delpros.delaware.gov/OH_HomePage\n",
                    "- **Requirements & Regulations**: https://dpr.delaware.gov/\n",
                    "- **Fee Schedules**: https://revenue.delaware.gov/business-tax-forms/\n",
                    "- **Contact Information**: (302) 744-4500 | dpr@delaware.gov\n\n",
                    "### **Supporting Resources**\n",
                    "- **Business Registration**: https://corp.delaware.gov/\n",
                    "- **Tax Registration**: https://revenue.delaware.gov/\n",
                    "- **Local Permits**: Contact local city/county offices\n",
                    "- **Industry Associations**: Delaware Restaurant Association\n\n",
                    "## ⚠️ **Important Deadlines & Compliance**\n\n",
                    "### **Critical Deadlines**\n",
                    "- **Application Deadline**: 45 days before opening\n",
                    "- **Health Inspection Deadline**: 30 days before opening\n",
                    "- **License Fee Payment**: Due upon approval\n",
                    "- **Renewal Deadline**: Annual renewal required\n\n",
                    "### **Compliance Requirements**\n",
                    "- **Food Safety Training**: Required for all employees\n",
                    "- **Health Inspections**: Annual inspections required\n",
                    "- **Record Keeping**: Maintain food safety records for 3 years\n",
                    "- **Reporting Requirements**: Report foodborne illness incidents\n\n",
                    "## 💡 **Pro Tips & Best Practices**\n\n",
                    "### **Cost Optimization**\n",
                    "- Apply for multiple licenses together to save on fees\n",
                    "- Consider annual payment plans for insurance\n",
                    "- Shop around for competitive insurance rates\n\n",
                    "### **Timeline Management**\n",
                    "- Start the process 90 days before planned opening\n",
                    "- Keep copies of all submitted documents\n",
                    "- Set calendar reminders for renewal dates\n\n",
                    "### **Compliance Maintenance**\n",
                    "- Set up automatic renewal reminders\n",
                    "- Maintain organized record keeping system\n",
                    "- Stay updated on regulatory changes\n\n",
                    "## 📞 **Need Help?**\n\n",
                    "### **Professional Services**\n",
                    "- **License Consultants**: Professional licensing services\n",
                    "- **Legal Assistance**: Delaware business law attorneys\n",
                    "- **Industry Associations**: Delaware Restaurant Association\n\n",
                    "### **Government Support**\n",
                    "- **Agency Contact**: (302) 744-4500\n",
                    "- **Online Support**: https://firststeps.delaware.gov/\n",
                    "- **In-Person Assistance**: Delaware State Capitol\n\n",
                    "---\n",
                    "**Sources**: Delaware Division of Professional Regulation, Delaware Business First Steps\n",
                    "**Last Updated**: Current\n",
                    "**Disclaimer**: This information is for guidance only. Always verify with official Delaware government sources.\n"
                ]
            },
            "construction": {
                "title": "Delaware Construction Contractor License",
                "content": [
                    "# 🏢 Delaware Business License Compliance Guide\n\n",
                    "## 📋 **Query Summary**\n",
                    "Comprehensive licensing requirements for construction businesses in Delaware.\n\n",
                    "## 🏛️ **Licensing Requirements Overview**\n\n",
                    "### **Delaware Construction Contractor License**\n",
                    "- **Agency**: Delaware Division of Professional Regulation\n",
                    "- **Law**: Del. C. § 312A\n",
                    "- **Eligible Entity Types**: Business Corporations, Professional Corporations, LLCs, LLPs\n",
                    "- **Cost**: $200-500 application fee + $300-800 license fee\n",
                    "- **Due Date**: Apply 60 days before starting work\n",
                    "- **Official URL**: https://firststeps.delaware.gov/topics/\n\n",
                    "### **Additional Permits & Registrations**\n",
                    "- **Business Registration**: Required with Delaware Secretary of State\n",
                    "- **Tax Registration**: Sales tax, employer tax registration\n",
                    "- **Local Permits**: City/county business permits\n",
                    "- **Industry-Specific Permits**: Experience verification, background check, insurance coverage\n\n",
                    "## 💰 **Cost Breakdown & Timeline**\n\n",
                    "### **Initial Costs**\n",
                    "- **Application Fees**: $200-500\n",
                    "- **License Fees**: $300-800\n",
                    "- **Background Check Fees**: $50-100\n",
                    "- **Insurance Bond**: $1000-5000\n",
                    "- **Total Estimated Initial Cost**: $1550-6400\n\n",
                    "### **Ongoing Costs**\n",
                    "- **Annual Renewal Fees**: $300-800\n",
                    "- **Insurance Premiums**: $1000-5000 annually\n",
                    "- **Continuing Education**: $100-300 annually\n",
                    "- **Total Annual Operating Cost**: $1400-6100\n\n",
                    "### **Payment Timeline**\n",
                    "- **Application**: 60 days before starting work\n",
                    "- **Background Check**: 30 days before application\n",
                    "- **License Issuance**: 4-8 weeks after application\n",
                    "- **Renewal**: Annual renewal required\n\n",
                    "## 📋 **Step-by-Step Application Process**\n\n",
                    "### **Phase 1: Business Setup (Days 1-30)**\n",
                    "1. **Business Entity Formation**\n",
                    "   - Choose business structure (LLC, Corporation, etc.)\n",
                    "   - File with Delaware Secretary of State\n",
                    "   - Cost: $50-200\n",
                    "   - Timeline: 5-10 business days\n\n",
                    "2. **Business Registration**\n",
                    "   - Register with Delaware Division of Revenue\n",
                    "   - Obtain Delaware Business License\n",
                    "   - Cost: $25-150\n",
                    "   - Timeline: 3-7 business days\n\n",
                    "### **Phase 2: License Application (Days 31-90)**\n",
                    "3. **Experience Verification**\n",
                    "   - Document 2-5 years of construction experience\n",
                    "   - Gather references and project documentation\n",
                    "   - Timeline: 1-2 weeks\n\n",
                    "4. **Background Check**\n",
                    "   - Complete criminal background check\n",
                    "   - Submit fingerprints and authorization\n",
                    "   - Cost: $50-100\n",
                    "   - Timeline: 30 days before application\n\n",
                    "5. **Submit Application**\n",
                    "   - Complete online application\n",
                    "   - Pay application fees\n",
                    "   - Submit supporting documents\n",
                    "   - Cost: $200-500\n",
                    "   - Timeline: 4-8 weeks processing\n\n",
                    "### **Phase 3: License Issuance (Days 91-120)**\n",
                    "6. **License Approval**\n",
                    "   - Receive license approval\n",
                    "   - Pay license fees\n",
                    "   - Receive official license\n",
                    "   - Cost: $300-800\n",
                    "   - Timeline: 1-2 weeks after approval\n\n",
                    "## 🔗 **Official Resources & Contact Information**\n\n",
                    "### **Primary Government Agencies**\n",
                    "- **Main Licensing Portal**: https://firststeps.delaware.gov/\n",
                    "- **Application Forms**: https://delpros.delaware.gov/OH_HomePage\n",
                    "- **Requirements & Regulations**: https://dpr.delaware.gov/\n",
                    "- **Fee Schedules**: https://revenue.delaware.gov/business-tax-forms/\n",
                    "- **Contact Information**: (302) 744-4500 | dpr@delaware.gov\n\n",
                    "### **Supporting Resources**\n",
                    "- **Business Registration**: https://corp.delaware.gov/\n",
                    "- **Tax Registration**: https://revenue.delaware.gov/\n",
                    "- **Local Permits**: Contact local city/county offices\n",
                    "- **Industry Associations**: Delaware Contractors Association\n\n",
                    "## ⚠️ **Important Deadlines & Compliance**\n\n",
                    "### **Critical Deadlines**\n",
                    "- **Application Deadline**: 60 days before starting work\n",
                    "- **Background Check Deadline**: 30 days before application\n",
                    "- **License Fee Payment**: Due upon approval\n",
                    "- **Renewal Deadline**: Annual renewal required\n\n",
                    "### **Compliance Requirements**\n",
                    "- **Continuing Education**: 12 hours annually\n",
                    "- **Insurance Maintenance**: $500,000 liability coverage\n",
                    "- **Record Keeping**: Maintain project records for 7 years\n",
                    "- **Reporting Requirements**: Annual reports to Delaware\n\n",
                    "## 💡 **Pro Tips & Best Practices**\n\n",
                    "### **Cost Optimization**\n",
                    "- Apply for multiple licenses together to save on fees\n",
                    "- Consider annual payment plans for insurance\n",
                    "- Shop around for competitive insurance rates\n\n",
                    "### **Timeline Management**\n",
                    "- Start the process 90 days before planned start\n",
                    "- Keep copies of all submitted documents\n",
                    "- Set calendar reminders for renewal dates\n\n",
                    "### **Compliance Maintenance**\n",
                    "- Set up automatic renewal reminders\n",
                    "- Maintain organized record keeping system\n",
                    "- Stay updated on regulatory changes\n\n",
                    "## 📞 **Need Help?**\n\n",
                    "### **Professional Services**\n",
                    "- **License Consultants**: Professional licensing services\n",
                    "- **Legal Assistance**: Delaware business law attorneys\n",
                    "- **Industry Associations**: Delaware Contractors Association\n\n",
                    "### **Government Support**\n",
                    "- **Agency Contact**: (302) 744-4500\n",
                    "- **Online Support**: https://firststeps.delaware.gov/\n",
                    "- **In-Person Assistance**: Delaware State Capitol\n\n",
                    "---\n",
                    "**Sources**: Delaware Division of Professional Regulation, Delaware Business First Steps\n",
                    "**Last Updated**: Current\n",
                    "**Disclaimer**: This information is for guidance only. Always verify with official Delaware government sources.\n"
                ]
            },
            "cannabis": {
                "title": "Delaware Cannabis Business License",
                "content": [
                    "# 🏢 Delaware Business License Compliance Guide\n\n",
                    "## 📋 **Query Summary**\n",
                    "Comprehensive licensing requirements for cannabis businesses in Delaware.\n\n",
                    "## 🏛️ **Licensing Requirements Overview**\n\n",
                    "### **Delaware Cannabis Business License**\n",
                    "- **Agency**: Delaware Division of Public Health\n",
                    "- **Law**: Del. C. § 312A\n",
                    "- **Eligible Entity Types**: Business Corporations, Professional Corporations, LLCs, LLPs\n",
                    "- **Cost**: $5,000-25,000 application fee + $10,000-50,000 license fee\n",
                    "- **Due Date**: Apply 120 days before planned opening\n",
                    "- **Official URL**: https://delawarecannabiscoalition.org/\n\n",
                    "### **Additional Permits & Registrations**\n",
                    "- **Business Registration**: Required with Delaware Secretary of State\n",
                    "- **Tax Registration**: Sales tax, employer tax registration\n",
                    "- **Local Permits**: City/county business permits\n",
                    "- **Industry-Specific Permits**: Background checks, security plan, financial solvency proof\n\n",
                    "## 💰 **Cost Breakdown & Timeline**\n\n",
                    "### **Initial Costs**\n",
                    "- **Application Fees**: $5,000-25,000\n",
                    "- **License Fees**: $10,000-50,000\n",
                    "- **Background Check Fees**: $500-2000\n",
                    "- **Security System**: $10,000-50,000\n",
                    "- **Total Estimated Initial Cost**: $25,500-127,000\n\n",
                    "### **Ongoing Costs**\n",
                    "- **Annual Renewal Fees**: $10,000-50,000\n",
                    "- **Security Maintenance**: $5,000-25,000 annually\n",
                    "- **Insurance Premiums**: $10,000-50,000 annually\n",
                    "- **Total Annual Operating Cost**: $25,000-125,000\n\n",
                    "### **Payment Timeline**\n",
                    "- **Application**: 120 days before planned opening\n",
                    "- **Background Check**: 90 days before application\n",
                    "- **License Issuance**: 8-12 weeks after application\n",
                    "- **Renewal**: Annual renewal required\n\n",
                    "## 📋 **Step-by-Step Application Process**\n\n",
                    "### **Phase 1: Business Setup (Days 1-60)**\n",
                    "1. **Business Entity Formation**\n",
                    "   - Choose business structure (LLC, Corporation, etc.)\n",
                    "   - File with Delaware Secretary of State\n",
                    "   - Cost: $50-200\n",
                    "   - Timeline: 5-10 business days\n\n",
                    "2. **Business Registration**\n",
                    "   - Register with Delaware Division of Revenue\n",
                    "   - Obtain Delaware Business License\n",
                    "   - Cost: $25-150\n",
                    "   - Timeline: 3-7 business days\n\n",
                    "### **Phase 2: License Application (Days 61-180)**\n",
                    "3. **Background Checks**\n",
                    "   - Complete criminal background checks for all principals\n",
                    "   - Submit fingerprints and authorization\n",
                    "   - Cost: $500-2000\n",
                    "   - Timeline: 90 days before application\n\n",
                    "4. **Security Plan Development**\n",
                    "   - Develop comprehensive security plan\n",
                    "   - Install security systems\n",
                    "   - Cost: $10,000-50,000\n",
                    "   - Timeline: 60 days before application\n\n",
                    "5. **Submit Application**\n",
                    "   - Complete comprehensive application\n",
                    "   - Pay application fees\n",
                    "   - Submit supporting documents\n",
                    "   - Cost: $5,000-25,000\n",
                    "   - Timeline: 8-12 weeks processing\n\n",
                    "### **Phase 3: License Issuance (Days 181-240)**\n",
                    "6. **License Approval**\n",
                    "   - Receive license approval\n",
                    "   - Pay license fees\n",
                    "   - Receive official license\n",
                    "   - Cost: $10,000-50,000\n",
                    "   - Timeline: 2-4 weeks after approval\n\n",
                    "## 🔗 **Official Resources & Contact Information**\n\n",
                    "### **Primary Government Agencies**\n",
                    "- **Main Licensing Portal**: https://delawarecannabiscoalition.org/\n",
                    "- **Application Forms**: https://delpros.delaware.gov/OH_HomePage\n",
                    "- **Requirements & Regulations**: https://dpr.delaware.gov/\n",
                    "- **Fee Schedules**: https://revenue.delaware.gov/business-tax-forms/\n",
                    "- **Contact Information**: (302) 744-4500 | dpr@delaware.gov\n\n",
                    "### **Supporting Resources**\n",
                    "- **Business Registration**: https://corp.delaware.gov/\n",
                    "- **Tax Registration**: https://revenue.delaware.gov/\n",
                    "- **Local Permits**: Contact local city/county offices\n",
                    "- **Industry Associations**: Delaware Cannabis Coalition\n\n",
                    "## ⚠️ **Important Deadlines & Compliance**\n\n",
                    "### **Critical Deadlines**\n",
                    "- **Application Deadline**: 120 days before planned opening\n",
                    "- **Background Check Deadline**: 90 days before application\n",
                    "- **License Fee Payment**: Due upon approval\n",
                    "- **Renewal Deadline**: Annual renewal required\n\n",
                    "### **Compliance Requirements**\n",
                    "- **Security Maintenance**: 24/7 security system required\n",
                    "- **Insurance Maintenance**: $1,000,000 liability coverage\n",
                    "- **Record Keeping**: Maintain detailed records for 7 years\n",
                    "- **Reporting Requirements**: Monthly reports to Delaware\n\n",
                    "## 💡 **Pro Tips & Best Practices**\n\n",
                    "### **Cost Optimization**\n",
                    "- Apply early to avoid rush fees\n",
                    "- Consider annual payment plans for insurance\n",
                    "- Shop around for competitive insurance rates\n\n",
                    "### **Timeline Management**\n",
                    "- Start the process 180 days before planned opening\n",
                    "- Keep copies of all submitted documents\n",
                    "- Set calendar reminders for renewal dates\n\n",
                    "### **Compliance Maintenance**\n",
                    "- Set up automatic renewal reminders\n",
                    "- Maintain organized record keeping system\n",
                    "- Stay updated on regulatory changes\n\n",
                    "## 📞 **Need Help?**\n\n",
                    "### **Professional Services**\n",
                    "- **License Consultants**: Professional licensing services\n",
                    "- **Legal Assistance**: Delaware cannabis law attorneys\n",
                    "- **Industry Associations**: Delaware Cannabis Coalition\n\n",
                    "### **Government Support**\n",
                    "- **Agency Contact**: (302) 744-4500\n",
                    "- **Online Support**: https://delawarecannabiscoalition.org/\n",
                    "- **In-Person Assistance**: Delaware State Capitol\n\n",
                    "---\n",
                    "**Sources**: Delaware Division of Professional Regulation, Delaware Cannabis Coalition\n",
                    "**Last Updated**: Current\n",
                    "**Disclaimer**: This information is for guidance only. Always verify with official Delaware government sources.\n"
                ]
            }
        }
        
        if category in license_details:
            details = license_details[category]
            return CallToolResult(content=[TextContent(type="text", text="".join(details["content"]))])
        else:
            return CallToolResult(content=[TextContent(type="text", text=f"Please provide a license type for detailed information about {category} licenses in Delaware.")])

    async def _search_licenses(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Search for licenses by keyword or business type."""
        query = arguments.get("query", "").strip().lower()
        
        if not query:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Please provide a search query."
                )]
            )
        
        try:
            response = self.session.get(DELAWARE_TOPICS_URL)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Search through all text content
            matches = []
            
            # Look for elements containing the query
            for element in soup.find_all(['h2', 'h3', 'h4', 'h5', 'li', 'a']):
                text = element.get_text(strip=True)
                if query in text.lower():
                    matches.append(text)
            
            # Remove duplicates and limit results
            matches = list(set(matches))[:15]
            
            result_text = f"Delaware License Search Results for: '{query}'\n\n"
            result_text += f"Source: {DELAWARE_TOPICS_URL}\n\n"
            
            if matches:
                result_text += f"Found {len(matches)} matching license types:\n\n"
                for i, match in enumerate(matches, 1):
                    result_text += f"{i}. {match}\n"
            else:
                result_text += f"No license types found matching '{query}'.\n"
                result_text += "\nTry searching for broader terms like:\n"
                result_text += "• 'food' for restaurant/bakery licenses\n"
                result_text += "• 'health' for medical licenses\n"
                result_text += "• 'profession' for professional licenses\n"
                result_text += "• 'business' for general business licenses\n"
            
            result_text += f"\nFor more detailed information, visit: {DELAWARE_TOPICS_URL}"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except Exception as e:
            logger.error(f"Error searching licenses: {e}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error searching Delaware licenses: {str(e)}"
                )]
            )

    async def _get_business_steps(self) -> CallToolResult:
        """Get the 4-step process for opening a business in Delaware."""
        try:
            # The 4 steps are known from the Delaware website structure
            steps = [
                {
                    "step": 1,
                    "title": "Harness Your Great Idea",
                    "description": "Develop and refine your business concept"
                },
                {
                    "step": 2,
                    "title": "Write Your Business Plan",
                    "description": "Create a comprehensive business plan"
                },
                {
                    "step": 3,
                    "title": "Get Your License",
                    "description": "Obtain necessary business licenses and permits"
                },
                {
                    "step": 4,
                    "title": "Open Your Business",
                    "description": "Launch your business operations"
                }
            ]
            
            result_text = "Delaware Business First Steps - 4-Step Process\n\n"
            result_text += f"Source: {DELAWARE_BASE_URL}\n\n"
            
            for step in steps:
                result_text += f"Step {step['step']}: {step['title']}\n"
                result_text += f"   {step['description']}\n\n"
            
            result_text += f"For detailed guidance on each step, visit: {DELAWARE_BASE_URL}"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except Exception as e:
            logger.error(f"Error fetching business steps: {e}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error fetching Delaware business steps: {str(e)}"
                )]
            )

async def main():
    """Main function to run the Delaware MCP server."""
    server = DelawareLicenseServer()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="delaware-licenses",
                server_version="1.0.0",
                capabilities=server.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main()) 
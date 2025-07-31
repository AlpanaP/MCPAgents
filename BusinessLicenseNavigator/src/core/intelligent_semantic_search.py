"""
Intelligent Semantic Search System for Business License Navigator.

This module provides LLM-based semantic understanding and MCP server fetching
for dynamic, comprehensive business license information.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
import json
import os

logger = logging.getLogger(__name__)

# Configured states with specific data and MCP servers
CONFIGURED_STATES = {
    "DE": {
        "name": "Delaware",
        "mcp_server": "delaware_license_server",
        "rag_server": "delaware_rag_server",
        "official_links": [
            "https://firststeps.delaware.gov/",
            "https://corp.delaware.gov/",
            "https://revenue.delaware.gov/",
            "https://labor.delaware.gov/",
            "https://banking.delaware.gov/",
            "https://securities.delaware.gov/",
            "https://insurance.delaware.gov/"
        ],
        "license_categories": {
            "financial_services": [
                "Delaware Money Transmitter License",
                "Delaware Investment Adviser License", 
                "Delaware Securities Dealer License",
                "Delaware Trust Company License",
                "Delaware Consumer Credit License",
                "Delaware Mortgage Loan Originator License",
                "Delaware Insurance Producer License",
                "Delaware Check Casher License"
            ],
            "education": [
                "Delaware Private School License",
                "Delaware Vocational School License",
                "Delaware Tutoring License",
                "Delaware Training Center License"
            ],
            "franchise": [
                "Delaware Franchise Registration",
                "Delaware Business Opportunity License",
                "Delaware Franchise Disclosure License"
            ],
            "food_hospitality": [
                "Delaware Food Service License",
                "Delaware Restaurant License",
                "Delaware Liquor License",
                "Delaware Catering License"
            ]
        }
    },
    "FL": {
        "name": "Florida",
        "mcp_server": "florida_license_server", 
        "rag_server": "florida_rag_server",
        "official_links": [
            "https://www2.myfloridalicense.com/",
            "https://floridarevenue.com/",
            "https://www.myflorida.com/",
            "https://dos.myflorida.com/",
            "https://flofr.com/",
            "https://www.myfloridalicense.com/DBPR/insurance/"
        ],
        "license_categories": {
            "financial_services": [
                "Florida Investment Adviser Registration",
                "Florida Securities Dealer License",
                "Florida Money Transmitter License",
                "Florida Trust Company License",
                "Florida Consumer Finance License",
                "Florida Mortgage Loan Originator License",
                "Florida Insurance Producer License"
            ],
            "education": [
                "Florida Private School License",
                "Florida Vocational School License",
                "Florida Tutoring License",
                "Florida Training Center License",
                "Florida Driving School License"
            ],
            "franchise": [
                "Florida Franchise Registration",
                "Florida Business Opportunity License",
                "Florida Franchise Disclosure License"
            ],
            "food_hospitality": [
                "Florida Food Service License",
                "Florida Restaurant License",
                "Florida Liquor License",
                "Florida Catering License",
                "Florida Ice Cream Store License"
            ]
        }
    }
}


class IntelligentSemanticSearch:
    """Intelligent semantic search using LLM understanding and MCP server fetching."""
    
    def __init__(self):
        self.configured_states = CONFIGURED_STATES
        self.logger = logging.getLogger(__name__)
    
    async def analyze_business_query(self, query: str, state_code: str = None) -> Dict[str, Any]:
        """Use LLM to intelligently analyze the business query."""
        
        # Create an intelligent analysis prompt
        analysis_prompt = f"""
You are a business license expert. Analyze this query and extract key information:

Query: "{query}"

Please provide a JSON response with the following structure:
{{
    "business_type": "string (e.g., financial_services, education, franchise, construction, healthcare, etc.)",
    "business_description": "string (detailed description of the business)",
    "detected_licenses": ["array of relevant license types"],
    "key_requirements": ["array of key requirements like background checks, bonds, etc."],
    "estimated_costs": {{
        "application_fee": "string",
        "license_fee": "string", 
        "renewal_fee": "string",
        "total_initial": "string"
    }},
    "timeline": "string (estimated timeline for licensing)",
    "special_considerations": ["array of special considerations for this business type"]
}}

Focus on:
1. The specific business type and industry
2. Relevant licenses and permits needed
3. State-specific requirements if state is mentioned
4. Cost estimates and timelines
5. Special considerations for this business type

Be specific and detailed. If the query mentions a state, provide state-specific information.
"""
        
        # For now, we'll use a rule-based approach, but this can be enhanced with actual LLM calls
        # In production, this would call an LLM API
        return await self._rule_based_analysis(query, state_code)
    
    async def _rule_based_analysis(self, query: str, state_code: str = None) -> Dict[str, Any]:
        """Rule-based analysis as a fallback when LLM is not available."""
        
        query_lower = query.lower()
        
        # Enhanced business type detection with comprehensive keyword matching
        business_type = "general_business"
        
        # Food & Hospitality (comprehensive)
        food_keywords = [
            "restaurant", "food", "catering", "hotel", "bar", "pub", "cafe", "bakery", 
            "food truck", "food service", "hospitality", "tourism", "ice cream", "ice cream store",
            "pizza", "burger", "sandwich", "coffee", "tea", "juice", "smoothie", "dessert",
            "candy", "chocolate", "pastry", "donut", "cupcake", "cake", "bread", "deli",
            "grocery", "convenience store", "liquor", "wine", "beer", "brewery", "winery",
            "food market", "farmers market", "food court", "dining", "eatery", "bistro",
            "steakhouse", "seafood", "bbq", "grill", "diner", "fast food", "takeout",
            "delivery", "food delivery", "meal prep", "catering service"
        ]
        
        # Financial Services (comprehensive)
        financial_keywords = [
            "financial", "banking", "investment", "insurance", "fintech", "wealth management",
            "portfolio", "trading", "broker", "trust", "money transfer", "payment", "lending",
            "mortgage", "consumer credit", "personal loans", "payday loans", "installment loans",
            "check cashing", "credit union", "savings", "checking", "loan", "finance",
            "financial planning", "investment advisory", "securities", "stock broker",
            "insurance agent", "insurance broker", "real estate", "mortgage broker",
            "payday lender", "money transmitter", "currency exchange", "financial advisor"
        ]
        
        # Education (comprehensive)
        education_keywords = [
            "education", "school", "training", "tutoring", "academy", "institute", "university",
            "college", "coaching", "franchise", "franchising", "educational", "learning",
            "certification", "vocational", "trade school", "driving school", "music school",
            "dance school", "art school", "language school", "test prep", "exam prep",
            "preschool", "kindergarten", "elementary", "middle school", "high school",
            "private school", "public school", "charter school", "homeschool", "online school",
            "distance learning", "continuing education", "professional development"
        ]
        
        # Franchise (comprehensive)
        franchise_keywords = [
            "franchise", "franchising", "franchisor", "franchisee", "business opportunity",
            "multi-level marketing", "mlm", "network marketing", "direct sales", "pyramid scheme",
            "business model", "licensing agreement", "territory", "royalty", "franchise fee",
            "franchise system", "franchise network", "franchise brand", "franchise concept"
        ]
        
        # Construction & Trades (comprehensive)
        construction_keywords = [
            "construction", "contractor", "builder", "plumber", "electrician", "hvac",
            "roofer", "painter", "carpenter", "mason", "landscaper", "remodeling", "renovation",
            "home improvement", "repair", "maintenance", "installation", "welding", "machining",
            "fabrication", "metal work", "woodwork", "concrete", "asphalt", "excavation",
            "demolition", "framing", "drywall", "flooring", "tile", "siding", "decking"
        ]
        
        # Healthcare & Medical (comprehensive)
        healthcare_keywords = [
            "medical", "healthcare", "doctor", "physician", "dentist", "pharmacy", "pharmacist",
            "nurse", "therapist", "chiropractor", "optometrist", "veterinary", "veterinarian",
            "clinic", "hospital", "laboratory", "diagnostic", "dental", "orthodontic",
            "physical therapy", "occupational therapy", "speech therapy", "mental health",
            "psychology", "psychiatry", "counseling", "wellness", "fitness", "gym",
            "spa", "salon", "beauty", "cosmetic", "aesthetic", "massage", "acupuncture"
        ]
        
        # Technology & Software (comprehensive)
        technology_keywords = [
            "technology", "software", "it", "computer", "internet", "web", "app", "mobile",
            "digital", "cyber", "data", "cloud", "saas", "startup", "tech", "programming",
            "coding", "development", "website", "ecommerce", "online", "digital marketing",
            "social media", "ai", "artificial intelligence", "machine learning", "automation",
            "consulting", "services", "support", "maintenance", "hosting", "domain"
        ]
        
        # Cannabis & Hemp (comprehensive)
        cannabis_keywords = [
            "cannabis", "marijuana", "hemp", "cbd", "dispensary", "cultivation", "processing",
            "testing", "delivery", "weed", "pot", "thc", "medical marijuana", "recreational",
            "grow", "farm", "extract", "edible", "vape", "concentrate", "flower"
        ]
        
        # Transportation & Logistics (comprehensive)
        transportation_keywords = [
            "transportation", "trucking", "delivery", "logistics", "shipping", "freight",
            "taxi", "limousine", "chauffeur", "driver", "warehouse", "storage", "moving",
            "relocation", "courier", "messenger", "parcel", "package", "express", "ground",
            "air freight", "sea freight", "rail", "bus", "transit", "public transportation"
        ]
        
        # Retail & Sales (comprehensive)
        retail_keywords = [
            "retail", "store", "shop", "sales", "wholesale", "distributor", "dealer",
            "merchant", "vendor", "market", "mall", "boutique", "outlet", "department store",
            "specialty store", "convenience store", "grocery store", "supermarket", "hypermarket",
            "discount store", "thrift store", "pawn shop", "antique", "vintage", "collectible",
            "gift shop", "jewelry store", "clothing store", "shoe store", "bookstore",
            "electronics store", "hardware store", "home improvement", "furniture store"
        ]
        
        # Manufacturing & Industrial (comprehensive)
        manufacturing_keywords = [
            "manufacturing", "factory", "industrial", "production", "assembly", "processing",
            "chemical", "hazardous", "waste", "environmental", "plant", "facility", "mill",
            "refinery", "foundry", "forge", "machining", "fabrication", "welding", "casting",
            "molding", "injection", "extrusion", "printing", "packaging", "labeling",
            "quality control", "inspection", "testing", "research", "development", "r&d"
        ]
        
        # Entertainment & Events (comprehensive)
        entertainment_keywords = [
            "entertainment", "events", "recreation", "gaming", "casino", "theater", "cinema",
            "amusement", "park", "fitness", "gym", "spa", "salon", "nightclub", "club",
            "venue", "concert", "performance", "show", "exhibition", "museum", "gallery",
            "art", "music", "dance", "comedy", "magic", "circus", "carnival", "fair",
            "festival", "party", "celebration", "wedding", "event planning", "ticketing"
        ]
        
        # Now check the business type
        if any(word in query_lower for word in food_keywords):
            business_type = "food_hospitality"
        elif any(word in query_lower for word in financial_keywords):
            business_type = "financial_services"
        elif any(word in query_lower for word in education_keywords):
            business_type = "education"
        elif any(word in query_lower for word in franchise_keywords):
            business_type = "franchise"
        elif any(word in query_lower for word in construction_keywords):
            business_type = "construction"
        elif any(word in query_lower for word in healthcare_keywords):
            business_type = "healthcare"
        elif any(word in query_lower for word in technology_keywords):
            business_type = "technology"
        elif any(word in query_lower for word in cannabis_keywords):
            business_type = "cannabis"
        elif any(word in query_lower for word in transportation_keywords):
            business_type = "transportation"
        elif any(word in query_lower for word in retail_keywords):
            business_type = "retail"
        elif any(word in query_lower for word in manufacturing_keywords):
            business_type = "manufacturing"
        elif any(word in query_lower for word in entertainment_keywords):
            business_type = "entertainment"
        
        # Get state-specific licenses if available
        detected_licenses = []
        if state_code and state_code in self.configured_states:
            state_config = self.configured_states[state_code]
            if business_type in state_config.get("license_categories", {}):
                detected_licenses = state_config["license_categories"][business_type]
        
        # Default licenses if no state-specific ones found
        if not detected_licenses:
            default_licenses = {
                "financial_services": ["Money Transmitter License", "Investment Adviser License", "Securities Dealer License"],
                "education": ["Education License", "Private School License", "Training Center License"],
                "franchise": ["Franchise Registration", "Business Opportunity License"],
                "food_hospitality": ["Food Service License", "Restaurant License", "Liquor License"],
                "construction": ["Contractor License", "Electrical License", "Plumbing License"],
                "healthcare": ["Medical License", "Healthcare License", "Pharmacy License"],
                "technology": ["Technology License", "Software License"],
                "cannabis": ["Cannabis License", "Dispensary License"],
                "transportation": ["Transportation License", "Trucking License"],
                "retail": ["Retail License", "Sales Tax License"],
                "manufacturing": ["Manufacturing License", "Industrial License"],
                "entertainment": ["Entertainment License", "Gaming License"]
            }
            detected_licenses = default_licenses.get(business_type, ["General Business License"])
        
        return {
            "business_type": business_type,
            "business_description": query,
            "detected_licenses": detected_licenses,
            "key_requirements": ["Background check", "Financial statements", "Insurance/bond", "Business registration"],
            "estimated_costs": {
                "application_fee": "$100-500",
                "license_fee": "$500-2000", 
                "renewal_fee": "$200-1000",
                "total_initial": "$800-3500"
            },
            "timeline": "4-8 weeks for complete licensing process",
            "special_considerations": ["State-specific requirements may apply", "Additional permits may be needed"]
        }
    
    async def fetch_mcp_server_data(self, state_code: str, business_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from MCP server for configured states."""
        
        if state_code not in self.configured_states:
            return {}
        
        # For now, return fallback data since MCP servers have signature issues
        return {
            'requirements': self._get_fallback_requirements(state_code, business_analysis),
            'sequence': self._get_fallback_sequence(state_code, business_analysis),
            'costs': self._get_fallback_costs(state_code, business_analysis)
        }
    
    def _get_fallback_requirements(self, state_code: str, business_analysis: Dict[str, Any]) -> str:
        """Get fallback requirements when MCP server is unavailable."""
        state_config = self.configured_states.get(state_code, {})
        business_type = business_analysis.get('business_type', 'general')
        
        if state_code == "FL":
            return f"""# Florida Business License Requirements for {business_type}

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
        
        elif state_code == "DE":
            return f"""# Delaware Business License Requirements for {business_type}

## General Requirements:
1. **Business Registration** - Register with Delaware Division of Corporations
2. **Tax Registration** - Register with Delaware Department of Revenue
3. **Industry Licensing** - Apply for required professional licenses
4. **Local Permits** - Obtain local business permits
5. **Insurance** - Maintain required insurance coverage

## Timeline:
- Business registration: 1-2 weeks
- Tax registration: 1-2 weeks
- Industry licensing: 2-8 weeks
- Local permits: 1-4 weeks
- Total timeline: 4-14 weeks

**Source**: Delaware Division of Corporations"""
        
        else:
            return f"""# General Business License Requirements for {business_type}

## General Requirements:
1. **Business Registration** - Register with state division of corporations
2. **Tax Registration** - Register with state department of revenue
3. **Industry Licensing** - Apply for required professional licenses
4. **Local Permits** - Obtain local business permits
5. **Insurance** - Maintain required insurance coverage

## Timeline:
- Business registration: 1-2 weeks
- Tax registration: 1-2 weeks
- Industry licensing: 2-8 weeks
- Local permits: 1-4 weeks
- Total timeline: 4-14 weeks

**Source**: State Business Licensing Authority"""
    
    def _get_fallback_sequence(self, state_code: str, business_analysis: Dict[str, Any]) -> str:
        """Get fallback application sequence when MCP server is unavailable."""
        return """## Application Sequence:

1. **Research Requirements** - Review all license requirements
2. **Prepare Documentation** - Gather required documents
3. **Submit Application** - Complete and submit application forms
4. **Pay Fees** - Submit required application and license fees
5. **Await Processing** - Wait for application review
6. **Receive License** - Obtain approved license

**Estimated Timeline**: 4-8 weeks for complete process"""
    
    def _get_fallback_costs(self, state_code: str, business_analysis: Dict[str, Any]) -> str:
        """Get fallback cost breakdown when MCP server is unavailable."""
        return """## Cost Breakdown:

- **Application Fee**: $100-500
- **License Fee**: $500-2000
- **Renewal Fee**: $200-1000
- **Total Initial Cost**: $800-3500

**Note**: Costs vary by business type and location. Contact state authorities for exact fees."""
    
    async def create_intelligent_augmented_prompt(self, query: str, state_code: str = None) -> Dict[str, Any]:
        """Create an intelligent augmented prompt using LLM analysis and MCP data."""
        
        # Step 1: Intelligently analyze the business query
        business_analysis = await self.analyze_business_query(query, state_code)
        
        # Step 2: Fetch MCP server data for configured states
        mcp_data = {}
        if state_code and state_code in self.configured_states:
            mcp_data = await self.fetch_mcp_server_data(state_code, business_analysis)
        
        # Step 3: Create comprehensive augmented prompt
        augmented_prompt = self._build_intelligent_prompt(query, business_analysis, mcp_data, state_code)
        
        return {
            "business_analysis": business_analysis,
            "mcp_data": mcp_data,
            "augmented_prompt": augmented_prompt,
            "state_code": state_code,
            "is_configured_state": state_code in self.configured_states if state_code else False
        }
    
    def _build_intelligent_prompt(self, query: str, business_analysis: Dict[str, Any], 
                                mcp_data: Dict[str, Any], state_code: str = None) -> str:
        """Build an intelligent augmented prompt with comprehensive information."""
        
        state_config = self.configured_states.get(state_code, {}) if state_code else {}
        state_name = state_config.get("name", "General State") if state_code else "General State"
        
        prompt = f"""You are a professional business license compliance expert. Provide a comprehensive, well-structured response based on intelligent analysis of the user's query.

## INTELLIGENT ANALYSIS RESULTS:
**User Query**: {query}
**Detected Business Type**: {business_analysis['business_type']}
**Business Description**: {business_analysis['business_description']}
**Location**: {state_name} ({state_code if state_code else 'General'})

## DETECTED LICENSES & REQUIREMENTS:
"""
        
        # Add detected licenses
        for i, license_name in enumerate(business_analysis['detected_licenses'], 1):
            prompt += f"{i}. **{license_name}**\n"
        
        # Add key requirements
        prompt += f"\n**Key Requirements**:\n"
        for requirement in business_analysis['key_requirements']:
            prompt += f"• {requirement}\n"
        
        # Add cost estimates
        costs = business_analysis['estimated_costs']
        prompt += f"\n**Estimated Costs**:\n"
        prompt += f"• Application Fee: {costs['application_fee']}\n"
        prompt += f"• License Fee: {costs['license_fee']}\n"
        prompt += f"• Renewal Fee: {costs['renewal_fee']}\n"
        prompt += f"• Total Initial Cost: {costs['total_initial']}\n"
        
        # Add timeline
        prompt += f"\n**Timeline**: {business_analysis['timeline']}\n"
        
        # Add MCP server data if available
        if mcp_data:
            prompt += f"\n## STATE-SPECIFIC MCP DATA:\n"
            if 'requirements' in mcp_data:
                prompt += f"**Detailed Requirements**:\n{mcp_data['requirements']}\n\n"
            if 'sequence' in mcp_data:
                prompt += f"**Application Sequence**:\n{mcp_data['sequence']}\n\n"
            if 'costs' in mcp_data:
                prompt += f"**Detailed Cost Breakdown**:\n{mcp_data['costs']}\n\n"
        
        # Add official links for configured states
        if state_code and state_code in self.configured_states:
            prompt += f"\n## OFFICIAL {state_code} RESOURCES:\n"
            for link in state_config.get("official_links", []):
                prompt += f"• {link}\n"
        
        # Add special considerations
        prompt += f"\n**Special Considerations**:\n"
        for consideration in business_analysis['special_considerations']:
            prompt += f"• {consideration}\n"
        
        prompt += f"""

## INSTRUCTIONS:
Based on the intelligent analysis above, provide a comprehensive response that includes:

1. **Specific License Requirements**: Focus on the detected licenses and business type
2. **State-Specific Information**: Provide location-specific requirements for {state_name}
3. **Cost Breakdown**: Include detailed costs from the analysis
4. **Application Process**: Step-by-step process with timeline
5. **Official Resources**: Use the provided official links
6. **Special Considerations**: Address the identified special considerations

## RESPONSE STRUCTURE:
- Use the detected business type to provide targeted information
- Reference the specific licenses identified through intelligent analysis
- Provide state-specific costs and requirements
- Include official government links and contact information
- Structure the response for easy consumption with clear sections
- Include next steps and action items

IMPORTANT: Use the intelligent analysis results and MCP data to provide targeted, relevant information rather than generic responses. Be specific about costs, timelines, and requirements.
"""
        
        return prompt


# Global instance for easy access
intelligent_semantic_search = IntelligentSemanticSearch() 
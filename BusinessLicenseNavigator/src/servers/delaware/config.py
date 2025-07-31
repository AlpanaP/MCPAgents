"""
Configuration for Delaware RAG Server.

This module contains all configuration constants and settings
for the Delaware RAG server to improve maintainability.
"""

import os
from typing import List

# Delaware Business First Steps URL
DELAWARE_BASE_URL = "https://firststeps.delaware.gov"
DELAWARE_TOPICS_URL = "https://firststeps.delaware.gov/topics/"

# Qdrant configuration
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = "delaware_licenses"
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 embedding size

# Security: Rate limiting and timeout settings
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RATE_LIMIT_DELAY = 1  # seconds between requests

# Allowed domains for web scraping
ALLOWED_DOMAINS: List[str] = [
    'firststeps.delaware.gov',
    'corp.delaware.gov',
    'sos.delaware.gov',
    'revenue.delaware.gov',
    'labor.delaware.gov',
    'dhss.delaware.gov',
    'delawaresbdc.org',
    'choosedelaware.com',
    'delawarechamber.com',
    'sba.gov',
    'delaware.score.org',
    'nccde.org',
    'co.kent.de.us',
    'sussexcountyde.gov',
    'wilmingtonde.gov',
    'cityofdover.com',
    'newarkde.gov'
]

# Delaware license categories
LICENSE_CATEGORIES = [
    "Food Establishments",
    "Construction",
    "Healthcare",
    "Real Estate",
    "Automotive",
    "Beauty",
    "Financial",
    "Professional Services",
    "Manufacturing",
    "Retail",
    "Entertainment",
    "Transportation",
    "Agriculture",
    "Technology",
    "Consulting"
]

# Delaware business steps
BUSINESS_STEPS = [
    "Harness Your Great Idea",
    "Write Your Business Plan", 
    "Choose Your Business Structure",
    "Register Your Business"
]

# Delaware license data structure
LICENSE_DATA_STRUCTURE = {
    "food": {
        "keywords": ["restaurant", "food", "cafe", "catering", "bakery", "diner"],
        "license_types": ["Food Service License", "Restaurant License", "Catering License"],
        "requirements": ["Food safety training", "Health inspection", "Kitchen compliance"],
        "fees": ["Application fee: $100-300", "License fee: $200-500", "Inspection fee: $75-150"],
        "due_dates": ["Apply 45 days before opening", "Health inspection: 30 days before opening"]
    },
    "construction": {
        "keywords": ["construction", "contractor", "building", "renovation", "remodeling"],
        "license_types": ["General Contractor License", "Building Contractor License", "Specialty Contractor License"],
        "requirements": ["Experience verification", "Background check", "Financial responsibility"],
        "fees": ["Application fee: $200-500", "License fee: $300-800", "Background check: $50-100"],
        "due_dates": ["Apply 60 days before starting work", "Background check: 30 days before application"]
    },
    "cannabis": {
        "keywords": ["cannabis", "marijuana", "dispensary", "cultivation", "weed"],
        "license_types": ["Cannabis Business License", "Dispensary License", "Cultivation License"],
        "requirements": ["Comprehensive business plan", "Financial solvency proof", "Security plan"],
        "fees": ["Application fee: $5,000-25,000", "License fee: $10,000-50,000", "Background check: $500-2000"],
        "due_dates": ["Apply 120 days before planned opening", "Background check: 90 days before application"]
    }
} 
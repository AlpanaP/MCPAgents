"""
Test configuration and fixtures for Business License Navigator.

This module contains test settings, fixtures, and utility functions
for running tests consistently across the test suite.
"""

import os
import sys
import tempfile
import json
from typing import Dict, Any, List

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test configuration
TEST_CONFIG = {
    "timeout": 30,  # seconds
    "retry_attempts": 3,
    "log_level": "INFO",
    "cleanup_temp_files": True
}

# Test data fixtures
TEST_QUERIES = {
    "delaware_cannabis": "I want to open a weed dispensary in Delaware",
    "delaware_art": "I want to set up an art studio in Delaware",
    "florida_construction": "I want to open a construction company in Palm Harbor",
    "florida_restaurant": "I want to start a restaurant in Florida",
    "generic_ny_construction": "I want to open a construction company in New York",
    "generic_il_restaurant": "I want to start a restaurant in Illinois",
    "generic_ca_beauty": "I want to open a beauty salon in California"
}

TEST_STATES = {
    "DE": {
        "name": "Delaware",
        "type": "state",
        "country": "US",
        "rag_enabled": True,
        "mcp_enabled": True
    },
    "FL": {
        "name": "Florida", 
        "type": "state",
        "country": "US",
        "rag_enabled": True,
        "mcp_enabled": True
    },
    "NY": {
        "name": "New York",
        "type": "state", 
        "country": "US",
        "rag_enabled": True,
        "mcp_enabled": True
    },
    "IL": {
        "name": "Illinois",
        "type": "state",
        "country": "US", 
        "rag_enabled": True,
        "mcp_enabled": True
    },
    "CA": {
        "name": "California",
        "type": "state",
        "country": "US",
        "rag_enabled": True,
        "mcp_enabled": True
    }
}

TEST_BUSINESS_TYPES = {
    "construction": {
        "keywords": ["construction", "contractor", "building"],
        "license_types": ["General Contractor", "Building Contractor"],
        "requirements": ["Background check", "Experience verification"]
    },
    "restaurant": {
        "keywords": ["restaurant", "food", "cafe"],
        "license_types": ["Food Service License", "Restaurant License"],
        "requirements": ["Food safety training", "Health inspection"]
    },
    "beauty": {
        "keywords": ["beauty", "salon", "cosmetology"],
        "license_types": ["Cosmetology License", "Hair Stylist License"],
        "requirements": ["Education completion", "Examination"]
    },
    "cannabis": {
        "keywords": ["cannabis", "marijuana", "dispensary", "weed"],
        "license_types": ["Cannabis Business License", "Dispensary License"],
        "requirements": ["Background check", "Financial responsibility"]
    }
}

def create_temp_config() -> str:
    """Create a temporary configuration file for testing."""
    temp_config = {
        "states": TEST_STATES,
        "business_types": TEST_BUSINESS_TYPES,
        "test_mode": True
    }
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(temp_config, temp_file)
    temp_file.close()
    
    return temp_file.name

def cleanup_temp_files(temp_files: List[str]) -> None:
    """Clean up temporary files created during testing."""
    if not TEST_CONFIG["cleanup_temp_files"]:
        return
    
    for temp_file in temp_files:
        try:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        except Exception as e:
            print(f"Warning: Could not clean up temp file {temp_file}: {e}")

def get_test_query(business_type: str, state: str) -> str:
    """Get a test query for a specific business type and state."""
    key = f"{state.lower()}_{business_type}"
    return TEST_QUERIES.get(key, f"I want to open a {business_type} business in {state}")

def validate_test_result(result: str, expected_keywords: List[str]) -> bool:
    """Validate that a test result contains expected keywords."""
    if not result:
        return False
    
    result_lower = result.lower()
    return all(keyword.lower() in result_lower for keyword in expected_keywords)

def get_expected_keywords(business_type: str, state: str) -> List[str]:
    """Get expected keywords for a business type and state."""
    keywords = [business_type, state]
    
    # Add business type specific keywords
    if business_type in TEST_BUSINESS_TYPES:
        keywords.extend(TEST_BUSINESS_TYPES[business_type]["keywords"])
    
    return keywords

class TestLogger:
    """Simple test logger for consistent test output."""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
    
    def info(self, message: str) -> None:
        print(f"ℹ️  [{self.test_name}] {message}")
    
    def success(self, message: str) -> None:
        print(f"✅ [{self.test_name}] {message}")
    
    def error(self, message: str) -> None:
        print(f"❌ [{self.test_name}] {message}")
    
    def warning(self, message: str) -> None:
        print(f"⚠️  [{self.test_name}] {message}")

def run_test_with_timeout(test_func, timeout: int = None) -> Dict[str, Any]:
    """Run a test function with timeout protection."""
    import signal
    
    timeout = timeout or TEST_CONFIG["timeout"]
    
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Test timed out after {timeout} seconds")
    
    # Set up timeout handler
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    
    try:
        result = test_func()
        signal.alarm(0)  # Cancel the alarm
        return {"success": True, "result": result}
    except TimeoutError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        signal.alarm(0)  # Cancel the alarm
        return {"success": False, "error": str(e)} 
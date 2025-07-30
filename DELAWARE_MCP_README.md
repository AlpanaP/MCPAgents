# Delaware Business License MCP Tools

This project provides MCP (Model Context Protocol) tools to access Delaware business license information from the official [Delaware Business First Steps](https://firststeps.delaware.gov/topics/) website.

## 🏢 Available Tools

### 1. `get_delaware_license_categories`
- **Description**: Get all available license categories from Delaware Business First Steps
- **Parameters**: None
- **Returns**: List of all license categories available in Delaware

### 2. `get_delaware_license_details`
- **Description**: Get detailed information about a specific license type from Delaware
- **Parameters**: 
  - `category` (required): License category (e.g., 'Food', 'Health', 'Professions')
  - `license_type` (optional): Specific license type within the category
- **Returns**: Detailed information about licenses in the specified category

### 3. `search_delaware_licenses`
- **Description**: Search for licenses by keyword or business type
- **Parameters**:
  - `query` (required): Search query (e.g., 'restaurant', 'bakery', 'consulting')
- **Returns**: Matching license types based on the search query

### 4. `get_delaware_business_steps`
- **Description**: Get the 4-step process for opening a business in Delaware
- **Parameters**: None
- **Returns**: The official 4-step process for starting a business in Delaware

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Test the Tools
```bash
python test_delaware_mcp.py
```

### Use with MCP Client
1. Add the Delaware MCP server to your MCP configuration:
```json
{
  "mcpServers": {
    "delaware_licenses": {
      "command": "python",
      "args": ["delaware_mcp_server.py"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

2. The tools will be available in your MCP client for querying Delaware business license information.

## 📋 License Categories Available

Based on the [Delaware Business First Steps](https://firststeps.delaware.gov/topics/) website, the following categories are available:

- **Agriculture** - Beekeepers, Commercial Feeds, Fertilizers, etc.
- **Alcohol** - Liquor Licenses
- **Automobile** - Auto Body Shops, Motor Vehicle Dealers, etc.
- **Banking** - Check Cashers, Licensed Lenders, etc.
- **Boating** - Charter Boat Licenses, River Pilots, etc.
- **Child Care** - Child Care Facilities, Residential Programs, etc.
- **Consumer Protection** - Alarm Agencies, Debt Management, etc.
- **Contractors/Building/Construction** - Architects, Electricians, Plumbers, etc.
- **Corporations** - Entity Formation, Foreign Qualification, etc.
- **Courts** - "Doing Business As" Name Registration
- **Educational Institutions** - Schools of Cosmetology and Barbering
- **Employers** - Employee Withholding, Unemployment Insurance, etc.
- **Environmental Protection** - Storage Tanks, Waste Management, etc.
- **Equine** - Harness Racing, Thoroughbred Racing
- **Food** - Restaurants, Food Trucks, Bakeries, Caterers, etc.
- **General Business License** - General Business Licenses
- **Health** - Medical Professionals, Healthcare Facilities, etc.
- **Lottery/Gaming** - Lottery Retailers
- **Manufacturing** - Chemical Safety, Boilers, etc.
- **Professions** - Accountants, Attorneys, Engineers, etc.
- **Protecting the Public** - Adult Entertainment, Fire Marshal, etc.
- **Roads and Access** - Commercial Drivers, Taxi Drivers, etc.
- **Special Event/Sporting Event** - Boxing, Gaming Events, etc.

## 🔧 Configuration Files

### `license_sources.json`
Contains the configuration for all license information sources, including Delaware:

```json
{
  "sources": {
    "delaware": {
      "name": "Delaware Business First Steps",
      "url": "https://firststeps.delaware.gov/topics/",
      "description": "Official Delaware government website for business licenses and registrations",
      "categories": [...],
      "mcp_tools": [...]
    }
  }
}
```

### `delaware_mcp.json`
MCP server configuration for the Delaware license tools.

## 🧪 Testing

Run the test script to verify all tools are working:

```bash
python test_delaware_mcp.py
```

This will test:
1. Getting license categories
2. Searching for food-related licenses
3. Getting business steps
4. Getting detailed license information

## 📞 Example Usage

### Get All License Categories
```python
# This will return all available license categories in Delaware
result = await server._get_license_categories()
```

### Search for Restaurant Licenses
```python
# Search for food-related licenses
result = await server._search_licenses({"query": "restaurant"})
```

### Get Food License Details
```python
# Get detailed information about food licenses
result = await server._get_license_details({"category": "Food"})
```

### Get Business Steps
```python
# Get the 4-step process for opening a business
result = await server._get_business_steps()
```

## 🔗 Data Source

All information is sourced from the official [Delaware Business First Steps](https://firststeps.delaware.gov/topics/) website, which provides comprehensive information about:

- Business licenses and registrations
- Professional licenses
- Industry-specific permits
- Step-by-step guidance for starting a business

## 📝 Notes

- The tools use web scraping to extract information from the Delaware government website
- Results are cached to improve performance
- Error handling is implemented for network issues and parsing problems
- All tools return structured text responses with source attribution

## 🤝 Contributing

To add more license sources or improve the tools:

1. Update `license_sources.json` with new sources
2. Create corresponding MCP server files
3. Add test cases to `test_delaware_mcp.py`
4. Update this README with new information 
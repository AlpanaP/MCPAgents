# TestEndPoints

A testing environment for various API endpoints, including Google's Gemini API with MCP (Model Context Protocol) servers for enhanced functionality.

## Features

- ✅ **Gemini API Integration**: Direct API calls with comprehensive testing
- ✅ **MCP Fetch Server**: Real-time web content fetching
- ✅ **MCP Playwright Server**: Browser automation for dynamic content
- ✅ **Enhanced Business License Queries**: Combine real-time data with AI analysis
- ✅ **Comprehensive Testing**: Multiple test scenarios and error handling

## Setup

### Prerequisites

- Python 3.13+
- Virtual environment (recommended)
- Node.js (optional, for full MCP server functionality)

### Installation

1. **Activate the virtual environment:**
   ```bash
   source bin/activate
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt --break-system-packages
   ```
   
   Or install individually:
   ```bash
   pip install google-generativeai python-dotenv requests httpx pydantic mcp mcp-use playwright --break-system-packages
   ```

3. **Install Playwright browsers (if using Playwright MCP server):**
   ```bash
   playwright install
   ```

4. **Set up environment variables:**
   Create a `.env` file in the project root with your API keys:
   ```bash
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```

## Usage

### Testing Gemini API

1. **Run the comprehensive test:**
   ```bash
   python callGeminiAPI.py
   ```

2. **Run the simple test:**
   ```bash
   python test_gemini_simple.py
   ```

### Testing MCP Servers

1. **Test MCP servers only:**
   ```bash
   python mcp_servers.py
   ```

2. **Test MCP + Gemini integration:**
   ```bash
   python test_mcp_gemini.py
   ```

### What the tests do

#### **Gemini API Tests:**
- **Simple Query Test:** Tests basic connectivity with a general business license question
- **Business License Query Test:** Tests with a specific ice cream franchise query in Florida
- **API Key Validation:** Ensures the API key is properly configured
- **Response Quality:** Verifies that Gemini provides detailed, relevant responses

#### **MCP Server Tests:**
- **Fetch Server Test:** Tests HTTP content fetching from government websites
- **Playwright Server Test:** Tests browser automation for dynamic content extraction
- **Integration Test:** Combines MCP data with Gemini AI for enhanced analysis

#### **Enhanced Integration Tests:**
- **Real-time Data Fetching:** Uses MCP servers to get current information
- **AI Analysis:** Combines fetched data with Gemini for comprehensive responses
- **Multi-state Support:** Tests different states (FL, DE, CA, TX)
- **Error Handling:** Robust error handling for network and API issues

### Expected Results

✅ **Successful tests will show:**
- API connectivity confirmation
- MCP server connection status
- Real-time data fetching results
- Enhanced AI responses with current information
- Proper error handling for missing API keys
- Response quality validation

❌ **Failed tests will show:**
- Missing API key errors
- Import errors for missing packages
- Network connectivity issues
- MCP server connection failures

## MCP Servers

### Fetch Server
- **Purpose:** HTTP content fetching from government websites
- **Capabilities:** GET requests, content extraction, header analysis
- **Use Case:** Getting current license requirements and fees

### Playwright Server
- **Purpose:** Browser automation for dynamic content
- **Capabilities:** Screenshots, form filling, JavaScript execution
- **Use Case:** Extracting data from complex government websites

### Integration Benefits
- **Real-time Data:** Always current information from official sources
- **Enhanced Accuracy:** AI analysis based on live data
- **Comprehensive Coverage:** Multiple data sources for complete information
- **Automated Updates:** No manual data maintenance required

## Dependencies

The project uses the following main dependencies:

### Core Dependencies
- `google-generativeai`: Google's Gemini API client
- `python-dotenv`: Environment variable management
- `requests`: HTTP client library
- `httpx`: Modern HTTP client
- `pydantic`: Data validation

### MCP Dependencies
- `mcp`: Model Context Protocol core library
- `mcp-use`: MCP client utilities
- `mcp-server-fetch`: HTTP fetch server
- `mcp-server-playwright`: Browser automation server
- `playwright`: Browser automation framework

### Development Dependencies
- `pytest`: Testing framework
- `pytest-asyncio`: Async testing support
- `black`: Code formatting
- `flake8`: Code linting

## Configuration

### Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key
  - Get your API key from: https://makersuite.google.com/app/apikey

### MCP Configuration

The project includes:
- `mcp_config.json`: Node.js-based MCP server configuration
- `mcp_servers.py`: Python-based MCP server implementation
- `test_mcp_gemini.py`: Integration testing script

### API Key Setup

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

## Project Structure

```
TestEndPoints/
├── callGeminiAPI.py          # Comprehensive Gemini API test
├── test_gemini_simple.py     # Simple API connectivity test
├── mcp_servers.py            # MCP server implementation
├── test_mcp_gemini.py        # MCP + Gemini integration test
├── mcp_config.json           # MCP server configuration
├── .env                      # Environment variables (create this)
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

## Advanced Usage

### Custom MCP Server Integration

You can extend the MCP functionality by:

1. **Adding new servers** in `mcp_servers.py`
2. **Customizing fetch behavior** for specific websites
3. **Implementing custom browser automation** for complex workflows
4. **Integrating with other AI models** beyond Gemini

### Business License Queries

The enhanced integration supports:

- **Multi-state analysis** (FL, DE, CA, TX, etc.)
- **Real-time fee updates** from government websites
- **Current requirement changes** through live data
- **Automated form analysis** for application processes

### Error Handling

The system includes robust error handling for:

- **Network connectivity issues**
- **API rate limiting**
- **Invalid responses**
- **Missing dependencies**
- **Configuration errors**

## Troubleshooting

### Common Issues

1. **"No module named 'mcp'"**
   - Solution: Install MCP packages
   ```bash
   pip install mcp mcp-use --break-system-packages
   ```

2. **"Playwright browsers not found"**
   - Solution: Install Playwright browsers
   ```bash
   playwright install
   ```

3. **"API key not valid"**
   - Solution: Check your API key in the `.env` file
   - Ensure the key is correct and active

4. **"externally-managed-environment"**
   - Solution: Use the `--break-system-packages` flag
   ```bash
   pip install package_name --break-system-packages
   ```

5. **"MCP server connection failed"**
   - Solution: Check network connectivity
   - Verify server configurations in `mcp_config.json`

### Virtual Environment Issues

If the virtual environment doesn't have pip:
```bash
deactivate
python callGeminiAPI.py
```

### MCP Server Issues

If MCP servers fail to connect:
1. Check if Node.js is installed (for Node-based servers)
2. Verify network connectivity
3. Check server configurations
4. Try the Python-based implementation in `mcp_servers.py`

## License

This project is for testing purposes only.

## Contributing

To add new features:
1. Add new MCP servers to `mcp_servers.py`
2. Update `pyproject.toml` with new dependencies
3. Create test scripts for new functionality
4. Update this README with new features

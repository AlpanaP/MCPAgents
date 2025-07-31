# TestEndPoints

A testing environment for various API endpoints, including Google's Gemini API.

## Setup

### Prerequisites

- Python 3.13+
- Virtual environment (recommended)

### Installation

1. **Activate the virtual environment:**
   ```bash
   source bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install google-generativeai python-dotenv requests httpx pydantic --break-system-packages
   ```

3. **Set up environment variables:**
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

### What the tests do

- **Simple Query Test:** Tests basic connectivity with a general business license question
- **Business License Query Test:** Tests with a specific ice cream franchise query in Florida
- **API Key Validation:** Ensures the API key is properly configured
- **Response Quality:** Verifies that Gemini provides detailed, relevant responses

### Expected Results

✅ **Successful tests will show:**
- API connectivity confirmation
- Detailed responses about business licensing
- Proper error handling for missing API keys
- Response quality validation

❌ **Failed tests will show:**
- Missing API key errors
- Import errors for missing packages
- Network connectivity issues

## Dependencies

The project uses the following main dependencies:

- `google-generativeai`: Google's Gemini API client
- `python-dotenv`: Environment variable management
- `requests`: HTTP client library
- `httpx`: Modern HTTP client
- `pydantic`: Data validation

## Configuration

### Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key
  - Get your API key from: https://makersuite.google.com/app/apikey

### API Key Setup

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

## Troubleshooting

### Common Issues

1. **"No module named 'dotenv'"**
   - Solution: Install python-dotenv
   ```bash
   pip install python-dotenv --break-system-packages
   ```

2. **"API key not valid"**
   - Solution: Check your API key in the `.env` file
   - Ensure the key is correct and active

3. **"externally-managed-environment"**
   - Solution: Use the `--break-system-packages` flag
   ```bash
   pip install package_name --break-system-packages
   ```

### Virtual Environment Issues

If the virtual environment doesn't have pip:
```bash
deactivate
python callGeminiAPI.py
```

## Project Structure

```
TestEndPoints/
├── callGeminiAPI.py          # Comprehensive Gemini API test
├── test_gemini_simple.py     # Simple API connectivity test
├── .env                      # Environment variables (create this)
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

## License

This project is for testing purposes only.

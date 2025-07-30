# MCP Demo Chat Application

A simple chat application that uses MCP (Model Context Protocol) agents with built-in conversation memory.

## Features

- Interactive chat interface with MCP agents
- Built-in conversation memory for contextual interactions
- Support for multiple MCP servers:
  - **Playwright**: Browser automation and web scraping
  - **Fetch**: Web requests and data retrieval
  - **Airbnb**: Property search and data collection
- Uses Groq's Llama 3.3 70B model for responses
- Structured responses with Summary, Topic, Result, and Tool Used sections

## Setup

### 1. Install Dependencies

The project uses `uv` for dependency management. All dependencies are already configured in `pyproject.toml`.

### 2. Get a Groq API Key

1. Visit [Groq Console](https://console.groq.com/)
2. Sign up or log in to your account
3. Create a new API key
4. Copy the API key (starts with `gsk_`)

### 3. Configure Environment Variables

Create a `.env` file in the project root with your Groq API key:

```bash
GROQ_API_KEY=gsk_your_actual_api_key_here
```

Replace `gsk_your_actual_api_key_here` with your actual Groq API key.

### 4. Verify MCP Servers

The application uses three MCP servers configured in `browser_mcp.json`:

- **Playwright**: For browser automation and web scraping
- **Fetch**: For web requests and data retrieval
- **Airbnb**: For Airbnb property search and data

All servers are configured and should work out of the box.

## Usage

### Running the Chat Application

```bash
uv run python chat_app.py
```

### Chat Commands

- Type your message and press Enter to chat
- Type `exit` or `quit` to end the conversation
- Type `clear` to clear the conversation history
- Type `servers` to see available MCP servers

### Example Usage

```
You: Hello! Can you help me search for information about Python programming?

Assistant: 
## Summary
I searched for current information about Python programming and found comprehensive resources.

## Topic
Python programming information and resources

## Result
Python is a high-level, interpreted programming language known for its simplicity and readability. Here are some key aspects:
- Easy to learn and use
- Extensive standard library
- Large ecosystem of third-party packages
- Cross-platform compatibility
- Strong community support

## Tool Used
Fetch server - web requests and data retrieval

You: Can you search for Airbnb properties in New York City?

Assistant:
## Summary
I searched for Airbnb properties in New York City and found available listings with pricing information.

## Topic
Airbnb properties in New York City

## Result
[Detailed property listings with prices, amenities, and availability]

## Tool Used
Airbnb server - property search and data
```

## MCP Servers

### Playwright Server
- Browser automation and control
- Web scraping and data extraction
- Taking screenshots
- Form filling and interaction
- Navigation and page manipulation

### Fetch Server
- Web requests and HTTP calls
- Data retrieval from APIs
- Content downloading
- Network communication

### Airbnb Server
- Property search and discovery
- Pricing information
- Property details and amenities
- Availability checking
- Location-based searches

## Project Structure

- `chat_app.py` - Main chat application with memory support
- `browser_mcp.json` - MCP server configuration
- `main.py` - Simple hello world example
- `pyproject.toml` - Project dependencies and configuration

## Troubleshooting

### Common Issues

1. **"GROQ API key not found"**
   - Make sure you've created a `.env` file with your Groq API key
   - Verify the API key is correct and starts with `gsk_`

2. **JSON parsing errors**
   - The `browser_mcp.json` file has been fixed and should work correctly

3. **Missing dependencies**
   - Run `uv sync` to ensure all dependencies are installed

4. **MCP server connection issues**
   - Ensure you have Node.js installed for Playwright and Airbnb servers
   - Verify network connectivity for web requests

### Getting Help

If you encounter any issues:
1. Check that your Groq API key is valid
2. Ensure you have a stable internet connection
3. Verify that the MCP servers are accessible
4. Use the `servers` command to check available tools

## Dependencies

- `mcp-use` - MCP client and agent functionality
- `langchain-groq` - Groq LLM integration
- `python-dotenv` - Environment variable management
- `langchain-openai` - Additional LLM support

## License

This project is for educational and demonstration purposes.

# 🚀 BusinessLicenseNavigator

**AI-powered business license guidance system with MCP integration**

A modern, scalable system that provides intelligent business license guidance across multiple states and provinces using advanced AI, semantic search, and Model Context Protocol (MCP) integration.

## ✨ Features

### 🤖 **Intelligent AI System**
- **Semantic Search**: Advanced natural language processing to understand business queries
- **Multi-State Support**: Delaware, Florida, and generic state handling
- **MCP Integration**: Model Context Protocol for enhanced capabilities
- **Chat Interface**: Interactive conversation with history and context

### 🏛️ **State-Specific Guidance**
- **Delaware (DE)**: Comprehensive financial services and business licensing
- **Florida (FL)**: Food service, education, and franchise licensing
- **Generic States**: AI-powered reasoning for other states/provinces

### 🔧 **Technical Capabilities**
- **Browser Automation**: Playwright for web scraping and data retrieval
- **Fetch Integration**: Real-time data from official state websites
- **Vector Database**: Qdrant for semantic search and retrieval
- **Modern Architecture**: Clean, modular, and scalable design

## 🏗️ Project Structure

```
BusinessLicenseNavigator/
├── 📁 src/                     # Source code
│   ├── 📁 core/               # Core business logic
│   │   ├── ai_services.py     # AI service integrations
│   │   ├── config_manager.py  # Configuration management
│   │   ├── intelligent_semantic_search.py  # Semantic search engine
│   │   ├── monitoring.py      # System monitoring
│   │   ├── prompt_builder.py  # Dynamic prompt construction
│   │   ├── factories/         # Factory patterns
│   │   ├── handlers/          # Request handlers
│   │   └── models/            # Data models
│   ├── 📁 servers/            # State-specific servers
│   │   ├── delaware/         # Delaware RAG & MCP servers
│   │   ├── florida/          # Florida RAG & MCP servers
│   │   ├── generic/          # Generic RAG & MCP servers
│   │   └── template/         # Template for new states
│   ├── 📁 config/             # Configuration files
│   │   ├── app_config.json    # Application configuration
│   │   ├── states.json        # State-specific data
│   │   ├── mcp_servers.json   # MCP server configuration
│   │   ├── rag_servers.json   # RAG server configuration
│   │   ├── business_types.json # Business type mappings
│   │   ├── license_sources.json # License sources
│   │   └── mcp_config.json    # MCP configuration
│   ├── chat_interface.py      # Interactive chat interface
│   ├── enhanced_agent.py      # Enhanced AI agent
│   └── add_new_state.py       # State addition utility
├── 📁 tests/                   # Test files
│   └── test_state_structure.py # Structure testing utility
├── 📁 markdowns/               # Documentation
│   ├── README.md              # Documentation index
│   ├── ARCHITECTURE.md        # Technical architecture
│   └── MCP_INTEGRATION_SUMMARY.md  # MCP integration guide
├── 📄 main.py                  # Application entry point
├── 📄 Makefile                 # Development tasks and automation
├── 📄 pyproject.toml          # Project dependencies
└── 📄 README.md               # This file
```

## 🚀 Quick Start

### 1. **Install Dependencies**
```bash
# Install with development tools
make install-dev

# Or install core dependencies only
make install
```

### 2. **Configure Environment**
```bash
# Create .env file
cp .env.example .env

# Add your API keys
echo "GOOGLE_API_KEY=your_gemini_api_key" >> .env
echo "GROQ_API_KEY=your_groq_api_key" >> .env
```

### 3. **Run the Application**
```bash
# Start chat interface
make run

# Or run web interface (if available)
make run-web
```

## 💬 Usage Examples

### **Chat Interface**
```bash
python main.py
```

**Example Queries:**
- "I want to open an ice cream store in Florida"
- "What licenses do I need for a financial services firm in Delaware?"
- "How do I start a restaurant in California?"
- "What are the requirements for a construction company in Texas?"

### **Commands**
- `exit` - Quit the application
- `clear` - Clear conversation history
- `history` - Show conversation history
- `servers` - List available MCP servers
- `help` - Show available commands

## 🔧 Development Tools

### **Makefile Commands**
The project includes a comprehensive Makefile for common development tasks:

```bash
make help          # Show all available commands
make install-dev   # Install development dependencies
make run           # Run the chat interface
make test          # Run all tests
make quality       # Run all code quality checks
make clean         # Clean build artifacts
make info          # Show project information
```

### **Adding New States**
```bash
make add-state STATE=CA NAME="California"
```

### **MCP Server Setup**
1. Install MCP servers:
   ```bash
   npm install -g @playwright/mcp
   uvx install mcp-server-fetch
   ```

2. Configure in `mcp_config.json`:
   ```json
   {
     "mcpServers": {
       "playwright": {
         "command": "npx",
         "args": ["@playwright/mcp@latest"]
       },
       "fetch": {
         "command": "uvx",
         "args": ["mcp-server-fetch"]
       }
     }
   }
   ```

## 🧪 Testing

### **Run Tests**
```bash
# Run all tests
make test

# Run with coverage
make test-coverage
```

### **Code Quality**
```bash
# Run all quality checks
make quality

# Or run individually:
make format    # Format code
make lint      # Lint code
make type-check # Type checking
```

## 📊 Architecture

### **Core Components**
1. **Enhanced Agent**: Orchestrates AI interactions and MCP calls
2. **Intelligent Semantic Search**: Maps queries to business types and licenses
3. **Chat Interface**: Provides interactive user experience
4. **Server Factory**: Dynamically creates state-specific servers
5. **Configuration Manager**: Centralized configuration management

### **Data Flow**
```
User Query → Chat Interface → Enhanced Agent → Semantic Search → MCP/RAG → Response
```

## 🔒 Security

- **Input Sanitization**: All user inputs are sanitized
- **API Key Management**: Secure environment variable handling
- **Rate Limiting**: Built-in protection against abuse
- **Error Handling**: Comprehensive error management

## 🚀 Deployment

### **Local Development**
```bash
# Install dependencies
pip install -e ".[dev]"

# Run application
python main.py
```

### **Production**
```bash
# Install production dependencies
pip install -e .

# Set environment variables
export GOOGLE_API_KEY=your_key
export GROQ_API_KEY=your_key

# Run application
python main.py
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-state`
3. **Make your changes**
4. **Run tests**: `pytest`
5. **Format code**: `black .`
6. **Submit a pull request**

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📚 Documentation

- **Main Documentation**: See [markdowns/README.md](markdowns/README.md) for comprehensive guides
- **Architecture**: [markdowns/ARCHITECTURE.md](markdowns/ARCHITECTURE.md) for technical details
- **MCP Integration**: [markdowns/MCP_INTEGRATION_SUMMARY.md](markdowns/MCP_INTEGRATION_SUMMARY.md) for integration details

## 🆘 Support

- **Issues**: Create an issue on GitHub
- **Documentation**: Check the [markdowns/](markdowns/) directory for technical details
- **Questions**: Open a discussion on GitHub

---

**Built with ❤️ using modern Python, AI, and MCP technologies**

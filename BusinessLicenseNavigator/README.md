# Business License Navigator

A comprehensive AI-powered business license guidance system with Delaware RAG (Retrieval-Augmented Generation) integration.

## 🏗️ Project Structure

```
BusinessLicenseNavigator/
├── agent.py                 # Main AI agent with Delaware RAG integration
├── streamlit_app.py         # Streamlit web application
├── setup_qdrant.py          # Qdrant vector database setup script
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Project configuration
├── README.md               # This file
├── delaware_rag/           # Delaware RAG package
│   ├── __init__.py
│   ├── delaware_rag_server.py    # RAG-enhanced MCP server
│   └── delaware_mcp_server.py    # Basic MCP server
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── test_delaware_rag.py     # RAG functionality tests
│   └── test_delaware_mcp.py     # MCP functionality tests
├── docs/                   # Documentation
│   ├── DELAWARE_RAG_README.md   # Delaware RAG documentation
│   └── DELAWARE_MCP_README.md   # Delaware MCP documentation
├── config/                 # Configuration files
│   ├── license_sources.json     # License sources configuration
│   └── delaware_mcp.json        # MCP server configuration
└── ui/                     # UI components
    └── app.py              # Legacy UI (deprecated)
```

## 🚀 Features

### **AI-Powered Guidance**
- **Gemini AI**: Google's AI for cloud deployment
- **Ollama**: Local AI for privacy-focused users
- **Fallback Mode**: Rule-based guidance when AI unavailable

### **Delaware RAG Integration**
- **Semantic Search**: AI-powered license search
- **Similarity Matching**: Find related license types
- **Vector Database**: Qdrant for efficient retrieval
- **Official Data**: Delaware Business First Steps integration

### **Source Attribution**
- **Location Detection**: Automatic state/province detection
- **Transparency**: Clear source attribution for all responses
- **State-Specific Links**: Relevant government resources

## 🛠️ Setup

### **1. Install Dependencies**
```bash
cd BusinessLicenseNavigator
pip install -r requirements.txt
```

### **2. Setup Qdrant Vector Database**
```bash
python setup_qdrant.py
```

### **3. Test Delaware RAG Tools**
```bash
python tests/test_delaware_rag.py
```

### **4. Run the Application**
```bash
streamlit run streamlit_app.py
```

## 🧪 Testing

### **Run All Tests**
```bash
python -m pytest tests/
```

### **Test Delaware RAG**
```bash
python tests/test_delaware_rag.py
```

### **Test Delaware MCP**
```bash
python tests/test_delaware_mcp.py
```

## 📚 Documentation

- **Delaware RAG**: See `docs/DELAWARE_RAG_README.md`
- **Delaware MCP**: See `docs/DELAWARE_MCP_README.md`
- **Configuration**: See `config/license_sources.json`

## 🎯 Usage Examples

### **Delaware Queries**
```
"I run a home bakery in Delaware"
"Restaurant business in DE"
"Consulting services in Delaware"
```

### **Other State Queries**
```
"Online business in Texas"
"Food truck in California"
"Consulting in New York"
```

## 🔧 Configuration

### **Environment Variables**
```bash
export GEMINI_API_KEY=your_gemini_api_key_here
```

### **Qdrant Configuration**
- **Host**: localhost
- **Port**: 6333
- **Collection**: delaware_licenses
- **Vector Size**: 384 (all-MiniLM-L6-v2)

## 📊 Response Sources

The system automatically detects location and provides appropriate sources:

- **Delaware**: Official Delaware Business First Steps + RAG
- **Texas**: Texas Secretary of State resources
- **California**: California Secretary of State resources
- **New York**: New York Department of State resources
- **Florida**: Florida Department of State resources
- **General**: SBA and local authority resources

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

- **Delaware Business First Steps**: 1-800-292-7935
- **Local SBA Office**: Contact your local Small Business Administration
- **Documentation**: See `docs/` directory for detailed guides

# Delaware Business License MCP Tools with RAG

This project provides MCP (Model Context Protocol) tools to access Delaware business license information with **RAG (Retrieval-Augmented Generation)** capabilities, using vector embeddings and semantic search with **Qdrant** vector database for enhanced retrieval.

## 🚀 **RAG Features**

### **What is RAG?**
RAG (Retrieval-Augmented Generation) combines:
- **Vector embeddings** for semantic understanding
- **Vector database** for efficient storage and retrieval
- **Semantic search** for finding relevant information
- **Similarity matching** for discovering related licenses

### **RAG Components:**
- **Embedding Model**: `all-MiniLM-L6-v2` (384-dimensional embeddings)
- **Vector Database**: **Qdrant** with persistent storage
- **Semantic Search**: Cosine similarity for relevance ranking
- **Fallback System**: Web scraping when RAG is unavailable

## 🛠️ **Available RAG-Powered Tools**

### 1. `search_delaware_licenses_rag`
- **Description**: Search for licenses using semantic search (RAG-powered with Qdrant)
- **Parameters**: 
  - `query` (required): Search query (e.g., 'restaurant', 'bakery', 'consulting')
  - `top_k` (optional): Number of top results to return (default: 5)
- **RAG Features**: Semantic understanding, relevance ranking, context-aware results

### 2. `get_similar_licenses`
- **Description**: Find similar licenses based on a license type (RAG-powered with Qdrant)
- **Parameters**:
  - `license_type` (required): License type to find similar ones for
  - `top_k` (optional): Number of similar results to return (default: 3)
- **RAG Features**: Similarity matching, related license discovery

### 3. `get_delaware_license_categories`
- **Description**: Get all available license categories from Delaware Business First Steps
- **Parameters**: None
- **Features**: Web scraping with RAG-enhanced categorization

### 4. `get_delaware_license_details`
- **Description**: Get detailed information about a specific license type from Delaware
- **Parameters**: 
  - `category` (required): License category (e.g., 'Food', 'Health', 'Professions')
  - `license_type` (optional): Specific license type within the category
- **Features**: Detailed extraction with RAG context

### 5. `get_delaware_business_steps`
- **Description**: Get the 4-step process for opening a business in Delaware
- **Parameters**: None
- **Features**: Structured business guidance

## 🚀 **Quick Start**

### **Prerequisites**
```bash
pip install -r requirements.txt
```

### **Setup Qdrant**
```bash
# Run the setup script
python setup_qdrant.py

# Or manually install Qdrant with Docker
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 -v qdrant_storage:/qdrant/storage qdrant/qdrant:latest
```

### **Test RAG Tools**
```bash
python test_delaware_rag.py
```

### **Use with MCP Client**
1. Add the Delaware RAG MCP server to your MCP configuration:
```json
{
  "mcpServers": {
    "delaware_licenses_rag": {
      "command": "python",
      "args": ["delaware_rag_server.py"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

## 🎯 **RAG vs Traditional Search**

### **Traditional Search (Web Scraping):**
- ❌ Keyword matching only
- ❌ No semantic understanding
- ❌ Limited to exact text matches
- ❌ No similarity discovery

### **RAG-Powered Search:**
- ✅ **Semantic understanding** of queries
- ✅ **Context-aware** results
- ✅ **Similarity matching** for related licenses
- ✅ **Relevance ranking** based on meaning
- ✅ **Fallback system** when RAG unavailable

## 📊 **RAG Performance Examples**

### **Semantic Search Examples:**

**Query**: "restaurant"
- **RAG Results**: Food Establishments, Food Trucks, Caterers, Bakeries
- **Traditional**: Only exact "restaurant" matches

**Query**: "healthcare"
- **RAG Results**: Medical Professionals, Healthcare Facilities, Nursing Homes
- **Traditional**: Only exact "healthcare" matches

**Query**: "consulting"
- **RAG Results**: Professional Services, Business Consultants, Management Services
- **Traditional**: Only exact "consulting" matches

### **Similarity Search Examples:**

**Input**: "Food Establishments"
- **Similar Licenses**: Food Trucks, Caterers, Bakeries, Frozen Dessert Stands
- **Reasoning**: All food service related businesses

**Input**: "Medical Professionals"
- **Similar Licenses**: Healthcare Facilities, Nursing Homes, Medical Transport
- **Reasoning**: All healthcare related services

## 🔧 **RAG Architecture with Qdrant**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Query    │───▶│  Embedding      │───▶│  Qdrant         │
│   "restaurant"  │    │  Model          │    │  Vector DB      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Semantic       │    │  Similarity     │
                       │  Search         │    │  Matching       │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Relevant       │    │  Related        │
                       │  Results        │    │  Licenses       │
                       └─────────────────┘    └─────────────────┘
```

## 📋 **License Categories with RAG**

The RAG system can understand and categorize licenses across all Delaware categories:

- **Agriculture** - Beekeepers, Commercial Feeds, Fertilizers, etc.
- **Alcohol** - Liquor Licenses
- **Automobile** - Auto Body Shops, Motor Vehicle Dealers, etc.
- **Banking** - Check Cashers, Licensed Lenders, etc.
- **Food** - Restaurants, Food Trucks, Bakeries, Caterers, etc.
- **Health** - Medical Professionals, Healthcare Facilities, etc.
- **Professions** - Accountants, Attorneys, Engineers, etc.
- **General Business License** - General Business Licenses
- And 15+ more categories...

## 🧪 **Testing RAG Capabilities**

### **Run the Test Suite:**
```bash
python test_delaware_rag.py
```

This will test:
1. ✅ License category retrieval
2. ✅ RAG-powered semantic search
3. ✅ Similarity matching
4. ✅ Business steps guidance
5. ✅ Detailed license information

### **RAG Status Check:**
The test will show:
- 🎯 **RAG System Status: ✅ Active** (if RAG is working)
- ⚠️ **RAG System Status: Fallback Mode** (if using web scraping)

## 📞 **Example Usage**

### **Semantic Search:**
```python
# Search for food-related businesses
result = await server._search_licenses_rag({
    "query": "restaurant", 
    "top_k": 5
})
```

### **Similarity Search:**
```python
# Find similar licenses
result = await server._get_similar_licenses({
    "license_type": "Food Establishments",
    "top_k": 3
})
```

### **Category Search:**
```python
# Get all categories
result = await server._get_license_categories()
```

## 🔗 **Data Source**

All information is sourced from the official [Delaware Business First Steps](https://firststeps.delaware.gov/topics/) website, with RAG enhancement for:

- **Semantic understanding** of business types
- **Context-aware** license recommendations
- **Similarity matching** for related services
- **Enhanced search** capabilities

## 📝 **Technical Details**

### **Embedding Model:**
- **Model**: `all-MiniLM-L6-v2`
- **Dimensions**: 384
- **Performance**: Fast inference, good semantic understanding

### **Vector Database (Qdrant):**
- **Database**: Qdrant
- **Host**: localhost:6333
- **Collection**: delaware_licenses
- **Distance**: Cosine similarity
- **Storage**: Persistent with Docker volumes

### **Qdrant Configuration:**
```python
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "delaware_licenses"
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 embedding size
```

### **Fallback System:**
- **Primary**: RAG-powered semantic search with Qdrant
- **Fallback**: Web scraping when Qdrant unavailable
- **Error Handling**: Graceful degradation

## 🐳 **Qdrant Setup**

### **Automatic Setup:**
```bash
python setup_qdrant.py
```

### **Manual Setup:**
```bash
# Install Qdrant with Docker
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 -v qdrant_storage:/qdrant/storage qdrant/qdrant:latest

# Access Qdrant dashboard
# http://localhost:6333/dashboard
```

### **Qdrant Management:**
```bash
# Start Qdrant
docker start qdrant

# Stop Qdrant
docker stop qdrant

# View logs
docker logs qdrant

# Remove Qdrant
docker rm -f qdrant
```

## 🤝 **Contributing**

To enhance the RAG system:

1. **Add new embedding models** in `_initialize_rag()`
2. **Improve Qdrant configuration** for better performance
3. **Add more license sources** to the vector database
4. **Enhance similarity algorithms** for better matching
5. **Add caching** for improved performance

## 🎯 **Benefits of RAG with Qdrant**

1. **Better Search**: Semantic understanding vs keyword matching
2. **Related Discovery**: Find similar licenses automatically
3. **Context Awareness**: Understand business context
4. **Scalability**: Qdrant vector database for efficient retrieval
5. **Reliability**: Fallback system ensures availability
6. **Performance**: Qdrant provides fast vector similarity search
7. **Persistence**: Data persists across restarts

## 🚀 **Why Qdrant?**

- **High Performance**: Optimized for vector similarity search
- **Scalability**: Handles large-scale vector operations
- **Persistence**: Data survives container restarts
- **Web UI**: Built-in dashboard for monitoring
- **Production Ready**: Used in production environments
- **Docker Support**: Easy deployment with containers

The RAG-enhanced Delaware MCP tools with Qdrant provide a sophisticated, AI-powered approach to business license information retrieval! 🎉 
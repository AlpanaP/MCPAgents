# streamlit_app.py - Main app for Streamlit Cloud deployment
import streamlit as st
import os
import sys

# Add the BusinessLicenseNavigator directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'BusinessLicenseNavigator'))

try:
    from BusinessLicenseNavigator.agent import run_agent, DELAWARE_RAG_AVAILABLE
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Please ensure all dependencies are installed")
    
    def run_agent(user_input):
        return "Error: Dependencies not available. Please check the requirements.txt file."
    
    DELAWARE_RAG_AVAILABLE = False

st.set_page_config(
    page_title="Business License Navigator",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 Business License Navigator")

st.markdown("""
This app helps you navigate business license requirements using AI-powered guidance. 
Enter a brief description of your business and where it's located.
""")

# Add info about AI options
with st.expander("ℹ️ About this app"):
    st.markdown("""
    **AI Options:**
    
    **1. Gemini AI (Recommended for Cloud):**
    - Set your Gemini API key below
    - Works in cloud deployment
    - Powered by Google's Gemini 1.5 Flash
    
    **2. Local Ollama:**
    - Install Ollama: `brew install ollama` (macOS) or `curl -fsSL https://ollama.ai/install.sh | sh` (Linux)
    - Pull model: `ollama pull llama3.1:8b`
    - Start server: `ollama serve`
    - Works locally only
    
    **3. Delaware RAG Integration:**
    - **NEW**: Delaware-specific license information using RAG
    - Vector database with Qdrant for semantic search
    - Official Delaware Business First Steps data
    - Available for Delaware-related queries
    
    **4. Fallback Mode:**
    - No AI required
    - Provides general guidance based on business type
    - Always verify with local authorities
    """)

# Delaware RAG Status
with st.expander("🏛️ Delaware RAG Status"):
    if DELAWARE_RAG_AVAILABLE:
        st.success("✅ Delaware RAG Integration Active")
        st.markdown("""
        **Delaware RAG Features:**
        - 🎯 **Semantic Search**: Find relevant licenses using AI
        - 🔍 **Similarity Matching**: Discover related license types
        - 📋 **Business Steps**: Official Delaware 4-step process
        - 🏢 **License Categories**: All Delaware license categories
        - 📊 **Relevance Scoring**: AI-powered result ranking
        
        **How to use:**
        - Include "Delaware" or "DE" in your query
        - Or just describe your business - RAG will enhance results
        - Get official Delaware Business First Steps information
        """)
    else:
        st.warning("⚠️ Delaware RAG Integration Not Available")
        st.markdown("""
        **To enable Delaware RAG:**
        1. Install dependencies: `pip install -r requirements.txt`
        2. Setup Qdrant: `python setup_qdrant.py`
        3. Test RAG tools: `python test_delaware_rag.py`
        
        **Benefits of Delaware RAG:**
        - Official Delaware government data
        - Semantic understanding of business types
        - Similarity matching for related licenses
        - Relevance scoring for better results
        """)

# Gemini API Key configuration
with st.expander("🔑 Gemini API Key Setup"):
    st.markdown("""
    **To use Gemini AI:**
    1. Get a free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
    2. Set it as an environment variable: `export GEMINI_API_KEY=your_key_here`
    3. Or enter it below (for testing only)
    """)
    
    # Option to enter API key manually (for testing)
    manual_key = st.text_input("Gemini API Key (optional, for testing)", type="password")
    if manual_key:
        os.environ['GEMINI_API_KEY'] = manual_key
        st.success("✅ API key set for this session")

# Check AI availability
gemini_available = os.getenv('GEMINI_API_KEY') is not None
st.sidebar.markdown("### 🤖 AI Status")
if gemini_available:
    st.sidebar.success("✅ Gemini AI Available")
else:
    st.sidebar.warning("⚠️ Gemini API key not set")

if DELAWARE_RAG_AVAILABLE:
    st.sidebar.success("✅ Delaware RAG Available")
else:
    st.sidebar.warning("⚠️ Delaware RAG not available")

user_input = st.text_area(
    "Business Description", 
    placeholder="e.g., I run a home bakery in Delaware",
    height=100
)

if st.button("🚀 Find My License Path", type="primary"):
    if user_input.strip():
        with st.spinner("🤖 Consulting AI agent..."):
            try:
                response = run_agent(user_input)
                
                # Check what type of response we got
                if response.startswith("ERROR:"):
                    st.warning("⚠️ AI not available - using general guidance")
                    st.info("💡 Set up Gemini API key or Ollama for AI-powered guidance")
                    st.markdown("### 📋 General License Guidance:")
                else:
                    st.success("✅ AI-powered guidance ready!")
                    st.markdown("### 🤖 AI License Guidance:")
                
                st.write(response)
                
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
                st.info("💡 Check your API key or try the fallback mode")
    else:
        st.warning("Please enter a business description")

st.markdown("---")
st.markdown("""
### ℹ️ How to use:
1. Describe your business type and location
2. Click "Find My License Path"
3. Get personalized guidance on licenses and permits

### 🔧 Setup Options:

**Option 1: Gemini AI (Cloud-friendly)**
```bash
# Get API key from https://makersuite.google.com/app/apikey
export GEMINI_API_KEY=your_key_here
streamlit run streamlit_app.py
```

**Option 2: Local Ollama**
```bash
# Install Ollama
brew install ollama  # macOS
# OR
curl -fsSL https://ollama.ai/install.sh | sh  # Linux

# Pull the model
ollama pull llama3.1:8b

# Start the server
ollama serve

# Run this app locally
streamlit run streamlit_app.py
```

**Option 3: Delaware RAG Integration**
```bash
# Install dependencies
pip install -r requirements.txt

# Setup Qdrant vector database
python setup_qdrant.py

# Test Delaware RAG tools
python test_delaware_rag.py

# Run the app
streamlit run streamlit_app.py
```

### 📞 Need Help?
- Contact your local Small Business Administration (SBA)
- Check with your city/county clerk's office
- Consult with a business attorney
- Verify requirements with your state's business licensing office
""") 
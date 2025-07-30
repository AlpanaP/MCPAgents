# streamlit_app.py
import streamlit as st
from agent import run_agent

st.set_page_config(
    page_title="Business License Navigator",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 Business License Navigator")

st.markdown("""
This app helps you navigate business license requirements. 
Enter a brief description of your business and where it's located.
""")

# Add info about Ollama status
with st.expander("ℹ️ About this app"):
    st.markdown("""
    **Local Mode (Recommended):**
    - Install Ollama: `brew install ollama` (macOS) or `curl -fsSL https://ollama.ai/install.sh | sh` (Linux)
    - Pull model: `ollama pull llama3.1:8b`
    - Start server: `ollama serve`
    - Get AI-powered personalized guidance
    
    **Cloud Mode:**
    - Works without Ollama
    - Provides general guidance based on business type
    - Always verify with local authorities
    """)

user_input = st.text_area(
    "Business Description", 
    placeholder="e.g., I run a home bakery in Austin, TX",
    height=100
)

if st.button("🚀 Find My License Path", type="primary"):
    if user_input.strip():
        with st.spinner("🤖 Consulting agent..."):
            try:
                response = run_agent(user_input)
                
                # Check if it's an error response
                if response.startswith("ERROR:"):
                    st.warning("⚠️ Ollama not available - using general guidance")
                    st.info("💡 For AI-powered guidance, run Ollama locally")
                    st.markdown("### 📋 General License Guidance:")
                else:
                    st.success("✅ AI-powered guidance ready!")
                    st.markdown("### 🤖 AI License Guidance:")
                
                st.write(response)
                
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
                st.info("💡 Try running the app locally with Ollama for best results")
    else:
        st.warning("Please enter a business description")

st.markdown("---")
st.markdown("""
### ℹ️ How to use:
1. Describe your business type and location
2. Click "Find My License Path"
3. Get personalized guidance on licenses and permits

### 🔧 Local Setup (for AI features):
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

### 📞 Need Help?
- Contact your local Small Business Administration (SBA)
- Check with your city/county clerk's office
- Consult with a business attorney
- Verify requirements with your state's business licensing office
""") 
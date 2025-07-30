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
                st.success("✅ Done!")
                st.markdown("### 📋 License Guidance:")
                st.write(response)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Note: This app requires Ollama to be running locally with the llama3.1:8b model")
    else:
        st.warning("Please enter a business description")

st.markdown("---")
st.markdown("""
### ℹ️ How to use:
1. Describe your business type and location
2. Click "Find My License Path"
3. Get personalized guidance on licenses and permits

### 🔧 Requirements:
- Ollama server running locally
- llama3.1:8b model installed (`ollama pull llama3.1:8b`)
""") 
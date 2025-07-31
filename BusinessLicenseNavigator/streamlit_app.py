#!/usr/bin/env python3
"""
Streamlit Web Interface for Business License Navigator

A modern web interface for testing the AI-powered business license guidance system.
"""

import streamlit as st
import asyncio
import sys
from pathlib import Path
import json
from datetime import datetime

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.chat_interface import BusinessLicenseChat
from src.core.intelligent_semantic_search import intelligent_semantic_search


def init_session_state():
    """Initialize session state variables."""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'chat_interface' not in st.session_state:
        st.session_state.chat_interface = None


def setup_page():
    """Setup the Streamlit page configuration."""
    st.set_page_config(
        page_title="Business License Navigator",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🏢 Business License Navigator")
    st.markdown("AI-powered business license guidance system with MCP integration")
    st.markdown("---")


def create_sidebar():
    """Create the sidebar with configuration options."""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key Configuration
        st.subheader("🔑 API Keys")
        
        # Load API key from environment
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        if gemini_api_key:
            st.success("✅ GEMINI_API_KEY loaded from .env file")
            # Set the API key in environment for the app to use
            os.environ["GEMINI_API_KEY"] = gemini_api_key
        else:
            st.warning("⚠️ GEMINI_API_KEY not found in .env file")
        
        # Show API key status (masked)
        if gemini_api_key:
            masked_key = gemini_api_key[:8] + "..." + gemini_api_key[-4:] if len(gemini_api_key) > 12 else "***"
            st.info(f"API Key: {masked_key}")
        else:
            st.error("No API key available")
        
        # Test Queries
        st.subheader("🧪 Test Queries")
        test_queries = [
            "I want to open an ice cream franchise in FL for Rita's",
            "What licenses do I need for a financial services firm in Delaware?",
            "How do I start a restaurant in California?",
            "What are the requirements for a construction company in Texas?"
        ]
        
        selected_query = st.selectbox(
            "Choose a test query:",
            test_queries,
            index=0
        )
        
        if st.button("🚀 Use Test Query"):
            st.session_state.user_input = selected_query
        
        # System Information
        st.subheader("ℹ️ System Info")
        st.info("""
        **Features:**
        - Intelligent semantic search
        - MCP server integration
        - Real-time license information
        - Cost estimation
        - Timeline analysis
        """)
        
        # Clear History
        if st.button("🗑️ Clear History"):
            st.session_state.chat_history = []
            st.success("History cleared!")


def display_chat_interface():
    """Display the main chat interface."""
    st.header("💬 Chat Interface")
    
    # Initialize chat interface if not exists
    if st.session_state.chat_interface is None:
        try:
            st.session_state.chat_interface = BusinessLicenseChat()
            st.success("✅ Chat interface initialized")
        except Exception as e:
            st.error(f"❌ Error initializing chat interface: {e}")
            return
    
    # Chat input
    user_input = st.text_input(
        "Ask about business licenses:",
        key="user_input",
        placeholder="e.g., I want to open an ice cream franchise in FL for Rita's"
    )
    
    # Process button
    col1, col2 = st.columns([1, 4])
    with col1:
        process_button = st.button("🚀 Process Query", type="primary")
    
    with col2:
        if st.button("🧪 Test Analysis"):
            if user_input:
                test_analysis(user_input)
    
    # Process the query
    if process_button and user_input:
        process_query(user_input)


def test_analysis(query: str):
    """Test the intelligent semantic search analysis."""
    st.subheader("🔍 Intelligent Analysis Test")
    
    try:
        # Run analysis
        with st.spinner("Analyzing query..."):
            analysis = asyncio.run(intelligent_semantic_search.analyze_business_query(query))
        
        # Display results
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Business Type", analysis.get('business_type', 'Unknown'))
            st.metric("Detected Licenses", len(analysis.get('detected_licenses', [])))
            st.metric("Timeline", analysis.get('timeline', 'Unknown'))
        
        with col2:
            costs = analysis.get('estimated_costs', {})
            st.metric("Total Cost", costs.get('total_initial', 'Unknown'))
            st.metric("Application Fee", costs.get('application_fee', 'Unknown'))
            st.metric("License Fee", costs.get('license_fee', 'Unknown'))
        
        # Detailed information
        with st.expander("📋 Detailed Analysis"):
            st.json(analysis)
            
    except Exception as e:
        st.error(f"❌ Analysis error: {e}")


def process_query(query: str):
    """Process a user query and display the response."""
    st.subheader("🤖 AI Response")
    
    try:
        # Process query
        with st.spinner("Processing query..."):
            response = asyncio.run(st.session_state.chat_interface.process_query(query))
        
        # Add to history
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.chat_history.append({
            "timestamp": timestamp,
            "query": query,
            "response": response
        })
        
        # Display response
        st.markdown("### Response:")
        st.markdown(response)
        
        # Show response analysis
        with st.expander("📊 Response Analysis"):
            analysis = {
                "Contains License Info": "license" in response.lower(),
                "Contains Source Info": "source" in response.lower() or "http" in response.lower(),
                "Contains Cost Info": "cost" in response.lower() or "$" in response,
                "Contains Next Steps": "next" in response.lower() or "step" in response.lower(),
                "Response Length": len(response),
                "Word Count": len(response.split())
            }
            
            for key, value in analysis.items():
                if isinstance(value, bool):
                    if value:
                        st.success(f"✅ {key}")
                    else:
                        st.warning(f"⚠️ {key}")
                else:
                    st.info(f"📊 {key}: {value}")
                    
    except Exception as e:
        st.error(f"❌ Processing error: {e}")


def display_chat_history():
    """Display the chat history."""
    if st.session_state.chat_history:
        st.subheader("📜 Chat History")
        
        for i, entry in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"💬 {entry['timestamp']} - {entry['query'][:50]}..."):
                st.markdown(f"**Query:** {entry['query']}")
                st.markdown(f"**Response:** {entry['response']}")


def display_system_status():
    """Display system status and configuration."""
    st.subheader("🔧 System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Chat History", len(st.session_state.chat_history))
        
        # Check API key status
        import os
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            st.success("✅ GEMINI_API_KEY Available")
        else:
            st.warning("⚠️ GEMINI_API_KEY Missing")
    
    with col2:
        # Test MCP availability
        try:
            from mcp_use import MCPAgent, MCPClient
            st.success("✅ MCP Components Available")
        except ImportError:
            st.info("ℹ️ MCP Components Not Installed")
            st.info("Install with: pip install mcp-use")
    
    with col3:
        # Test intelligent semantic search
        try:
            from src.core.intelligent_semantic_search import intelligent_semantic_search
            st.success("✅ Intelligent Semantic Search Available")
        except Exception as e:
            st.error(f"❌ Intelligent Semantic Search Error: {str(e)[:50]}...")
    
    # Additional status information
    with st.expander("📊 Detailed System Info"):
        st.info("""
        **System Components:**
        - ✅ Streamlit Web Interface
        - ✅ Intelligent Semantic Search
        - ✅ Business License Analysis
        - ✅ Cost Estimation
        - ✅ Timeline Analysis
        - ⚠️ MCP Integration (Optional)
        - ⚠️ Real-time Data Fetching (Optional)
        
        **Features Working:**
        - Query processing and analysis
        - Business type detection
        - License requirement identification
        - Cost and timeline estimation
        - Source information display
        """)


def main():
    """Main Streamlit application."""
    # Load environment variables at startup
    import os
    from dotenv import load_dotenv
    
    # Load .env file
    load_dotenv()
    
    # Set up the page
    setup_page()
    init_session_state()
    
    # Create sidebar
    create_sidebar()
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📜 History", "🔧 Status"])
    
    with tab1:
        display_chat_interface()
    
    with tab2:
        display_chat_history()
    
    with tab3:
        display_system_status()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🚀 Business License Navigator - AI-Powered License Guidance System</p>
        <p>Built with Streamlit, MCP, and Intelligent Semantic Search</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main() 
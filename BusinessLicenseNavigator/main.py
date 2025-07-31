#!/usr/bin/env python3
"""
BusinessLicenseNavigator - Main Entry Point
==========================================

AI-powered business license guidance system with MCP integration.
"""

import asyncio
import sys
from src.chat_interface import BusinessLicenseChat

async def main():
    """Main entry point for the BusinessLicenseNavigator application."""
    print("🚀 BusinessLicenseNavigator - AI-Powered License Guidance System")
    print("=" * 60)
    print("Starting chat interface...")
    print("Type 'exit' to quit, 'help' for commands")
    print("-" * 60)
    
    try:
        chat = BusinessLicenseChat()
        await chat.run_chat()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)


def run_streamlit():
    """Run the Streamlit web interface."""
    import subprocess
    import sys
    
    try:
        # Check if streamlit is available
        subprocess.run([sys.executable, "-m", "streamlit", "--version"], 
                      check=True, capture_output=True)
        
        # Run streamlit app
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])
    except subprocess.CalledProcessError:
        print("❌ Streamlit not available. Install with: pip install streamlit")
    except FileNotFoundError:
        print("❌ Streamlit app not found")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        run_streamlit()
    else:
        asyncio.run(main()) 